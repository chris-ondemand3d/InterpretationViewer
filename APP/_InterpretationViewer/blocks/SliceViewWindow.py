import os, sys

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

        self.layout_item = self._win.rootObject().findChild(QObject, 'sliceview_mxn_layout')
        self.repeater_imgholder = self._win.rootObject().findChild(QObject, 'repeater_imgholder_sliceview')
        cnt = QQmlProperty.read(self.repeater_imgholder, 'count')

        if not hasattr(self, '_mgr'):
            return

        # initialize sig/slot
        self._mgr.init_slice(cnt)
        self._mgr.sig_change_slice_num.connect(self.on_change_slice_num)

        for i, s in enumerate(self._mgr.SLICES):
            item = self.repeater_imgholder.itemAt(i).childItems()[1]
            _w = QQmlProperty.read(item, 'width')
            _h = QQmlProperty.read(item, 'height')
            item.setHeight(2000)
            item.setWidth(2000)
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

    def get_next_layout_id(self):
        # get next available id
        next_id = self._mgr.get_next_layout_id()

        if next_id == -1:
            return next_id

        # get fullscreen status
        F = [QQmlProperty.read(self.repeater_imgholder.itemAt(i).childItems()[1], 'fullscreenTrigger')
             for i, s in enumerate(self._mgr.SLICES)]
        F_IDX = [i for i, elem in enumerate(F) if elem is True]
        # get vtk image init status
        I = [s.vtk_img for i, s in enumerate(self._mgr.SLICES)]

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

    def set_data_info_str(self, patient_info, layout_id):
        _s = self.repeater_imgholder.itemAt(layout_id).childItems()[1]
        _obj = _s.findChild(QObject, 'col_sv_patient_info')
        self.layout_item.setPatientInfo(_obj, patient_info['id'], patient_info['name'],
                                        patient_info['age'], patient_info['sex'],
                                        patient_info['date'], patient_info['series_id'])

    @pyqtSlot(object, object)
    def on_change_slice_num(self, slice_num, layout_id):
        _obj = self.repeater_imgholder.itemAt(layout_id).childItems()[1]
        self.layout_item.setSliceNumber(_obj, slice_num)
