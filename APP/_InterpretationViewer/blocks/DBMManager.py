import os, sys

import numpy as np
import vtk
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QObject, QUrl, QTimer, Qt, pyqtSignal, pyqtSlot, QThread
from PyQt5.QtQml import QQmlProperty

import gc

from COMMON import WorkerThread

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
        self.dicom_web = _dicom_web

    def initialize(self):
        self.study_model = StudyModel()

    def reset(self):
        pass

    def get_study_model(self):
        return self.study_model

    def query_studies_series(self):
        if self.dicom_web:
            studies = self.dicom_web.query_studies()
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
                series = self.dicom_web.query_series(_study['StudyInstanceUID'])
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
        return None

    def retrieve_dicom(self, study_uid, series_uid):
        print("study uid :: ", study_uid)
        print("series uid :: ", series_uid)

        if hasattr(self, 'vtk_img'):
            self.vtk_img.ReleaseData()
            del self.vtk_img
            gc.collect()

        self.dicom_web.query_metadata(study_uid, series_uid)
        dim = self.dicom_web.get_dimensions()
        o = self.dicom_web.get_origin()
        s = [*self.dicom_web.get_spacing(), self.dicom_web.get_thickness()]
        self.vtk_img = vtk_img = vtk.vtkImageData()
        vtk_img.SetDimensions(dim)
        vtk_img.SetOrigin(o)
        vtk_img.SetSpacing(s)
        # # vtk_img.SetExtent(e)
        vtk_img.AllocateScalars(vtk.VTK_CHAR, 1)
        buf = np.zeros(np.product(dim))
        buf.fill(-1000)
        vtk_img.GetPointData().SetScalars(dsa.numpyTovtkDataArray(buf))
        self.vtk_img_narray = buf.reshape(dim, order='F')

        url = "%s/%s/studies/%s/series/%s/" % (self.dicom_web.host_url, self.dicom_web.wadors_prefix,
                                               self.dicom_web.study_uid, self.dicom_web.series_uid)
        header = dw.HEADERS2
        rescale_params = self.dicom_web.rescale_slope, self.dicom_web.rescale_intercept

        # Thread function
        def _do(_mode):
            instance_uids = self.dicom_web.get_instance_uids()
            num_of_img = len(instance_uids)

            if _mode == 'upper':
                b, e = num_of_img // 2, num_of_img
                uids = instance_uids[b:e]
                def _get_index(x):
                    return x + b
            elif _mode == 'lower':
                b, e = 0, num_of_img // 2
                uids = list(reversed(instance_uids[b:e]))
                def _get_index(x):
                    return e - x - 1
            else:
                b, e = 0, num_of_img
                uids = instance_uids
                def _get_index(x):
                    return x

            def _update(_frame_info):
                for _frame, _idx in _frame_info:
                    self.vtk_img_narray[:, :, _idx] = _frame.reshape(dim[:2], order='F')
                vtk_img.Modified()
                self._win.send_message.emit(['mpr::refresh_all', None])

            processes_cnt = 4
            pool = multiprocessing.Pool(processes=processes_cnt)
            uid_infos = [[url + "instances/%s/frames/1" % uid, header, _get_index(i), rescale_params] for i, uid in enumerate(uids)]
            a = len(uid_infos) // processes_cnt
            b = len(uid_infos) % processes_cnt
            for i in range(a):
                _i = i * processes_cnt
                pool.map_async(dw.requests_buf16, uid_infos[_i:_i+processes_cnt], callback=_update)
            pool.close()
            pool.join()

        # upper
        thread_idx = 1 if not WorkerThread.is_running() else 3
        _fn = eval('WorkerThread.start_worker%d' % thread_idx)
        _fn(_do, 'upper', _finished_func=lambda: print("DICOM Files(Upper) had been loaded!! :)"))
        # lower
        thread_idx = 2 if not WorkerThread.is_running2() else 4
        _fn = eval('WorkerThread.start_worker%d' % thread_idx)
        _fn(_do, 'lower', _finished_func=lambda: print("DICOM Files(Lower) had been loaded!! :)"))

        return vtk_img
