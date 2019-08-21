import os, sys
from datetime import datetime
import time

import shutil

from cyhub.cy_image_holder import CyQQuickView

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QObject, QUrl, QTimer, Qt, pyqtSlot, QVariant
from PyQt5.QtQml import QQmlProperty
from PyQt5.QtGui import QImage


class DBMWindow(QObject):
    def __init__(self, _app, _mgr, *args, **kdws):
        super().__init__()
        self._app = _app
        self._mgr = _mgr

        # self.reset()
        self.initialize()

    def initialize(self):
        self.study_model = self._mgr.get_study_model()
        self.related_study_model = self._mgr.get_related_study_model()
        self._app.rootContext().setContextProperty('study_treeview_model', self.study_model)
        self._app.rootContext().setContextProperty('related_study_treeview_model', self.related_study_model)
        # self.dbm.PT_sort_data(4, 0)

        # query studies & init treeview
        self.refresh_study_model()

        _win_source = QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), '../layout/dbm/DBM_layout.qml'))
        self._app.setSource(_win_source)

        self.dbm_msg_box_item = self._app.rootObject().findChild(QObject, 'dbm_message_box')
        self.dbm_study_thumbnail_item = self._app.rootObject().findChild(QObject, 'dbm_study_thumbnail_item')
        self.dbm_related_study_thumbnail_item = self._app.rootObject().findChild(QObject, 'dbm_related_study_thumbnail_item')

        # connect signals
        study_treeview_item = self._app.rootObject().findChild(QObject, 'study_treeview')
        study_treeview_item.sig_changed_index.connect(self.on_index_changed)
        study_treeview_item.sig_childitem_dclick.connect(self.on_childitem_dblclick)
        study_treeview_item.sig_menu_trigger.connect(self.on_data_load)
        related_study_treeview_item = self._app.rootObject().findChild(QObject, 'related_study_treeview')
        related_study_treeview_item.sig_changed_index.connect(self.on_index_changed)
        related_study_treeview_item.sig_childitem_dclick.connect(self.on_childitem_dblclick)
        related_study_treeview_item.sig_menu_trigger.connect(self.on_data_load)

    def reset(self):
        #TODO!!!
        # win reset
        # self._app.reset()

        def _remove(X):
            if type(X) is not dict:
                for o in X:
                    del o
            X.clear()

    def refresh_study_model(self):
        return self._mgr.refresh_study_model()

    def refresh_related_study_model(self, _model):

        # 1. clear model
        self._mgr.clear_related_study_model()

        # 2. get patiend id
        if _model.parent() is None:
            """
            case of study
            """
            _patiend_id = _model.itemData['PatientID']
        else:
            """
            case of series
            """
            _patiend_id = _model.parent().itemData['PatientID']

        if _patiend_id is None:
            return False

        # 3. filter by patiend id & set model
        self._mgr.refresh_related_study_model(_patiend_id)

    def initialize_thumbnail(self, model, which_model=None):
        _model_item = None
        if which_model == 'study_model':
            _model_item = self.dbm_study_thumbnail_item
        elif which_model == 'related_study_model':
            _model_item = self.dbm_related_study_thumbnail_item

        if not _model_item:
            return

        # 1. clear model
        _model_item.clearThumbnail()

        def _parse(_model):
            _a = _model.parent().itemData['PatientID']
            _b = _model.parent().itemData['PatientName']
            _c = _model.parent().itemData['StudyInstanceUID']
            _d = _model.itemData['SeriesInstanceUID']
            _e = _model.itemData['PatientID']
            # _f = _model..itemData['DateTime']
            _f = _model.parent().itemData['DateTime']
            _g = _model.itemData['Modality']
            _h = _model.itemData['Imgs']
            return _a, _b, _c, _d, _e, _f, _g, _h

        # 2.
        if model.parent() is None:
            """
            case of study
            """
            from random import random
            _children = model.children()
            for _series in _children[:]:
                _params = _parse(_series)
                _study_uid, _series_uid, _num = _params[2], _params[3], _params[7]
                _model_item.appendThumbnail(*_params)

                # thumbnail
                self._mgr.retrieve_thumbnail(_study_uid, _series_uid, _num)
        else:
            """
            case of series
            """
            _params = _parse(model)
            _study_uid, _series_uid, _num = _params[2], _params[3], _params[7]
            _model_item.appendThumbnail(*_params)
            self._mgr.retrieve_thumbnail(_study_uid, _series_uid, _num)

    def clear_thumbnail(self, which_model=None):
        _model_item = None
        if which_model == 'study_model':
            _model_item = self.dbm_study_thumbnail_item
        elif which_model == 'related_study_model':
            _model_item = self.dbm_related_study_thumbnail_item

        if not _model_item:
            return

        _model_item.clearThumbnail()

    def refresh_thumbnail_img(self):

        _repeater_item = self.dbm_study_thumbnail_item.getRepeaterItem()
        thumbnail_cnt = QQmlProperty.read(_repeater_item, 'count')
        for i in range(thumbnail_cnt):
            _item = _repeater_item.itemAt(i)
            _study_uid = _item.getStudyUID()
            _series_uid = _item.getSeriesUID()
            if _study_uid in self._mgr.thumbnails:
                if _series_uid in self._mgr.thumbnails[_study_uid]:
                    _img_url = self._mgr.thumbnails[_study_uid][_series_uid]
                    _item.setProperty('img', _img_url)

        _repeater_item2 = self.dbm_related_study_thumbnail_item.getRepeaterItem()
        thumbnail_cnt = QQmlProperty.read(_repeater_item2, 'count')
        for i in range(thumbnail_cnt):
            _item = _repeater_item2.itemAt(i)
            _study_uid = _item.getStudyUID()
            _series_uid = _item.getSeriesUID()
            if _study_uid in self._mgr.thumbnails:
                if _series_uid in self._mgr.thumbnails[_study_uid]:
                    _img_url = self._mgr.thumbnails[_study_uid][_series_uid]
                    _item.setProperty('img', _img_url)

    @pyqtSlot(QVariant, bool)
    def on_index_changed(self, index, trigger):
        if index is None:
            return
        selected_model = index.internalPointer()

        if index.model() is self.study_model:
            self.refresh_related_study_model(selected_model)
            self.clear_thumbnail('related_study_model')
            self.initialize_thumbnail(selected_model, 'study_model')
        elif index.model() is self.related_study_model:
            self.initialize_thumbnail(selected_model, 'related_study_model')

    @pyqtSlot(QVariant)
    def on_childitem_dblclick(self, index):
        if index is None:
            return
        selected_model = index.internalPointer()
        # to check the dicom data is already exists.
        self._app.send_message.emit(['dbm::load_data', [[selected_model, ], 0]])

    @pyqtSlot(str, QVariant)
    def on_data_load(self, cmd, indices):
        indices = indices.toVariant()
        models = [index.internalPointer() for index in indices]
        if cmd == 'view(1)':
            self._app.send_message.emit(['dbm::load_data', [models, 0]])
        if cmd == 'view(2)':
            self._app.send_message.emit(['dbm::load_data', [models, 1]])
