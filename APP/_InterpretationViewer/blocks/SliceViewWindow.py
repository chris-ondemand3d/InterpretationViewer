import os, sys
import gc

from cyhub.cy_image_holder import CyQQuickView

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QObject, QUrl, QTimer, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtQml import QQmlProperty


class SliceViewWindow(QObject):
    def __init__(self, _win, _mgr, *args, **kdws):
        super().__init__()
        self._win = _win
        self._mgr = _mgr

        # self.reset()
        self.initialize()

    def initialize(self):
        # win init
        _win_source = QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), '../layout/slice_view/SliceView_layout.qml'))
        self._win.setSource(_win_source)

        self.topbar_thumbnail_item = self._win.rootObject().findChild(QObject, 'sliceview_topbar_thumbnail')
        self.layout_item = self._win.rootObject().findChild(QObject, 'sliceview_mxn_layout')
        self.repeater_imgholder = self._win.rootObject().findChild(QObject, 'repeater_imgholder_sliceview')
        cnt = QQmlProperty.read(self.repeater_imgholder, 'count')

        if not hasattr(self, '_mgr'):
            return

        # initialize slices
        self._mgr.init_slice(cnt)

        # initialize sig/slot of Python
        self._mgr.sig_change_slice_num.connect(self.on_change_slice_num)
        self._mgr.sig_change_thickness.connect(self.on_change_thickness)
        self._mgr.sig_change_filter.connect(self.on_change_filter)
        self._mgr.sig_change_wwl.connect(self.on_change_wwl)

        # initialize sig/slot of QML
        self.topbar_thumbnail_item.sigDrop.connect(self.on_dropped_thumbnail)
        self.topbar_thumbnail_item.sigHighlight.connect(self.on_hightlight)
        self.topbar_thumbnail_item.sigClose.connect(self.on_close_data)

        for i, s in enumerate(self._mgr.SLICES):
            item = self.repeater_imgholder.itemAt(i).childItems()[1]
            _w = QQmlProperty.read(item, 'width')
            _h = QQmlProperty.read(item, 'height')
            item.setHeight(2000)
            item.setWidth(2000)
            item.set_vtk(s)
            item.setHeight(_w)
            item.setWidth(_h)
            # item.installEventFilter(self._win) # to grab mouse hover leave, add eventfilter

            # initialize sig/slot of QML ImageHolder
            _obj_th = item.findChild(QObject, 'col_sv_thickness')
            _obj_th.sigChanged.connect(self.on_changed_thickness)
            _obj_filter = item.findChild(QObject, 'col_sv_image_filter')
            _obj_filter.sigChanged.connect(self.on_changed_filter)

    def reset(self):
        #TODO!!!
        # win reset
        # self._win.reset()

        def _remove(X):
            if type(X) is not dict:
                for o in X:
                    del o
            X.clear()

        if hasattr(self, 'items'):
            _remove(self.items)

    def get_next_layout_id(self):
        # get layout count
        layout_cnt = QQmlProperty.read(self.repeater_imgholder, 'count')

        # get next available id
        next_id = self._mgr.get_next_layout_id(limit=layout_cnt)

        if next_id == -1:
            return next_id

        # get fullscreen status
        F = [QQmlProperty.read(self.repeater_imgholder.itemAt(i).childItems()[1], 'fullscreenTrigger')
             for i, s in enumerate(self._mgr.SLICES[0:layout_cnt])]
        F_IDX = [i for i, elem in enumerate(F) if elem is True]
        # get vtk image init status
        I = [s.vtk_img for i, s in enumerate(self._mgr.SLICES[0:layout_cnt])]

        # if any views are fullscreen mode,
        if any(F):
            # if vtk img isn't initialized at fullscreen idx, return fullscreen idx
            if len(F_IDX) > 0 and I[F_IDX[0]] is None:
                return F_IDX[0]
            # vtk img isn't initialized at next idx, return next_id. so, it's an available next_id!
            elif F[next_id] and I[next_id] is None:
                return next_id
            # else, return -1 for skip to next application.
            return -1
        # else, return next available id
        return next_id

    def fullscreen(self, layout_idx, fullscreen_mode):
        item = self.repeater_imgholder.itemAt(layout_idx).childItems()[1]
        item.setProperty('fullscreenTrigger', fullscreen_mode)

    def appendThumbnail(self, patient_info, study_uid, series_uid):
        _id = patient_info['id']
        _name = patient_info['name']
        _series_id = patient_info['series_id']
        _date = patient_info['date']
        _modality = patient_info['modality']
        _thumbnail_item = self._win.rootObject().findChild(QObject, 'sliceview_topbar_thumbnail')
        _thumbnail_item.appendThumbnail(_id, _name, study_uid, series_uid, _series_id, _date, _modality)

    def set_data_info_str(self, patient_info, layout_id):
        self._mgr.SLICES[layout_id].set_patient_info(patient_info)
        _s = self.repeater_imgholder.itemAt(layout_id).childItems()[1]
        _obj = _s.findChild(QObject, 'col_sv_patient_info')
        self.layout_item.setPatientInfo(_obj, patient_info['id'], patient_info['name'],
                                        patient_info['age'], patient_info['sex'],
                                        patient_info['date'], patient_info['series_id'])

    @pyqtSlot(object, object)
    def on_change_slice_num(self, slice_num, layout_id):
        _obj = self.repeater_imgholder.itemAt(layout_id).childItems()[1]
        self.layout_item.setSliceNumber(_obj, slice_num)

    def on_changed_slice_num(self, slice_num, layout_id):
        # TODO
        pass

    @pyqtSlot(object, object)
    def on_change_thickness(self, thickness, layout_id):
        _obj = self.repeater_imgholder.itemAt(layout_id).childItems()[1]
        self.layout_item.setThickness(_obj, thickness)

    def on_changed_thickness(self, thickness, layout_id):
        layout_id = int(layout_id)
        _obj = self.repeater_imgholder.itemAt(layout_id).childItems()[1]
        self._mgr.SLICES[layout_id].set_thickness(thickness)

    @pyqtSlot(object, object)
    def on_change_filter(self, img_filter, layout_id):
        _obj = self.repeater_imgholder.itemAt(layout_id).childItems()[1]
        self.layout_item.setFilter(_obj, img_filter)

    def on_changed_filter(self, img_filter, layout_id):
        layout_id = int(layout_id)
        _obj = self.repeater_imgholder.itemAt(layout_id).childItems()[1]
        self._mgr.SLICES[layout_id].set_image_filter_type(img_filter)

    @pyqtSlot(object, object, object)
    def on_change_wwl(self, ww, wl, layout_id):
        _obj = self.repeater_imgholder.itemAt(layout_id).childItems()[1]
        self.layout_item.setWWL(_obj, ww, wl)

    def on_changed_wwl(self, ww, wl, layout_id):
        # TODO
        pass

    def on_close_data(self, study_uid, series_uid):

        new_slice = None

        # 1. release thumbnail
        _thumbnail_item = self._win.rootObject().findChild(QObject, 'sliceview_topbar_thumbnail')
        _thumbnail_item.removeThumbnail(study_uid, series_uid)

        # 2. release imageholder - qml part
        layout_cnt = QQmlProperty.read(self.repeater_imgholder, 'count')
        for i, s in enumerate(self._mgr.SLICES[0:layout_cnt]):
            dcm_info = s.get_dcm_info()
            if dcm_info and 'study_uid' in dcm_info and 'series_uid' in dcm_info:
                _study_uid = dcm_info['study_uid']
                _series_uid = dcm_info['series_uid']
                if study_uid == _study_uid and series_uid == _series_uid:
                    _item = self.repeater_imgholder.itemAt(i).childItems()[1]
                    new_slice = self._mgr.create_new_slice()
                    _item.set_vtk(new_slice)
                    _item.clear()
                    break

        # 3. release slice(vtk_img) - vtk part
        for i, s in enumerate(self._mgr.SLICES[:]):
            dcm_info = s.get_dcm_info()
            if dcm_info and 'study_uid' in dcm_info and 'series_uid' in dcm_info:
                _study_uid = dcm_info['study_uid']
                _series_uid = dcm_info['series_uid']
                if study_uid == _study_uid and series_uid == _series_uid:
                    s.reset()
                    del s
                    self._mgr.SLICES[i] = new_slice
                    break

        # 4. force garbage collector!!!
        gc.collect()

    def on_dropped_thumbnail(self, picked_layout_id, study_uid, series_uid):

        picked_layout_id = int(picked_layout_id)
        layout_cnt = QQmlProperty.read(self.repeater_imgholder, 'count')

        for i, s in enumerate(self._mgr.SLICES):

            dcm_info = s.get_dcm_info()

            if dcm_info and 'study_uid' in dcm_info and 'series_uid' in dcm_info:

                _study_uid = dcm_info['study_uid']
                _series_uid = dcm_info['series_uid']

                if study_uid == _study_uid and series_uid == _series_uid:

                    # do nothing if slice is self-selected
                    if picked_layout_id == i:
                        return

                    # get imgholder and set slice
                    _item = self.repeater_imgholder.itemAt(picked_layout_id).childItems()[1]
                    _item.set_vtk(s)

                    # switch slice object
                    _tmp_s = self._mgr.SLICES[picked_layout_id]
                    self._mgr.SLICES[picked_layout_id] = s
                    self._mgr.SLICES[i] = self._mgr.create_new_slice()
                    self._mgr.SLICES.append(_tmp_s)

                    # set dummy slice and clear
                    if layout_cnt > i:
                        _item = self.repeater_imgholder.itemAt(i).childItems()[1]
                        _item.set_vtk(self._mgr.SLICES[i])
                        _item.clear()


                    # refresh qml text items (patient id, name, age, sex ...)
                    self._mgr.refresh_text_items(picked_layout_id)
                    _patient_info = s.get_patient_info()
                    self.set_data_info_str(_patient_info, picked_layout_id)

                    return

            continue

    def on_hightlight(self, study_uid, series_uid, on):
        layout_cnt = QQmlProperty.read(self.repeater_imgholder, 'count')
        for i, s in enumerate(self._mgr.SLICES[0:layout_cnt]):
            dcm_info = s.get_dcm_info()
            if dcm_info and 'study_uid' in dcm_info and 'series_uid' in dcm_info:
                _study_uid = dcm_info['study_uid']
                _series_uid = dcm_info['series_uid']
                if study_uid == _study_uid and series_uid == _series_uid:
                    # get imgholder's titlebar and set highlight
                    _item = self.repeater_imgholder.itemAt(i).childItems()[0]
                    _item.setProperty('highlight', on)
