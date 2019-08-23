import os, sys
import shutil
import gc

from cyhub.cy_image_holder import CyQQuickView

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QObject, QUrl, QTimer, Qt, QEvent, pyqtSignal
from PyQt5.QtQml import QQmlProperty
from PyQt5.Qt  import QApplication, Qt, QScreen, QStyle
from PyQt5.QtGui import QCursor

import _qapp
from cyhub import is_available_memory

from APP._InterpretationViewer.blocks.DBMWindow import DBMWindow
from APP._InterpretationViewer.blocks.DBMManager import DBMManager
from APP._InterpretationViewer.blocks.SliceViewWindow import SliceViewWindow
from APP._InterpretationViewer.blocks.SliceViewManager import SliceViewManager
from APP._InterpretationViewer.blocks.MPRWindow import MPRWindow
from APP._InterpretationViewer.blocks.MPRManager import MPRManager


_win_source = QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), './main.qml'))


class DBMApp(CyQQuickView):
    """
    DBMApp
    """

    send_message = pyqtSignal(object)

    def __init__(self, dicom_web=None, *args, **kwds):
        super().__init__(*args, **kwds)
        self.setResizeMode(QQuickView.SizeRootObjectToView)

        app_name = "PanDok.V1ewer"
        win_name = "DBM(Database Manager)"
        title = app_name + ' - ' + win_name
        if 'app_index' in kwds:
            title = title + kwds['app_index']
        self.setTitle(title)

        self.dbm_mgr = DBMManager(_app=self, _dicom_web = dicom_web)
        self.dbm_win = DBMWindow(_app=self, _mgr=self.dbm_mgr)

        self.sig_msgbox = self.dbm_win.dbm_msg_box_item.sigMsg

    def eventFilter(self, obj, event):
        print("event filter (dbm_app):: ", obj, event)
        return super().eventFilter(obj, event)

    def release_downloader(self, study_uid, series_uid):
        self.dbm_mgr.release_dicom_web(study_uid, series_uid)

    def refresh_thumbnail_img(self):
        self.dbm_win.refresh_thumbnail_img()


class SliceApp(CyQQuickView):
    """
    SliceApp
    """

    send_message = pyqtSignal(object)
    sig_refresh_all = pyqtSignal()

    def __init__(self, *args, **kwds):
        super().__init__()
        self.setResizeMode(QQuickView.SizeRootObjectToView)
        self.setSource(_win_source)
        self.resize(1300, 650)
        # self.show(isMaximize=True)

        app_name = "PanDok.V1ewer"
        win_name = "Viewer"
        title = app_name + ' - ' + win_name
        if 'app_index' in kwds:
            title = title + str(kwds['app_index'])
        self.setTitle(title)

        self.slice_mgr = SliceViewManager()
        self.slice_win = SliceViewWindow(_app=self, _mgr=self.slice_mgr)
        self.sig_refresh_all.connect(lambda: self.slice_mgr.on_refresh_all())

    # def eventFilter(self, obj, event):
    # #     # print("event filter (mpr_app):: ", obj, event)
    # #     if event.type() == QEvent.HoverLeave:
    # #         QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
    #     return super().eventFilter(obj, event)

    def set_key_event(self, _key, _modifiers):
        self.slice_win.set_key_event(_key, _modifiers)

    def get_next_layout_id(self, force=False):
        return self.slice_win.get_next_layout_id(force)

    def get_next_layout_id2(self, _study_uid):
        return self.slice_win.get_next_layout_id2(_study_uid)

    def init_vtk(self, _vtk_img, patient_pos_ori, _wwl, _patient_info, study_uid, series_uid, next_id):
        self.slice_win.init_vtk(_vtk_img, patient_pos_ori, _wwl, _patient_info, study_uid, series_uid, next_id)
        self.slice_win.busy_check()

    def busy_check(self):
        self.slice_win.busy_check()

    def fullscreen(self, layout_idx, fullscreen_mode):
        self.slice_win.fullscreen(layout_idx, fullscreen_mode)

    def refresh_thumbnail_img(self):
        self.slice_win.refresh_thumbnail_img()

    def is_contained(self, global_mouse):
        return self.slice_win.is_contained(global_mouse)

    def set_dummy_thumbnail(self, global_pos, img_url, mode):
        self.slice_win.set_dummy_thumbnail(global_pos, img_url, mode)

    def release_dummy_thumbnail(self):
        self.slice_win.release_dummy_thumbnail()

    def insert_slice_obj(self, slice_obj, layout_id):

        # TODO
        # _id = None
        # if global_mouse:
        #     _id = self.slice_win.get_layout_id(global_mouse)

        if not self.slice_win.insert_slice_obj(slice_obj, layout_id):
            return False
        self.slice_win.refresh_item(layout_id)

        # NOTE Sometimes, inserted slice isn't shown. So, tried to fix it with the callback function.
        QTimer.singleShot(100, lambda: self.sig_refresh_all.emit())

        return True

    def remove_slice_obj(self, _study_uid, _series_uid):

        # TODO!!!!!!!!!! need to clean up source...

        # 1 close view
        self.slice_win.on_close_view(_study_uid, _series_uid)

        # 2 remove (without reset())
        if _study_uid in self.slice_mgr.ALL_SLICES:
            waiting_list = []
            _slices = self.slice_mgr.ALL_SLICES[_study_uid]
            if _series_uid is None:
                for _s in _slices.keys():
                    waiting_list.append(_s)
            else:
                for _s in _slices.keys():
                    _dcm_info = _s.get_dcm_info()
                    if _series_uid == _dcm_info['series_uid']:
                        waiting_list.append(_s)
                        break
            for _s in waiting_list:
                self.slice_mgr.ALL_SLICES[_study_uid].pop(_s)
            if len(self.slice_mgr.ALL_SLICES[_study_uid]) == 0:
                self.slice_mgr.ALL_SLICES.pop(_study_uid)
            waiting_list.clear()

        # refresh study thumbnail
        _series_item = self.slice_win.repeater_series.itemAt(0)
        if _series_item:
            _study_uid = _series_item.getStudyUID()
            _idx = int(self.slice_win.topbar_study_item.getIndex(_study_uid))
            self.slice_win.topbar_study_item.refreshToggleStatus(_idx)

        return True

    def move_selected_slice(self, value):
        self.slice_win.move_selected_slice(value)


class MPRApp(CyQQuickView):
    """
    MPRApp
    """

    sig_refresh_all = pyqtSignal()

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.setResizeMode(QQuickView.SizeRootObjectToView)
        self.setSource(_win_source)
        self.resize(1300, 650)
        # self.show(isMaximize=True)

        self.mpr_mgr = MPRManager()
        self.mpr_win = MPRWindow(_app=self, _mgr=self.mpr_mgr)
        self.sig_refresh_all.connect(lambda: self.mpr_mgr.on_refresh_all())

    # def eventFilter(self, obj, event):
    #     # print("event filter (mpr_app):: ", obj, event)
    #     # if event.type() == QEvent.HoverLeave:
    #     #     QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
    #     return super().eventFilter(obj, event)
