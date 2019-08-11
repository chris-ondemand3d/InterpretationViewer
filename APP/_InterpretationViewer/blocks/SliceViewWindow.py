import os, sys
import gc
from datetime import datetime
import time

from cyhub.cy_image_holder import CyQQuickView

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QObject, QUrl, QTimer, Qt, pyqtSignal, pyqtSlot, QByteArray
from PyQt5.QtQml import QQmlProperty
from PyQt5.QtGui import QImage


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

        self.root_itme = self._win.rootObject()
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
        self.topbar_thumbnail_item.sigReleaseDummyThumbnail.connect(self.on_release_dummy_thumbnail)
        self.topbar_thumbnail_item.sigClose.connect(self.on_close_data)
        self.topbar_thumbnail_item.sigPositionChanged_Global.connect(self.on_thumbnail_position_changed)
        self.topbar_thumbnail_item.sigDropToOtherApp.connect(self.on_dropped_thumbnail_to_other_app)

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

    def get_next_layout_id(self, force=False):

        # if force is true, return slices's next id
        if force:
            self._mgr.SLICES.append(self._mgr.create_new_slice())
            return len(self._mgr.SLICES) - 1

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

    def refresh_thumbnail_img(self):

        _repeater_sv_thumbnail = self._win.rootObject().findChild(QObject, 'repeater_sv_thumbnail')
        _thumbnail_item = self._win.rootObject().findChild(QObject, 'thumbnail_item')

        thumbnail_cnt = QQmlProperty.read(_repeater_sv_thumbnail, 'count')

        for i, s in enumerate(self._mgr.SLICES):
            dcm_info = s.get_dcm_info()
            if dcm_info and 'study_uid' in dcm_info and 'series_uid' in dcm_info:
                _study_uid = dcm_info['study_uid']
                _series_uid = dcm_info['series_uid']
                _thumbnail_img, _thumbnail_dims, _thumbnail_bits = s.get_scout_img()
                _thumbnail_format = QImage.Format_RGB888 if _thumbnail_bits == 8 else QImage.Format_Grayscale8 if _thumbnail_bits == 16 else None
                if not _thumbnail_img is None:
                    # find thumbnail item by study_uid and series_uid
                    for j in range(thumbnail_cnt):
                        _sub_item = _repeater_sv_thumbnail.itemAt(j)
                        if _sub_item.isExist(_study_uid, _series_uid):
                            _img_item = _sub_item.findChild(QObject, 'img_thumbnail')

                            _source = QQmlProperty.read(_img_item, 'source')
                            if not _source.isEmpty():
                                continue

                            _img = QImage(_thumbnail_img.data, _thumbnail_dims[0], _thumbnail_dims[1], _thumbnail_img.strides[0], _thumbnail_format)
                            _path = os.path.join(os.path.abspath("."), "../_tmp/")
                            if not os.path.exists(_path):
                                os.mkdir(_path)
                            _path = os.path.join(_path, "%s%d.thumb"%
                                                 (datetime.now().strftime("%m%d%Y"), int(round(time.time() * 1000))))
                            _img.save(_path, 'JPG', 70)
                            _url = QUrl.fromLocalFile(_path)
                            _img_item.setProperty('source', _url)

                            os.remove(_path)

                            break

    def busy_check(self):
        layout_cnt = QQmlProperty.read(self.repeater_imgholder, 'count')
        for i, s in enumerate(self._mgr.SLICES[:layout_cnt]):
            _obj = self.repeater_imgholder.itemAt(i)
            if _obj is None:
                continue
            _vtk_img = s.get_vtk_img()
            if _vtk_img is None:
                continue

            _busy = _vtk_img.GetFieldData().GetArray('BUSY')
            if _busy is None:
                _obj.childItems()[1].setBusy(False)
            else:
                _obj.childItems()[1].setBusy(True)

    def appendThumbnail(self, patient_info, study_uid, series_uid):
        _id = patient_info['id']
        _name = patient_info['name']
        _series_id = patient_info['series_id']
        _date = patient_info['date']
        _modality = patient_info['modality']
        self.topbar_thumbnail_item.appendThumbnail(_id, _name, study_uid, series_uid, _series_id, _date, _modality)
        self.refresh_thumbnail_img()

    def set_data_info_str(self, patient_info, layout_id):
        if not len(self._mgr.SLICES) > layout_id:
            return
        self._mgr.SLICES[layout_id].set_patient_info(patient_info)

        _s = self.repeater_imgholder.itemAt(layout_id)
        if not _s:
            return
        _obj = _s.childItems()[1].findChild(QObject, 'col_sv_patient_info')
        self.layout_item.setPatientInfo(_obj, patient_info['id'], patient_info['name'],
                                        patient_info['age'], patient_info['sex'],
                                        patient_info['date'], patient_info['series_id'])

    def set_vtk_img_from_slice_obj(self, slice_obj, layout_id):
        layout_cnt = QQmlProperty.read(self.repeater_imgholder, 'count')
        if layout_cnt > layout_id:
            _item = self.repeater_imgholder.itemAt(layout_id).childItems()[1]
            _item.set_vtk(slice_obj)
            _item.clear()

    def is_contained(self, global_mouse):
        _pos = self._win.mapFromGlobal(global_mouse.toPoint())
        return self.root_itme.contains(_pos)

    def set_dummy_thumbnail(self, global_pos, img_url):
        _pos = self._win.mapFromGlobal(global_pos.toPoint())
        _item = self._win.rootObject().findChild(QObject, 'img_sc_dummythumbnail')
        _w = QQmlProperty.read(_item, 'width')
        _h = QQmlProperty.read(_item, 'height')
        _item.setProperty('visible', True)
        _item.setProperty('x', _pos.x() - _w // 2)
        _item.setProperty('y', _pos.y() - _h // 2)
        _item.setProperty('source', img_url)

    def release_dummy_thumbnail(self):
        _item = self._win.rootObject().findChild(QObject, 'img_sc_dummythumbnail')
        _item.setProperty('visible', False)
        _item.setProperty('x', 0)
        _item.setProperty('y', 0)
        _item.setProperty('source', None)

    def get_layout_id(self, global_mouse):
        _item = self._win.rootObject().findChild(QObject, 'grid_layout')
        _pos = _item.mapFromGlobal(global_mouse.toPoint())
        _obj = _item.childAt(_pos.x(), _pos.y())
        if _obj and _obj.objectName() == 'img_holder_root':
            return _obj.children()[1].getIndex()
        return -1

    def insert_slice_obj(self, slice_obj, next_id):
        patient_info = slice_obj.get_patient_info()
        if not patient_info:
            return False
        dcm_info = slice_obj.get_dcm_info()
        if not dcm_info:
            return False
        self.appendThumbnail(patient_info, dcm_info['study_uid'], dcm_info['series_uid'])
        self.set_vtk_img_from_slice_obj(slice_obj, next_id)
        self.set_data_info_str(patient_info, next_id)
        # busy check
        self.busy_check()
        return True

    def get_slice_obj(self, study_uid, series_uid):
        return self._mgr.get_slice_obj(study_uid, series_uid)

    @pyqtSlot(object, object)
    def on_change_slice_num(self, slice_num, layout_id):
        _obj = self.repeater_imgholder.itemAt(layout_id)
        if not _obj:
            return
        _obj = _obj.childItems()[1]
        self.layout_item.setSliceNumber(_obj, slice_num)

    def on_changed_slice_num(self, slice_num, layout_id):
        # TODO
        pass

    @pyqtSlot(object, object)
    def on_change_thickness(self, thickness, layout_id):
        _obj = self.repeater_imgholder.itemAt(layout_id)
        if not _obj:
            return
        _obj = _obj.childItems()[1]
        self.layout_item.setThickness(_obj, thickness)

    def on_changed_thickness(self, thickness, layout_id):
        layout_id = int(layout_id)
        _obj = self.repeater_imgholder.itemAt(layout_id)
        if not _obj:
            return
        _obj = _obj.childItems()[1]
        self._mgr.SLICES[layout_id].set_thickness(thickness)

    @pyqtSlot(object, object)
    def on_change_filter(self, img_filter, layout_id):
        _obj = self.repeater_imgholder.itemAt(layout_id)
        if not _obj:
            return
        _obj = _obj.childItems()[1]
        self.layout_item.setFilter(_obj, img_filter)

    def on_changed_filter(self, img_filter, layout_id):
        layout_id = int(layout_id)
        _obj = self.repeater_imgholder.itemAt(layout_id)
        if not _obj:
            return
        _obj = _obj.childItems()[1]
        self._mgr.SLICES[layout_id].set_image_filter_type(img_filter)

    @pyqtSlot(object, object, object)
    def on_change_wwl(self, ww, wl, layout_id):
        _obj = self.repeater_imgholder.itemAt(layout_id)
        if not _obj:
            return
        _obj = _obj.childItems()[1]
        self.layout_item.setWWL(_obj, ww, wl)

    def on_changed_wwl(self, ww, wl, layout_id):
        # TODO
        pass

    def on_close_view(self, study_uid, series_uid):

        new_slice = self._mgr.create_new_slice()

        # 1. release thumbnail
        self.topbar_thumbnail_item.removeThumbnail(study_uid, series_uid)

        # 2. replace specified slice img with blank img & remove slice img from "SLICES" & clear qml items
        layout_cnt = QQmlProperty.read(self.repeater_imgholder, 'count')
        for i, s in enumerate(self._mgr.SLICES[:]):
            dcm_info = s.get_dcm_info()
            if dcm_info and 'study_uid' in dcm_info and 'series_uid' in dcm_info:
                _study_uid = dcm_info['study_uid']
                _series_uid = dcm_info['series_uid']
                if study_uid == _study_uid and series_uid == _series_uid:
                    if layout_cnt > i:
                        _item = self.repeater_imgholder.itemAt(i).childItems()[1]
                        _item.set_vtk(new_slice)
                        del s
                        self._mgr.SLICES[i] = new_slice
                        # NOTE item.clear() function should be called after remove the s(slice object)
                        _item.clear()
                    else:
                        del s
                        self._mgr.SLICES[i] = new_slice
                    break

        # 3. refresh thumbnails
        self.refresh_thumbnail_img()

    def on_close_data(self, study_uid, series_uid):

        new_slice = self._mgr.create_new_slice()

        # 1. release thumbnail
        self.topbar_thumbnail_item.removeThumbnail(study_uid, series_uid)

        # 2. release imageholder & release slice(vtk_img) - vtk part & clear qml items
        layout_cnt = QQmlProperty.read(self.repeater_imgholder, 'count')
        for i, s in enumerate(self._mgr.SLICES[:]):
            dcm_info = s.get_dcm_info()
            if dcm_info and 'study_uid' in dcm_info and 'series_uid' in dcm_info:
                _study_uid = dcm_info['study_uid']
                _series_uid = dcm_info['series_uid']
                if study_uid == _study_uid and series_uid == _series_uid:
                    if layout_cnt > i:
                        _item = self.repeater_imgholder.itemAt(i).childItems()[1]
                        _item.set_vtk(new_slice)
                        s.reset()
                        del s
                        self._mgr.SLICES[i] = new_slice
                        # NOTE item.clear() function should be called after remove the s(slice object)
                        _item.clear()
                    else:
                        s.reset()
                        del s
                        self._mgr.SLICES[i] = new_slice
                    break

        # 3. force garbage collector!!!
        gc.collect()

        # 4. refresh thumbnails
        self.refresh_thumbnail_img()

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

                    # busy check
                    self.busy_check()

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

    def on_release_dummy_thumbnail(self):
        self._win.send_message.emit(['slice::release_dummy_thumbnail', None])

    def on_thumbnail_position_changed(self, global_mouse, img_url):
        if not global_mouse:
            return
        _contained = self.is_contained(global_mouse)
        if not _contained:
            self._win.send_message.emit(['slice::set_dummy_thumbnail', [global_mouse, img_url]])
        else:
            self._win.send_message.emit(['slice::release_dummy_thumbnail', None])

    def on_dropped_thumbnail_to_other_app(self, global_mouse, study_uid, series_uid):
        if not global_mouse:
            return
        _contained = self.is_contained(global_mouse)
        if not _contained:
            self._win.send_message.emit(['slice::send_to_other_app', [global_mouse, study_uid, series_uid]])
