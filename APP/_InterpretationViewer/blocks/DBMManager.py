import os, sys

import copy
import collections

from datetime import datetime

import numpy as np
import vtk
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QObject, QUrl, QTimer, Qt, pyqtSignal, pyqtSlot, QThread
from PyQt5.QtQml import QQmlProperty

import gc

from COMMON import WorkerThread, WorkerThread, get_vtkmat_from_list, get_matrix_from_vtkmat

import multiprocessing
from multiprocessing.managers import BaseManager

from .DBMModel import StudyModel
from . import DicomWeb as dw


class DBMManager(QObject):

    def __init__(self, _app=None, _dicom_web=None, *args, **kdws):
        super().__init__()

        self.reset()
        self.initialize()

        self._app = _app

    def initialize(self):
        self.study_model = StudyModel()
        self.related_study_model = StudyModel()
        self.DICOM_WEB = collections.OrderedDict()

    def reset(self):
        pass

    def get_study_model(self):
        return self.study_model

    def get_related_study_model(self):
        return self.related_study_model

    def clear_study_model(self):
        self.study_model.beginResetModel()
        self.study_model.clearData()
        self.study_model.endResetModel()

    def clear_related_study_model(self):
        self.related_study_model.beginResetModel()
        self.related_study_model.clearData()
        self.related_study_model.endResetModel()

    def refresh_study_model(self):
        _data = self.query_studies_series()
        if _data:
            self.study_model.beginResetModel()
            self.study_model.addData(_data)
            self.study_model.endResetModel()
            return True
        return False

    def refresh_related_study_model(self, patiend_id):
        # Thread function
        def _do(args):
            conditions = {"PatientID": patiend_id}
            _data = self.query_studies_series(conditions)
            if _data:
                self.related_study_model.beginResetModel()
                self.related_study_model.addData(_data)
                self.related_study_model.endResetModel()
                return True
            return False

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
        WorkerThread.start_worker(*W0, _do, None,
                                  _finished_func=lambda: _on_finished(W0))

    def query_studies_series(self, conditions=None):
        dicom_web = dw.cyDicomWeb()
        studies = dicom_web.query_studies(conditions)
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
            _study['AccessionNumber'] = _get(_x, dw.TAG_AccessionNumber)
            _study['BodyPartExamined'] = _get(_x, dw.TAG_BodyPartExamined)
            _date = _get(_x, dw.TAG_StudyDate)
            _time = _get(_x, dw.TAG_StudyTime)
            _datetime = "%s%s" % (_date if _date else "", _time if _time else "")
            try:
                _datetime = datetime.strptime(_datetime, "%Y%m%d%H%M%S").timetuple()
                _study['StudyDateTime'] = "%d-%d-%d %d:%d:%d"%(_datetime.tm_year, _datetime.tm_mon, _datetime.tm_mday,
                                                               _datetime.tm_hour, _datetime.tm_min, _datetime.tm_sec)
            except ValueError:
                _study['StudyDateTime'] = _datetime
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
                _date = _get(_y, dw.TAG_SeriesDate)
                _time = _get(_y, dw.TAG_SeriesTime)
                _datetime = "%s%s" % (_date if _date else "", _time if _time else "")
                try:
                    _datetime = datetime.strptime(_datetime, "%Y%m%d%H%M%S").timetuple()
                    _series['SeriesDateTime'] = "%d-%d-%d %d:%d:%d"%(_datetime.tm_year, _datetime.tm_mon, _datetime.tm_mday,
                                                                     _datetime.tm_hour, _datetime.tm_min, _datetime.tm_sec)
                except ValueError:
                    _series['SeriesDateTime'] = _datetime
                _series['SeriesDescription'] = _get(_y, dw.TAG_SeriesDescription)
                _series['NumberOfImages'] = _get(_y, dw.TAG_NumberofSeriesRelatedInstances)
                _series['Modality'] = _get(_y, dw.TAG_Modality)
                _series['BodyPartExamined'] = _get(_y, dw.TAG_BodyPartExamined)
                _series['Comments'] = ""
                _study['Series'][_j] = _series
        return _items

    def retrieve_dicom(self, study_uid, series_uid):

        # TODO
        dicom_web = dw.cyDicomWeb()
        if study_uid in self.DICOM_WEB:
            if series_uid in self.DICOM_WEB[study_uid]:
                # TODO
                return None
            else:
                self.DICOM_WEB[study_uid][series_uid] = dicom_web
        else:
            self.DICOM_WEB[study_uid] = {series_uid: dicom_web}

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

        # orientation
        patient_pos_ori = copy.deepcopy(dicom_web.patient_pos_ori)

        # busy flag
        _vtk_busy = dsa.numpyTovtkDataArray(np.array([]))
        _vtk_busy.SetName('BUSY')
        vtk_img.GetFieldData().AddArray(_vtk_busy)

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
                self._app.send_message.emit(['slice::refresh_all', None])

            def _update_thumbnail_scout_img(_frame_info):
                for _frame, _idx in _frame_info:
                    _w = _dicom_web.scout_img_data[dw.TAG_Columns]['Value'][0]
                    _h = _dicom_web.scout_img_data[dw.TAG_Rows]['Value'][0]
                    _scout_img = _frame.reshape((_h, _w, 3), order='C').astype(np.uint8).ravel()
                    _vtk_scout_dims = dsa.numpyTovtkDataArray(np.array([_w, _h, 3]))
                    _vtk_scout_dims.SetName('SCOUT_IMG_DIMS')
                    vtk_img.GetFieldData().AddArray(_vtk_scout_dims)
                    _vtk_scout_array = dsa.numpyTovtkDataArray(_scout_img)
                    _vtk_scout_array.SetName('SCOUT_IMG')
                    vtk_img.GetFieldData().AddArray(_vtk_scout_array)
                    self._app.send_message.emit(['slice::update_thumbnail_img', None])

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
                    self._app.send_message.emit(['slice::update_thumbnail_img', None])

            processes_cnt = 4
            uid_infos = [[url + "instances/%s/frames/1" % uid, header, i, dicom_web.bits, rescale_params] for i, uid in enumerate(uids)]
            total_cnt = len(uid_infos)
            a = total_cnt // processes_cnt
            b = total_cnt % processes_cnt

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
                    print("*** Downloading.....................!!! [%d/%d]***"%(_i+processes_cnt, total_cnt))
                    if _dicom_web.stop:
                        pool.close()
                        pool.join()
                        gc.collect()
                        print("*** Forced Termination!!! ***")
                        return
                _i = a * processes_cnt
                _pool = pool.map_async(dw.requests_buf, uid_infos[_i:_i+b], callback=_update)
                _pool.wait()
                print("*** Downloading.....................!!! [%d/%d]***" % (_i+b, total_cnt))
                pool.close()
                pool.join()
                gc.collect()

        # finished fn
        def _on_finished(_worker, _study_uid, _series_uid):
            print("DICOM Files had been loaded!! :)")
            for _w in self.WORKERS:
                if _w[1].isRunning():
                    continue
                self.WORKERS.remove(_w)
                _w[1].quit()
                del _w
            vtk_img.GetFieldData().RemoveArray('BUSY')
            self._app.send_message.emit(["slice::busy_check", None])
            # delete dicom_web
            _w = self.DICOM_WEB[_study_uid].pop(_series_uid)
            _w.reset()
            del _w
            if len(self.DICOM_WEB[_study_uid]) == 0:
                self.DICOM_WEB.pop(_study_uid)

        # do
        if not hasattr(self, 'WORKERS'):
            self.WORKERS = []
        W0 = WorkerThread.create_worker(0)
        self.WORKERS.append(W0)
        WorkerThread.start_worker(*W0, _do, dicom_web,
                                   _finished_func=lambda: _on_finished(W0, study_uid, series_uid))
        return vtk_img, patient_pos_ori, wwl

    def release_dicom_web(self, study_uid, series_uid):
        if study_uid in self.DICOM_WEB and series_uid in self.DICOM_WEB[study_uid]:
            self.DICOM_WEB[study_uid][series_uid].stop = True
