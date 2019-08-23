import os, sys

from cyhub.cy_image_holder import CyQQuickView

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QObject, QUrl, QTimer, Qt
from PyQt5.QtQml import QQmlProperty


class MPRWindow(QObject):
    def __init__(self, _app, _mgr, *args, **kdws):
        super().__init__()
        self._app = _app
        self._mgr = _mgr

        # self.reset()
        self.initialize()

    def initialize(self):
        # win init
        _win_source = QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), '../layout/MPR_layout.qml'))
        self._app.setSource(_win_source)

        coronal_item = self._app.rootObject().findChild(QObject, 'vtk_coronal')
        sagittal_item = self._app.rootObject().findChild(QObject, 'vtk_sagittal')
        axial_item = self._app.rootObject().findChild(QObject, 'vtk_axial')
        self.items = {'coronal': coronal_item, 'sagittal': sagittal_item, 'axial': axial_item}

        # set vtk and init size
        for k, v in self.items.items():
            _slice = getattr(self._mgr, k)
            if _slice:
                _item = v
                _w = QQmlProperty.read(_item, 'width')
                _h = QQmlProperty.read(_item, 'height')
                _item.setHeight(1000)
                _item.setWidth(1000)
                _item.set_vtk(_slice)
                _item.setHeight(_w)
                _item.setWidth(_h)
                # _item.installEventFilter(self._app) # to grab mouse hover leave, add eventfilter

    def reset(self):
        #TODO!!!
        # win reset
        # self._app.reset()

        def _remove(X):
            if type(X) is not dict:
                for o in X:
                    del o
            X.clear()

        if hasattr(self, 'items'):
            _remove(self.items)
