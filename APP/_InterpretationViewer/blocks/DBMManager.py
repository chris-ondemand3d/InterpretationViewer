import os, sys

import copy
import collections

import numpy as np
import vtk
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QObject, QUrl, QTimer, Qt, pyqtSignal, pyqtSlot, QThread
from PyQt5.QtQml import QQmlProperty

import gc

from COMMON import WorkerThread, WorkerThread

import multiprocessing
from multiprocessing.managers import BaseManager

from .DBMModel import StudyModel
from . import DicomWeb as dw


class DBMManager(QObject):

    def __init__(self, _win=None, _dicom_web=None, *args, **kdws):
        super().__init__()

        self.reset()
        self.initialize()

        self._win = _win

    def initialize(self):
        self.study_model = StudyModel()
        self.DICOM_WEB = collections.OrderedDict()

    def reset(self):
        pass

    def get_study_model(self):
        return self.study_model

    def query_studies_series(self):
        dicom_web = dw.cyDicomWeb()
        studies = dicom_web.query_studies()
        if not studies:
            return None

        def _get(_x, _tag):
            _p = _x.get(_tag)
            if _p:
                if len(_p['Value']) == 0:
                    return None
                if _p['vr'] is 'PN':
                    _p = _p['Value'][0]['Alphabetic']
                else:
                    _p = _p['Value'][0]
            return _p

        _items = dict()
        _items['Study'] = dict()
        _studies = _items['Study']
        for _i, _x in enumerate(studies):
            # study
            _study = dict()
            _study['StudyInstanceUID'] = _get(_x, dw.TAG_StudyInstanceUID)
            _study['Study_Key'] = _get(_x, dw.TAG_StudyID)
            _study['PatientID'] = _get(_x, dw.TAG_PatientID)
            _study['PatientName'] = _get(_x, dw.TAG_PatientName)
            _study['PatientSex'] = _get(_x, dw.TAG_PatientSex)
            _study['PatientAge'] = _get(_x, dw.TAG_PatientAge)
            _study['BodyPartExamined'] = _get(_x, dw.TAG_BodyPartExamined)
            _study['StudyDateTime'] = _get(_x, dw.TAG_StudyDate)
            _study['StudyDescription'] = _get(_x, dw.TAG_StudyDescription)
            _study['Comments'] = ''
            _studies[_i] = _study
            # series
            _study['Series'] = dict()
            series = dicom_web.query_series(_study['StudyInstanceUID'])
            if not series:
                continue
            for _j, _y in enumerate(series):
                _series = dict()
                _series['SeriesInstanceUID'] = _get(_y, dw.TAG_SeriesInstanceUID)
                _series['Series_Key'] = "1004" # TODO
                _series['SeriesNumber'] = _get(_y, dw.TAG_SeriesNumber)
                _series['SeriesDateTime'] = _get(_y, dw.TAG_SeriesDate)
                _series['SeriesDescription'] = _get(_y, dw.TAG_SeriesDescription)
                _series['NumberOfImages'] = _get(_y, dw.TAG_NumberofSeriesRelatedInstances)
                _series['Modality'] = _get(_y, dw.TAG_Modality)
                _series['BodyPartExamined'] = _get(_y, dw.TAG_BodyPartExamined)
                _series['Comments'] = ""
                _study['Series'][_j] = _series
        return _items

    def retrieve_dicom(self, study_uid, series_uid):

        if not study_uid in self.DICOM_WEB:
            dicom_web = self.DICOM_WEB[study_uid] = dw.cyDicomWeb()
        else:
            dicom_web = self.DICOM_WEB[study_uid]

        # if hasattr(self, 'vtk_img_narray'):
        #     del self.vtk_img_narray
        #
        # if hasattr(self, 'vtk_img'):
        #     self.vtk_img.ReleaseData()
        #     del self.vtk_img
        #     gc.collect()


        dicom_web.query_metadata(study_uid, series_uid)
        dim = dicom_web.get_dimensions()
        o = dicom_web.get_origin()
        s = [*dicom_web.get_spacing(), dicom_web.get_thickness()]
        wwl = dicom_web.get_wwl()
        vtk_img = vtk.vtkImageData()
        vtk_img.SetDimensions(dim)
        vtk_img.SetOrigin(o)
        vtk_img.SetSpacing(s)
        # # vtk_img.SetExtent(e)
        vtk_img.AllocateScalars(vtk.VTK_CHAR, 1)
        buf = np.zeros(np.product(dim))
        buf.fill(-1000)
        vtk_img.GetPointData().SetScalars(dsa.numpyTovtkDataArray(buf))
        vtk_img_narray = buf.reshape(dim, order='F')

        url = "%s/%s/studies/%s/series/%s/" % (dicom_web.host_url, dicom_web.wadors_prefix,
                                               dicom_web.study_uid, dicom_web.series_uid)
        header = dw.HEADERS2
        rescale_params = dicom_web.rescale_slope, dicom_web.rescale_intercept

        # Thread function
        def _do(_dicom_web):
            instance_uids = _dicom_web.get_instance_uids()
            if instance_uids is None:
                print("****** Make sure dicom web!!!!!!!!! ******")
                return

            uids = instance_uids

            def _update(_frame_info):
                for _frame, _idx in _frame_info:
                    _shape_of_dest = vtk_img_narray.shape
                    _w = _dicom_web.metadata[_idx][dw.TAG_Columns]['Value'][0]
                    _h = _dicom_web.metadata[_idx][dw.TAG_Rows]['Value'][0]

                    if _shape_of_dest[0] - _w == 0:
                        x_b, x_e = 0, _shape_of_dest[0]
                    else:
                        _dif_x = (_shape_of_dest[0] - _w) // 2
                        x_b, x_e = _dif_x, -_dif_x

                    if _shape_of_dest[1] - _h == 0:
                        y_b, y_e = 0, _shape_of_dest[1]
                    else:
                        _dif_y = (_shape_of_dest[1] - _h) // 2
                        y_b, y_e = _dif_y, -_dif_y

                    vtk_img_narray[x_b:x_e, y_b:y_e, _idx] = _frame.reshape((_w, _h), order='F')[:, :]

                vtk_img.Modified()
                self._win.send_message.emit(['slice::refresh_all', None])

            def _update_thumbnail_scout_img(_frame_info):
                for _frame, _idx in _frame_info:
                    _w = _dicom_web.scout_img_data[dw.TAG_Columns]['Value'][0]
                    _h = _dicom_web.scout_img_data[dw.TAG_Rows]['Value'][0]
                    _scout_img = _frame.reshape((_h, _w, 3), order='C').astype(_frame.dtype).ravel()
                    _vtk_scout_dims = dsa.numpyTovtkDataArray(np.array([_w, _h, 3]))
                    _vtk_scout_dims.SetName('SCOUT_IMG_DIMS')
                    vtk_img.GetFieldData().AddArray(_vtk_scout_dims)
                    _vtk_scout_array = dsa.numpyTovtkDataArray(_scout_img)
                    _vtk_scout_array.SetName('SCOUT_IMG')
                    vtk_img.GetFieldData().AddArray(_vtk_scout_array)
                    self._win.send_message.emit(['slice::update_thumbnail_img', None])

            def _update_thumbnail_center_img(_frame_info):
                for _frame, _idx in _frame_info:
                    _w = _dicom_web.metadata[_idx][dw.TAG_Columns]['Value'][0]
                    _h = _dicom_web.metadata[_idx][dw.TAG_Rows]['Value'][0]
                    _frame[:] = _frame[:] / (np.max(_frame)) * 255
                    _frame[_frame < 0] = 0
                    _frame[_frame > 255] = 255
                    _thumbnail_img = _frame.reshape((_h, _w), order='C').astype(np.uint8).ravel()
                    _vtk_thumbnail_dims = dsa.numpyTovtkDataArray(np.array([_w, _h]))
                    _vtk_thumbnail_dims.SetName('THUMBNAIL_IMG_DIMS')
                    vtk_img.GetFieldData().AddArray(_vtk_thumbnail_dims)
                    _vtk_thumbnail_array = dsa.numpyTovtkDataArray(_thumbnail_img)
                    _vtk_thumbnail_array.SetName('THUMBNAIL_IMG')
                    vtk_img.GetFieldData().AddArray(_vtk_thumbnail_array)
                    self._win.send_message.emit(['slice::update_thumbnail_img', None])

            processes_cnt = 4
            uid_infos = [[url + "instances/%s/frames/1" % uid, header, i, dicom_web.bits, rescale_params] for i, uid in enumerate(uids)]
            a = len(uid_infos) // processes_cnt
            b = len(uid_infos) % processes_cnt

            with multiprocessing.Pool(processes=processes_cnt) as pool:
                pool.daemon = True

                if _dicom_web.scout_img_data:
                    # scout image
                    _scout_uid = _dicom_web.scout_img_data[dw.TAG_SOPInstanceUID]['Value'][0]
                    _scout_bits = _dicom_web.scout_img_data[dw.TAG_BitsAllocated]['Value'][0]
                    _scout_param = [url + "instances/%s/frames/1" % _scout_uid, header, None, _scout_bits, None]
                    _scout_pool = pool.map_async(dw.requests_buf, [_scout_param, ], callback=_update_thumbnail_scout_img)
                    _scout_pool.wait()
                else:
                    # center img
                    _idx_cen = len(uids) // 2
                    _meta = _dicom_web.metadata[_idx_cen]
                    _thumbnail_uid = _meta[dw.TAG_SOPInstanceUID]['Value'][0]
                    _thumbnail_bits = _meta[dw.TAG_BitsAllocated]['Value'][0]
                    _thumbnail_param = [url + "instances/%s/frames/1" % _thumbnail_uid, header, _idx_cen, _thumbnail_bits, rescale_params]
                    _thumbnail_pool = pool.map_async(dw.requests_buf, [_thumbnail_param, ], callback=_update_thumbnail_center_img)
                    _thumbnail_pool.wait()

                for i in range(a):
                    _i = i * processes_cnt
                    _pool = pool.map_async(dw.requests_buf, uid_infos[_i:_i+processes_cnt], callback=_update)
                    _pool.wait()
                _i = a * processes_cnt
                _pool = pool.map_async(dw.requests_buf, uid_infos[_i:_i+b], callback=_update)
                _pool.wait()
                pool.close()
                pool.join()
                gc.collect()

        # finished fn
        def _on_finished(_worker):
            print("DICOM Files had been loaded!! :)")
            for _w in self.WORKERS:
                if _w[1].isRunning():
                    continue
                self.WORKERS.remove(_w)
                del _w

        # do
        if not hasattr(self, 'WORKERS'):
            self.WORKERS = []
        W0 = WorkerThread.create_worker(0)
        self.WORKERS.append(W0)
        # NOTE
        _dicom_web = copy.deepcopy(self.DICOM_WEB[study_uid])
        WorkerThread.start_worker(*W0, _do, _dicom_web,
                                   _finished_func=lambda: _on_finished(W0))
        return vtk_img, wwl
