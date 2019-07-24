import os, sys

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
        # print("event filter (mpr_app):: ", obj, event)
        if event.type() == QEvent.HoverLeave:
            QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        return super().eventFilter(obj, event)


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
        if event.type() == QEvent.HoverLeave:
            QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        return super().eventFilter(obj, event)


def onClose(event):
    sys.exit()

def onMsg(msg):
    _msg, _params = msg

    if _msg == 'slice::init_vtk':
        app_slice.slice_mgr.init_vtk(*_params)
    elif _msg == 'slice::refresh_all':
        app_slice.sig_refresh_all.emit()
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


if __name__ == '__main__':

    app_dbm = dbm_app()
    app_dbm.closing.connect(onClose)
    app_dbm.send_message.connect(onMsg)
    app_mpr = mpr_app()
    app_mpr.closing.connect(onClose)
    app_slice = slice_app()
    app_slice.closing.connect(onClose)

    # multiple monitor
    screens = _qapp.qapp.screens()
    if len(screens) == 3:
        pass
    elif len(screens) == 2:
        screen1 = screens[0]
        screen2 = screens[1]
        app_dbm.setScreen(screen1)
        # app_mpr.setScreen(screen2)
        app_slice.setScreen(screen2)

        titlebar_height = _qapp.qapp.style().pixelMetric(QStyle.PM_TitleBarHeight)
        w = screen2.geometry().width()
        h = screen2.availableGeometry().height() - titlebar_height
        mpr_sz = [int(w * 1 / 2), h]
        # app_mpr.resize(*mpr_sz)
        # app_mpr.setPosition(screen2.geometry().x(), screen2.geometry().y() + titlebar_height)
        app_slice.resize(*mpr_sz)
        app_slice.setPosition(screen2.geometry().x() + mpr_sz[0], screen2.geometry().y() + titlebar_height)

        app_dbm.show(isMaximize=True)
        # app_mpr.show(isMaximize=False)
        app_slice.show(isMaximize=False)
    else:
        screen = screens[0]
        titlebar_height = _qapp.qapp.style().pixelMetric(QStyle.PM_TitleBarHeight)
        w = screen.size().width()
        # h = screen.size().height() - titlebar_height
        h = screen.availableGeometry().height() - titlebar_height
        dbm_sz = [int(w * 1 / 2), h]
        mpr_sz = [int(w * 1 / 2), h]
        app_dbm.resize(*dbm_sz)
        app_mpr.resize(*mpr_sz)
        app_dbm.setPosition(0, titlebar_height)
        app_mpr.setPosition(dbm_sz[0], titlebar_height)
        app_dbm.show(isMaximize=False)
        app_mpr.show(isMaximize=False)

    # Start Qt event loop.
    _qapp.exec_(None, False)
