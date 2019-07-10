import os, sys

import numpy as np

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

    def __init__(self, dicom_web=None, *args, **kdws):
        super().__init__()

        self.reset()
        self.initialize()

        self.dicom_web = dicom_web

    def initialize(self):
        self.study_model = StudyModel()

    def reset(self):
        pass

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
                _study_uid = _get(_x, dw.TAG_StudyInstanceUID)
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
                series = self.dicom_web.query_series(_study_uid)
                if not series:
                    continue
                for _j, _y in enumerate(series):
                    _series = dict()
                    _series_uid = _get(_y, dw.TAG_SeriesInstanceUID)
                    _series['Series_Key'] = "1004"
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

    def get_study_model(self):
        return self.study_model
