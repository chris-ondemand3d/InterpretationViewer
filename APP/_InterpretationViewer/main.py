import os, sys
import shutil

from cyhub.cy_image_holder import CyQQuickView

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QObject, QUrl, QTimer, Qt, QEvent, pyqtSignal
from PyQt5.QtQml import QQmlProperty
from PyQt5.Qt  import QApplication, Qt, QScreen, QStyle
from PyQt5.QtGui import QCursor

import _qapp

import gc

from APP._InterpretationViewer.blocks.DBMWindow import DBMWindow
from APP._InterpretationViewer.blocks.DBMManager import DBMManager
from APP._InterpretationViewer.blocks.SliceViewWindow import SliceViewWindow
from APP._InterpretationViewer.blocks.SliceViewManager import SliceViewManager
from APP._InterpretationViewer.blocks.MPRWindow import MPRWindow
from APP._InterpretationViewer.blocks.MPRManager import MPRManager


_win_source = QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), './main.qml'))


def clear_tmp_directory():
    # clear tmp directory
    _tmp_path = os.path.join(os.path.abspath("."), "../_tmp/")
    if os.path.exists(_tmp_path):
        shutil.rmtree(_tmp_path)


class dbm_app(CyQQuickView):

    send_message = pyqtSignal(object)

    def __init__(self, dicom_web=None, *args, **kwds):
        super().__init__(*args, **kwds)
        self.setResizeMode(QQuickView.SizeRootObjectToView)

        self.dbm_mgr = DBMManager(_win=self, _dicom_web = dicom_web)
        self.dbm_win = DBMWindow(_win=self, _mgr=self.dbm_mgr)

    def eventFilter(self, obj, event):
        print("event filter (dbm_app):: ", obj, event)
        return super().eventFilter(obj, event)


class slice_app(CyQQuickView):

    send_message = pyqtSignal(object)
    sig_refresh_all = pyqtSignal()

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.setResizeMode(QQuickView.SizeRootObjectToView)
        self.setSource(_win_source)
        self.resize(1300, 650)
        # self.show(isMaximize=True)

        self.slice_mgr = SliceViewManager()
        self.slice_win = SliceViewWindow(_win=self, _mgr=self.slice_mgr)
        self.sig_refresh_all.connect(lambda: self.slice_mgr.on_refresh_all())

    def eventFilter(self, obj, event):
    #     # print("event filter (mpr_app):: ", obj, event)
    #     if event.type() == QEvent.HoverLeave:
    #         QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        return super().eventFilter(obj, event)

    def get_next_layout_id(self, force=False):
        return self.slice_win.get_next_layout_id(force)

    def init_vtk(self, _vtk_img, _wwl, _patient_info, study_uid, series_uid, next_id):

        dcm_info = {'study_uid': study_uid, 'series_uid': series_uid}   # TODO
        self.slice_win.appendThumbnail(_patient_info, study_uid, series_uid)
        self.slice_win.set_data_info_str(_patient_info, next_id)
        self.slice_mgr.init_vtk(_vtk_img, _wwl, dcm_info, next_id)

    def fullscreen(self, layout_idx, fullscreen_mode):
        self.slice_win.fullscreen(layout_idx, fullscreen_mode)

    def refresh_thumbnail_img(self):
        self.slice_win.refresh_thumbnail_img()

    def is_contained(self, global_mouse):
        return self.slice_win.is_contained(global_mouse)

    def set_dummy_thumbnail(self, global_pos, img_url):
        self.slice_win.set_dummy_thumbnail(global_pos, img_url)

    def release_dummy_thumbnail(self):
        self.slice_win.release_dummy_thumbnail()

    def insert_slice_obj(self, slice_obj, global_mouse=None):
        _id = None
        if global_mouse:
            _id = self.slice_win.get_layout_id(global_mouse)
        next_id = self.slice_mgr.insert_slice_obj(slice_obj, _id)

        if not self.slice_win.insert_slice_obj(slice_obj, next_id):
            return False
        self.slice_mgr.refresh_text_items(next_id)
        return True

    def remove_slice_obj(self, slice_obj):
        dcm_info = slice_obj.get_dcm_info()
        if not dcm_info:
            return False
        self.slice_win.on_close_view(dcm_info['study_uid'], dcm_info['series_uid'])
        return True


class mpr_app(CyQQuickView):

    sig_refresh_all = pyqtSignal()

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.setResizeMode(QQuickView.SizeRootObjectToView)
        self.setSource(_win_source)
        self.resize(1300, 650)
        # self.show(isMaximize=True)

        self.mpr_mgr = MPRManager()
        self.mpr_win = MPRWindow(_win=self, _mgr=self.mpr_mgr)
        self.sig_refresh_all.connect(lambda: self.mpr_mgr.on_refresh_all())

    def eventFilter(self, obj, event):
        # print("event filter (mpr_app):: ", obj, event)
        # if event.type() == QEvent.HoverLeave:
        #     QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        return super().eventFilter(obj, event)


def onClose(event):
    clear_tmp_directory()
    sys.exit()

def onMsg(msg):
    _msg, _params = msg

    if _msg == 'slice::init_vtk':
        _vtk_img, _wwl, _patient_info, _study_uid, _series_uid, _open_type = _params
        next_id = app_slice.get_next_layout_id()
        if next_id >= 0:
            app_slice.init_vtk(_vtk_img, _wwl, _patient_info, _study_uid, _series_uid, next_id)
        else:
            next_id = app_slice2.get_next_layout_id()
            if next_id >= 0:
                app_slice2.init_vtk(_vtk_img, _wwl, _patient_info, _study_uid, _series_uid, next_id)
            else:
                next_id = app_slice.get_next_layout_id(force=True)
                app_slice.init_vtk(_vtk_img, _wwl, _patient_info, _study_uid, _series_uid, next_id)

    elif _msg == 'slice::try_fullscreen_mode':
        _full_screen_mode = _params
        next_id_1 = app_slice.get_next_layout_id()
        img_cnt_1 = app_slice.slice_mgr.get_vtk_img_count()
        next_id_2 = app_slice2.get_next_layout_id()
        img_cnt_2 = app_slice2.slice_mgr.get_vtk_img_count()

        # if app1 is available
        if next_id_1 >= 0:
            # if any vtk img isn't initialized in app1, do fullscreen mode of app1
            if img_cnt_1 == 0:
                app_slice.fullscreen(next_id_1, _full_screen_mode)
            # else, do nothing
            else:
                return
        else:
            # if app2 is available
            if next_id_2 >= 0:
                # if any vtk img isn't initialized in app2, do fullscreen mode of app2
                if img_cnt_2 == 0:
                    app_slice2.fullscreen(next_id_2, _full_screen_mode)
                # else, do nothing
                else:
                    return

    elif _msg == 'slice::update_thumbnail_img':
        app_slice.refresh_thumbnail_img()
        app_slice2.refresh_thumbnail_img()

    elif _msg == 'slice::refresh_all':
        app_slice.sig_refresh_all.emit()
        app_slice2.sig_refresh_all.emit()

    elif _msg == 'slice::set_dummy_thumbnail':
        _global_pos, _img_url = _params
        if app_slice.is_contained(_global_pos):
            app_slice.set_dummy_thumbnail(_global_pos, _img_url)
        elif app_slice2.is_contained(_global_pos):
            app_slice2.set_dummy_thumbnail(_global_pos, _img_url)

    elif _msg == 'slice::release_dummy_thumbnail':
        app_slice.release_dummy_thumbnail()
        app_slice2.release_dummy_thumbnail()

    elif _msg == 'slice::send_to_other_app':
        _global_mouse, _study_uid, _series_uid = _params
        if app_slice.is_contained(_global_mouse):
            _slice_obj = app_slice2.slice_win.get_slice_obj(_study_uid, _series_uid)
            if not _slice_obj:
                return
            if app_slice.insert_slice_obj(_slice_obj, _global_mouse):
                app_slice2.remove_slice_obj(_slice_obj)
        elif app_slice2.is_contained(_global_mouse):
            _slice_obj = app_slice.slice_win.get_slice_obj(_study_uid, _series_uid)
            if not _slice_obj:
                return
            if app_slice2.insert_slice_obj(_slice_obj, _global_mouse):
                app_slice.remove_slice_obj(_slice_obj)

    # MPR
    elif _msg == 'mpr::init_vtk':
        app_mpr.mpr_mgr.init_vtk(_params)
        # app_mpr2.mpr_mgr.init_vtk(_params)
    elif _msg == 'mpr::clear_all_actors':
        app_mpr.mpr_mgr.clear_all_actors()
        app_mpr.mpr_mgr.on_refresh_all()
        # app_mpr2.mpr_mgr.clear_all_actors()
        # app_mpr2.mpr_mgr.on_refresh_all()
    elif _msg == 'mpr::refresh_all':
        app_mpr.sig_refresh_all.emit()
        # app_mpr2.sig_refresh_all.emit()

    # debug
    elif _msg == 'test_msg':
        print("This is test msg :: ", _params)


if __name__ == '__main__':

    # clear tmp directory
    clear_tmp_directory()

    app_dbm = dbm_app()
    app_dbm.closing.connect(onClose)
    app_dbm.send_message.connect(onMsg)
    app_mpr = mpr_app()
    app_mpr.closing.connect(onClose)
    app_slice = slice_app()
    app_slice.closing.connect(onClose)
    app_slice.send_message.connect(onMsg)
    app_slice2 = slice_app()
    app_slice2.closing.connect(onClose)
    app_slice2.send_message.connect(onMsg)

    # multiple monitor
    screens = _qapp.qapp.screens()
    if len(screens) == 3:
        screen1 = screens[2]
        screen2 = screens[1]
        app_dbm.setScreen(screen1)
        app_slice.setScreen(screen2)
        app_slice2.setScreen(screen2)
        # app_mpr.setScreen(screen2)

        titlebar_height = _qapp.qapp.style().pixelMetric(QStyle.PM_TitleBarHeight)
        w = screen2.geometry().width()
        h = screen2.availableGeometry().height() - titlebar_height
        mpr_sz = [int(w * 1 / 2), h]
        app_slice.resize(*mpr_sz)
        app_slice.setPosition(screen2.geometry().x(), screen2.geometry().y() + titlebar_height)
        app_slice2.resize(*mpr_sz)
        app_slice2.setPosition(screen2.geometry().x() + mpr_sz[0], screen2.geometry().y() + titlebar_height)
        # app_mpr.resize(*mpr_sz)
        # app_mpr.setPosition(screen2.geometry().x(), screen2.geometry().y() + titlebar_height)

        app_dbm.show(isMaximize=True)
        app_slice.show(isMaximize=False)
        app_slice2.show(isMaximize=False)
        # app_mpr.show(isMaximize=False)
    elif len(screens) == 2:
        screen1 = screens[0]
        screen2 = screens[1]
        app_dbm.setScreen(screen1)
        app_slice.setScreen(screen2)
        app_slice2.setScreen(screen2)
        # app_mpr.setScreen(screen2)

        titlebar_height = _qapp.qapp.style().pixelMetric(QStyle.PM_TitleBarHeight)
        w = screen2.geometry().width()
        h = screen2.availableGeometry().height() - titlebar_height
        mpr_sz = [int(w * 1 / 2), h]
        app_slice.resize(*mpr_sz)
        app_slice.setPosition(screen2.geometry().x(), screen2.geometry().y() + titlebar_height)
        app_slice2.resize(*mpr_sz)
        app_slice2.setPosition(screen2.geometry().x() + mpr_sz[0], screen2.geometry().y() + titlebar_height)
        # app_mpr.resize(*mpr_sz)
        # app_mpr.setPosition(screen2.geometry().x(), screen2.geometry().y() + titlebar_height)

        app_dbm.show(isMaximize=True)
        app_slice.show(isMaximize=False)
        app_slice2.show(isMaximize=False)
        # app_mpr.show(isMaximize=False)
    else:
        screen = screens[0]
        titlebar_height = _qapp.qapp.style().pixelMetric(QStyle.PM_TitleBarHeight)
        w = screen.size().width()
        # h = screen.size().height() - titlebar_height
        h = screen.availableGeometry().height() - titlebar_height
        app_sz = [int(w * 1 / 3), h]

        # mpr
        # app_dbm.resize(*dbm_sz)
        # app_mpr.resize(*mpr_sz)
        # app_dbm.setPosition(0, titlebar_height)
        # app_mpr.setPosition(dbm_sz[0], titlebar_height)
        # app_dbm.show(isMaximize=False)
        # app_mpr.show(isMaximize=False)

        # slice view
        # app_dbm.resize(app_sz[0], app_sz[1] * 2 / 3)
        app_dbm.resize(*app_sz)
        app_dbm.setPosition(0, titlebar_height)
        app_slice.resize(*app_sz)
        app_slice.setPosition(app_sz[0], titlebar_height)
        app_slice2.resize(*app_sz)
        app_slice2.setPosition(app_sz[0]*2, titlebar_height)
        app_dbm.show(isMaximize=False)
        app_slice.show(isMaximize=False)
        app_slice2.show(isMaximize=False)


    # Start Qt event loop.
    _qapp.exec_(None, False)
