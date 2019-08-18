import os, sys
import gc
from datetime import datetime
import time

from cyhub.cy_image_holder import CyQQuickView

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QObject, QUrl, QTimer, Qt, pyqtSignal, pyqtSlot, QByteArray, QVariant, QEvent
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
        self.layout_item = self._win.rootObject().findChild(QObject, 'sliceview_mxn_layout')

        self.topbar_study_item = self._win.rootObject().findChild(QObject, 'sliceview_topbar_panel')
        self.repeater_study = self._win.rootObject().findChild(QObject, 'repeater_sv_study')

        self.topbar_thumbnail_item = self._win.rootObject().findChild(QObject, 'sliceview_topbar_thumbnail')
        self.repeater_series = self._win.rootObject().findChild(QObject, 'repeater_sv_thumbnail')

        self.repeater_imgholder = self._win.rootObject().findChild(QObject, 'repeater_imgholder_sliceview')

        self.menu_common_item = self._win.rootObject().findChild(QObject, 'sliceview_menu_common')
        self.menu_measure_item = self._win.rootObject().findChild(QObject, 'sliceview_menu_measure')


        if not hasattr(self, '_mgr'):
            return

        # initialize sig/slot of Python

        self._mgr.sig_changed_slice.connect(self.on_changed_slice) # TODO

        self._mgr.sig_change_slice_num.connect(self.on_change_slice_num)
        self._mgr.sig_change_thickness.connect(self.on_change_thickness)
        self._mgr.sig_change_filter.connect(self.on_change_filter)
        self._mgr.sig_change_wwl.connect(self.on_change_wwl)

        # initialize sig/slot of QML
        # keyboard signal
        self.layout_item.sigKeyPressed.connect(lambda _key, _modifiers:
                                               self._win.send_message.emit(['common::set_key_event', (_key, _modifiers)]))
        self.layout_item.sigKeyReleased.connect(lambda _key, _modifiers:
                                                self._win.send_message.emit(['common::set_key_event', (_key, _modifiers)]))
        # for study
        self.topbar_study_item.sigSelected.connect(self.on_selected_study)
        self.topbar_study_item.sigReleaseDummyThumbnail.connect(self.on_release_dummy_thumbnail)
        self.topbar_study_item.sigClose.connect(self.on_close_data)
        self.topbar_study_item.sigPositionChanged_Global.connect(self.on_thumbnail_position_changed)
        self.topbar_study_item.sigDropToOtherApp.connect(self.on_dropped_thumbnail_to_other_app)
        # for thumbnail(series)
        self.topbar_thumbnail_item.sigDrop.connect(self.on_dropped_thumbnail)
        self.topbar_thumbnail_item.sigHighlight.connect(self.on_hightlight)
        self.topbar_thumbnail_item.sigReleaseDummyThumbnail.connect(self.on_release_dummy_thumbnail)
        self.topbar_thumbnail_item.sigClose.connect(self.on_close_data)
        self.topbar_thumbnail_item.sigPositionChanged_Global.connect(self.on_thumbnail_position_changed)
        self.topbar_thumbnail_item.sigDropToOtherApp.connect(self.on_dropped_thumbnail_to_other_app)
        # menu panel
        self.menu_common_item.sigSelected.connect(self.on_selected_menu)
        self.menu_measure_item.sigSelected.connect(self.on_selected_menu)
        self.menu_common_item.retrySelect()

        layout_cnt = QQmlProperty.read(self.repeater_imgholder, 'count')
        for i in range(layout_cnt):
            item = self.repeater_imgholder.itemAt(i).childItems()[1]
            _w = QQmlProperty.read(item, 'width')
            _h = QQmlProperty.read(item, 'height')
            item.setHeight(2000)
            item.setWidth(2000)
            # item.set_vtk(None)
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

    def set_key_event(self, _key, _modifiers):
        self.layout_item.setKeyInfo(_key, _modifiers)

    def init_vtk(self, _vtk_img, patient_pos_ori, _wwl, _patient_info, study_uid, series_uid, next_id):
        _dcm_info = {'study_uid': study_uid, 'series_uid': series_uid}           # TODO

        # generate slices[...]
        _new_slice = self._mgr.create_new_slice()
        if study_uid in self._mgr.ALL_SLICES:
            self._mgr.ALL_SLICES[study_uid][_new_slice] = next_id
        else:
            self._mgr.ALL_SLICES[study_uid] = {_new_slice: next_id}
        self._mgr.SELECTED_SLICES = self._mgr.ALL_SLICES[study_uid]

        # ...
        self.append_study_series_model(_patient_info, study_uid, series_uid)
        self.set_metadata(_patient_info, _dcm_info, next_id)
        self._mgr.init_vtk(_vtk_img, patient_pos_ori, _wwl, next_id)
        self.select_study(study_uid)

        #
        self._mgr.fit_screen_all()

    # will be deprecated
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

    def get_next_layout_id2(self, _study_uid):
        # get next available id
        return self._mgr.get_next_layout_id2(_study_uid)

    def fullscreen(self, layout_idx, fullscreen_mode):
        item = self.repeater_imgholder.itemAt(layout_idx).childItems()[1]
        item.setProperty('fullscreenTrigger', fullscreen_mode)

    def refresh_thumbnail_img(self):

        _repeater_sv_thumbnail = self._win.rootObject().findChild(QObject, 'repeater_sv_thumbnail')
        _thumbnail_item = self._win.rootObject().findChild(QObject, 'thumbnail_item')

        thumbnail_cnt = QQmlProperty.read(_repeater_sv_thumbnail, 'count')

        for s, i in self._mgr.SELECTED_SLICES.items():
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
        for s, i in self._mgr.SELECTED_SLICES.items():
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

    def append_study_series_model(self, patient_info, study_uid, series_uid):
        self._appendStudy(patient_info, study_uid)
        self._appendThumbnail(patient_info, study_uid, series_uid)

    def _appendStudy(self, patient_info, study_uid):
        _id = patient_info['id']
        _name = patient_info['name']
        _date = patient_info['date']
        self.topbar_study_item.appendStudy(_id, _name, study_uid, _date)

    def _appendThumbnail(self, patient_info, study_uid, series_uid):
        _id = patient_info['id']
        _name = patient_info['name']
        _series_id = patient_info['series_id']
        _date = patient_info['date']
        _modality = patient_info['modality']
        self.topbar_thumbnail_item.appendThumbnail(_id, _name, study_uid, series_uid, _series_id, _date, _modality)
        self.refresh_thumbnail_img()

    def set_metadata(self, patient_info, dcm_info, layout_id):
        for _s, _i in self._mgr.SELECTED_SLICES.items():
            if _i == layout_id:
                _s.set_patient_info(patient_info)
                _s.set_dcm_info(dcm_info)
                return True
        return False

    def refresh_item(self, layout_id):
        self._refresh_status_item(layout_id)
        self._refresh_patient_info_item(layout_id)

    def _refresh_status_item(self, layout_id):
        self._mgr.refresh_status_item(layout_id)

    def _refresh_patient_info_item(self, layout_id):
        if not layout_id in list(self._mgr.SELECTED_SLICES.values()):
            return
        _slice = list(self._mgr.SELECTED_SLICES.keys())[list(self._mgr.SELECTED_SLICES.values()).index(layout_id)]
        _patient_info = _slice.get_patient_info()
        _s = self.repeater_imgholder.itemAt(layout_id)
        if _s and _patient_info:
            _obj = _s.childItems()[1].findChild(QObject, 'col_sv_patient_info')
            self.layout_item.setPatientInfo(_obj, _patient_info['id'], _patient_info['name'],
                                            _patient_info['age'], _patient_info['sex'],
                                            _patient_info['date'], _patient_info['series_id'])

    def set_vtk_img_from_slice_obj(self, slice_obj, layout_id):
        layout_cnt = QQmlProperty.read(self.repeater_imgholder, 'count')
        if layout_cnt > layout_id:
            _item = self.repeater_imgholder.itemAt(layout_id).childItems()[1]
            _item.set_vtk(slice_obj)
            _item.clear()

    def is_contained(self, global_mouse):
        _pos = self._win.mapFromGlobal(global_mouse.toPoint())
        return self.root_itme.contains(_pos)

    def set_dummy_thumbnail(self, global_pos, img_url, mode):
        _pos = self._win.mapFromGlobal(global_pos.toPoint())
        _item = self._win.rootObject().findChild(QObject, 'img_sc_dummythumbnail')
        if mode == 'study_thumbnail':
            _item.set_study_preview_mode()
        elif mode == 'series_thumbnail':
            _item.set_default_mode()
        elif mode == 'series_preview':
            _item.set_series_preview_mode()
        else:
            _item.set_default_mode()
        _w = QQmlProperty.read(_item, 'width')
        _h = QQmlProperty.read(_item, 'height')
        _item.setProperty('visible', True)
        _item.setProperty('x', _pos.x() - _w // 2)
        _item.setProperty('y', _pos.y() - _h // 2)
        _item.setProperty('source', img_url)

    def release_dummy_thumbnail(self):
        _item = self._win.rootObject().findChild(QObject, 'img_sc_dummythumbnail')
        _item.set_default_mode()
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
        # get metadata
        patient_info = slice_obj.get_patient_info()
        if not patient_info:
            return False
        dcm_info = slice_obj.get_dcm_info()
        if not dcm_info:
            return False

        # insert slice obj to mgr's slices dict
        layout_id = self._mgr.insert_slice_obj(slice_obj, next_id)
        if layout_id == -1:
            return False

        # set vtk & set metadata
        self.set_vtk_img_from_slice_obj(slice_obj, layout_id)
        self.set_metadata(patient_info, dcm_info, layout_id)

        # select slices from study_uid
        self.select_study(dcm_info['study_uid'])
        _idx = self.topbar_study_item.getIndex(dcm_info['study_uid'])
        self.topbar_study_item.refreshToggleStatus(_idx)

        return True

    def get_slice_obj(self, study_uid, series_uid):
        return self._mgr.get_slice_obj(study_uid, series_uid)

    def get_slice_objs(self, study_uid):
        return self._mgr.get_slice_objs(study_uid)

    def move_selected_slice(self, value, layout_id=None):
        # 1. get selected items (view) & send wheel event
        indices = self.layout_item.getSelectedIndices()
        if indices is None:
            return
        indices = indices.toVariant()

        if not layout_id is None:
            try:
                indices.remove(layout_id)
            except ValueError:
                pass

        self._mgr.move_selected_slice(value, indices)

    @pyqtSlot(object, object)
    def on_changed_slice(self, value, layout_id):
        # 1. get selected items (view) & send wheel event
        self.move_selected_slice(value, layout_id)
        # 2. send msg to others app
        self._win.send_message.emit(['slice::change_selected_slice_of_other_app', [value, self._win]])

    @pyqtSlot(object, object)
    def on_change_slice_num(self, slice_num, layout_id):
        _obj = self.repeater_imgholder.itemAt(layout_id)
        if not _obj:
            return
        _obj = _obj.childItems()[1]
        self.layout_item.setSliceNumber(_obj, slice_num)

        # TODO CROSS LINK TEST!!!
        _keys = list(self._mgr.SELECTED_SLICES.keys())
        _values = list(self._mgr.SELECTED_SLICES.values())
        _cur_slice = _keys[_values.index(layout_id)]
        try:
            _senders_pos_ori = _cur_slice.patient_pos_ori[slice_num]
        except IndexError:
            return
        for _s, _i in self._mgr.SELECTED_SLICES.items():
            if _i == layout_id:
                continue
            _s.cross_link_test(_senders_pos_ori)

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
        if layout_id in list(self._mgr.SELECTED_SLICES.values()):
            s = list(self._mgr.SELECTED_SLICES.keys())[list(self._mgr.SELECTED_SLICES.values()).index(layout_id)]
            s.set_thickness(thickness)
            s.refresh()

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
        if layout_id in list(self._mgr.SELECTED_SLICES.values()):
            s = list(self._mgr.SELECTED_SLICES.keys())[list(self._mgr.SELECTED_SLICES.values()).index(layout_id)]
            s.set_image_filter_type(img_filter)

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
        """
        NOTE emitted by sigDropToOtherApp thumbnail(series) or study(?)
        """

        # 1. release thumbnail(series)
        self.topbar_thumbnail_item.removeThumbnail(study_uid, series_uid)
        # 2. check if there is any slice with study_uid.
        exist = self.topbar_thumbnail_item.isExist(study_uid)
        if exist is False:
            # removeStudy
            self.topbar_study_item.removeStudy(study_uid)

        # 3. release imageholder & release slice(vtk_img) - vtk part & clear qml items
        waiting_list = []
        for s, i in self._mgr.SELECTED_SLICES.items():
            dcm_info = s.get_dcm_info()
            if dcm_info and 'study_uid' in dcm_info and 'series_uid' in dcm_info:
                _study_uid = dcm_info['study_uid']
                _series_uid = dcm_info['series_uid']

                if study_uid == _study_uid:
                    if series_uid == _series_uid:
                        _item = self.repeater_imgholder.itemAt(i)
                        _item = _item.childItems()[1] if _item else None
                        waiting_list.append([s, _item])
                        break
                    elif series_uid is None:
                        _item = self.repeater_imgholder.itemAt(i)
                        _item = _item.childItems()[1] if _item else None
                        waiting_list.append([s, _item])
        for _slice, _item in waiting_list:
            self._mgr.SELECTED_SLICES.pop(_slice)
            del _slice
            if _item:
                _item.set_vtk(None)
                _item.clear()
        waiting_list.clear()

        # 4. force garbage collector!!!
        gc.collect()

        # 5. refresh thumbnails
        self.refresh_thumbnail_img()

    def on_close_data(self, study_uid, series_uid=None):
        """
        NOTE emitted by sigClose of thumbnail(series) or study
        """

        # 1. release thumbnail(series)
        self.topbar_thumbnail_item.removeThumbnail(study_uid, series_uid)
        # 2. check if there is any slice with study_uid.
        exist = self.topbar_thumbnail_item.isExist(study_uid)
        if exist is False:
            # removeStudy
            self.topbar_study_item.removeStudy(study_uid)

        # 3. release imageholder & release slice(vtk_img) - vtk part & clear qml items
        waiting_list = []
        for s, i in self._mgr.SELECTED_SLICES.items():
            dcm_info = s.get_dcm_info()
            if dcm_info and 'study_uid' in dcm_info and 'series_uid' in dcm_info:
                _study_uid = dcm_info['study_uid']
                _series_uid = dcm_info['series_uid']

                # stop dicom web
                self._win.send_message.emit(['dbm::stop', [_study_uid, _series_uid]])

                if study_uid == _study_uid:
                    if series_uid == _series_uid:
                        _item = self.repeater_imgholder.itemAt(i)
                        _item = _item.childItems()[1] if _item else None
                        waiting_list.append([s, _item])
                        break
                    elif series_uid is None:
                        _item = self.repeater_imgholder.itemAt(i)
                        _item = _item.childItems()[1] if _item else None
                        waiting_list.append([s, _item])
        for _slice, _item in waiting_list:
            self._mgr.SELECTED_SLICES.pop(_slice)
            _slice.reset()
            del _slice
            if _item:
                _item.set_vtk(None)
                _item.clear()
        waiting_list.clear()

        # 4. force garbage collector!!!
        gc.collect()

        # 5. refresh thumbnails
        self.refresh_thumbnail_img()

    def on_dropped_thumbnail(self, picked_layout_id, study_uid, series_uid):

        picked_layout_id = int(picked_layout_id)
        layout_cnt = QQmlProperty.read(self.repeater_imgholder, 'count')

        for s, i in self._mgr.SELECTED_SLICES.items():

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
                    _keys = list(self._mgr.SELECTED_SLICES.keys())
                    _values = list(self._mgr.SELECTED_SLICES.values())
                    if picked_layout_id in _values:
                        _new_idx = max(_values) + 1
                        _picked_s = _keys[_values.index(picked_layout_id)]
                        self._mgr.SELECTED_SLICES[_picked_s] = _new_idx
                    self._mgr.SELECTED_SLICES[s] = picked_layout_id

                    # set dummy slice and clear
                    if layout_cnt > i:
                        _item = self.repeater_imgholder.itemAt(i).childItems()[1]
                        _item.set_vtk(None)
                        _item.clear()

                    # refresh qml text items (patient id, name, age, sex ...)
                    self.refresh_item(picked_layout_id)

                    # busy check
                    self.busy_check()

                    return

            continue

    def on_hightlight(self, study_uid, series_uid, on):
        for s, i in self._mgr.SELECTED_SLICES.items():
            dcm_info = s.get_dcm_info()
            if dcm_info and 'study_uid' in dcm_info and 'series_uid' in dcm_info:
                _study_uid = dcm_info['study_uid']
                _series_uid = dcm_info['series_uid']
                if study_uid == _study_uid and series_uid == _series_uid:
                    # get imgholder's titlebar and set highlight
                    _item = self.repeater_imgholder.itemAt(i)
                    if _item:
                        _item.childItems()[0].setProperty('highlight', on)

    def on_release_dummy_thumbnail(self):
        self._win.send_message.emit(['slice::release_dummy_thumbnail', None])

    def on_thumbnail_position_changed(self, global_mouse, img_url, mode):
        if not global_mouse:
            return
        _contained = self.is_contained(global_mouse)
        if not _contained:
            self._win.send_message.emit(['slice::set_dummy_thumbnail', [global_mouse, img_url, mode]])
        else:
            self._win.send_message.emit(['slice::release_dummy_thumbnail', None])

    def on_dropped_thumbnail_to_other_app(self, global_mouse, study_uid, series_uid=None):
        if not global_mouse:
            return
        _contained = self.is_contained(global_mouse)
        if not _contained:
            self._win.send_message.emit(['slice::send_to_other_app', [global_mouse, study_uid, series_uid]])

    def on_selected_study(self, selected_index):
        if selected_index is None or selected_index == -1:
            return
        _study_item = self.repeater_study.itemAt(selected_index)
        _study_uid = _study_item.getStudyUID()
        self.select_study(_study_uid)

    def select_study(self, _study_uid):

        # 1. clear thumbnail items
        self.topbar_thumbnail_item.clearThumbnail()

        # 2. re-generate the selected slices by study uid
        self._mgr.select_study(_study_uid)

        # 3. set vtk and info & set thumbnails & refresh items
        # set
        waiting_list = []
        for _s, _i in self._mgr.SELECTED_SLICES.items():
            # append layout_idx
            waiting_list.append(_i)
            # get imgholder and set slice
            _item = self.repeater_imgholder.itemAt(_i)
            if _item:
                _item.childItems()[1].set_vtk(_s)
                _item.childItems()[1].update()

            _patient_info = _s.get_patient_info()
            _dcm_info = _s.get_dcm_info()
            if _dcm_info is None or _patient_info is None:
                continue
            # refresh qml text items (patient id, name, age, sex ...)
            self.refresh_item(_i)
            self.append_study_series_model(_patient_info, _dcm_info['study_uid'], _dcm_info['series_uid'])
        # clear image holder
        layout_cnt = QQmlProperty.read(self.repeater_imgholder, 'count')
        for _i in range(layout_cnt):
            if _i in waiting_list:
                continue
            _item = self.repeater_imgholder.itemAt(_i)
            if _item:
                _item.childItems()[1].set_vtk(None)
                _item.childItems()[1].clear()
        waiting_list.clear()
        # set variable 'selected' to true
        _study_item = self.topbar_study_item.getItem(_study_uid)
        if _study_item:
            _study_item.setProperty('selected', True)

        # busy check
        self.busy_check()

        # garbage collect
        gc.collect()

    def on_selected_menu(self, name, selected):

        print("selected button :: ", self.sender().objectName(), name, selected)

        if name == "select":
            self.layout_item.setSelector(selected)
        elif name == "pan":
            pass
        elif name == "zoom":
            pass
        elif name == "fit":
            pass
        elif name == "windowing":
            pass
        elif name == "auto_windowing":
            pass
        elif name == 'reset_wwl':
            self._mgr.reset_wwl()
        elif name == 'reset_all':
            pass
        elif name == "key_image":
            pass
        elif name == "report":
            pass

        self._mgr.on_selected_menu(name, selected)
