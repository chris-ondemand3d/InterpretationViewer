import os, sys

from cyhub.cy_image_holder import CyQQuickView

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QObject, QUrl, QTimer, Qt
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

        repeater_imgholder = self._win.rootObject().findChild(QObject, 'repeater_imgholder_sliceview')
        cnt = QQmlProperty.read(repeater_imgholder, 'count')

        if not hasattr(self, '_mgr'):
            return

        self._mgr.init_slice(cnt)

        for i, s in enumerate(self._mgr.SLICES):
            item = repeater_imgholder.itemAt(i).childItems()[1]
            _w = QQmlProperty.read(item, 'width')
            _h = QQmlProperty.read(item, 'height')
            item.setHeight(1000)
            item.setWidth(1000)
            item.set_vtk(s)
            item.setHeight(_w)
            item.setWidth(_h)
            item.installEventFilter(self._win) # to grab mouse hover leave, add eventfilter

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
