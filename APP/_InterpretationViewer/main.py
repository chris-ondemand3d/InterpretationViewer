import os, sys
import shutil
import gc

import _qapp

from PyQt5.Qt  import QStyle

from APP._InterpretationViewer import App
from APP._InterpretationViewer import CallbackMessage


def clear_tmp_directory():
    # clear tmp directory
    _tmp_path = os.path.join(os.path.abspath("."), "../_tmp/")
    if os.path.exists(_tmp_path):
        shutil.rmtree(_tmp_path)


def make_tmp_directory():
    _tmp_path = os.path.join(os.path.abspath("."), "../_tmp/")
    if not os.path.exists(_tmp_path):
        os.mkdir(_tmp_path)


def onClose(event):
    clear_tmp_directory()
    sys.exit()


if __name__ == '__main__':

    # clear and make tmp directory
    clear_tmp_directory()
    make_tmp_directory()

    # create and register
    app_dbm = App.DBMApp()
    app_slice = App.SliceApp(app_index=1)
    app_slice2 = App.SliceApp(app_index=2)
    # app_mpr = App.MPRApp()
    CallbackMessage.register_global_attribute({'app_dbm': app_dbm
                                               ,'app_slice': app_slice
                                               ,'app_slice2': app_slice2
                                               # ,'app_mpr': app_mpr
                                               })

    app_dbm.closing.connect(onClose)
    app_dbm.send_message.connect(CallbackMessage.onMessage)
    # app_mpr.closing.connect(onClose)
    app_slice.closing.connect(onClose)
    app_slice.send_message.connect(CallbackMessage.onMessage)
    app_slice2.closing.connect(onClose)
    app_slice2.send_message.connect(CallbackMessage.onMessage)

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
        app_dbm.resize(app_sz[0], app_sz[1] * 2 / 3)
        # app_dbm.resize(*app_sz)
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
