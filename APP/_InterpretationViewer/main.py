import os, sys

from cyhub.cy_image_holder import CyQQuickView

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QObject, QUrl, QTimer, Qt, QEvent
from PyQt5.QtQml import QQmlProperty
from PyQt5.Qt  import QApplication, Qt, QScreen
from PyQt5.QtGui import QCursor

import _qapp

import gc

from APP._InterpretationViewer.blocks.MPRWindow import MPRWindow
from APP._InterpretationViewer.blocks.MPRManager import MPRManager


_win_source = QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), './main.qml'))
_dbm_source = QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), './layout/DBM_layout.qml'))


class mpr_app(CyQQuickView):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.setResizeMode(QQuickView.SizeRootObjectToView)
        self.setSource(_win_source)
        self.resize(1300, 650)
        # self.show(isMaximize=True)

        # TODO!!!
        # go to MPR
        self.mpr_mgr = MPRManager()
        self.mpr_win = MPRWindow(_win=self, _mgr=self.mpr_mgr)

    def eventFilter(self, obj, event):
        print("event filter (mpr_app):: ", obj, event)
        if event.type() == QEvent.HoverLeave:
            QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        return super().eventFilter(obj, event)


class dbm_app(CyQQuickView):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.setResizeMode(QQuickView.SizeRootObjectToView)
        self.setSource(_dbm_source)
        self.resize(1300, 650)
        # self.show(isMaximize=True)

    def eventFilter(self, obj, event):
        print("event filter (dbm_app):: ", obj, event)
        return super().eventFilter(obj, event)


def onClose(event):
    sys.exit()


if __name__ == '__main__':
    app_dbm = dbm_app()
    app_dbm.closing.connect(onClose)
    app_mpr = mpr_app()
    app_mpr.closing.connect(onClose)

    # multiple monitor
    screens = _qapp.qapp.screens()
    if len(screens) >= 2:
        screen1 = screens[0]
        screen2 = screens[1]
        app_dbm.setScreen(screen1)
        app_mpr.setScreen(screen2)
        app_dbm.show(isMaximize=True)
        app_mpr.show(isMaximize=True)
    else:
        screen = screens[0]
        w = screen.size().width()
        h = screen.size().height()
        dbm_sz = [int(w * 1 / 3), h]
        mpr_sz = [int(w * 2 / 3), h]
        app_dbm.resize(*dbm_sz)
        app_mpr.resize(*mpr_sz)
        app_dbm.setPosition(0, 0)
        app_mpr.setPosition(dbm_sz[0], 0)
        app_dbm.show(isMaximize=False)
        app_mpr.show(isMaximize=False)

    # Start Qt event loop.
    _qapp.exec_(None, False)
