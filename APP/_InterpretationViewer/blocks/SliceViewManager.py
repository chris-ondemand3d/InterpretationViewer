import os, sys

import numpy as np
import vtk
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
import SimpleITK as sitk
import cyCafe

from cyhub.cy_image_holder import CyQQuickView
from cyhub.cy_vtk import Vtk_image_holder

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QObject, QUrl, QTimer, Qt, pyqtSignal, pyqtSlot, QThread
from PyQt5.QtQml import QQmlProperty

# from cgal.cython import cy_cgal

import gc
try:
    import resource
    print_memory = lambda: print('Memory usage : % 2.2f MB' %
                                 round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0, 1))
except ImportError:
    print_memory = lambda: print()

from .Slice import Slice

import multiprocessing
from multiprocessing.managers import BaseManager


# DCM_PATH = "/Users/scott/Dicom/OD3DData/20180425/S0000000099/"
# DCM_PATH = "/Users/scott/Dicom/1/"
# DCM_PATH = "/Users/scott/Dicom/uncompressed/S0000000007/"
DCM_INTERVAL = 1


class SliceViewManager(QObject):

    sig_changed_slice = pyqtSignal(object, object)
    sig_change_slice_num = pyqtSignal(object, object)
    sig_change_wwl = pyqtSignal(object, object, object)

    sig_change_thickness = pyqtSignal(object, object)
    sig_change_filter = pyqtSignal(object, object)

    def __init__(self, *args, **kdws):
        super().__init__()

        self.SELECTED_SLICES = {}       # selected slice list to visualize
        self.ALL_SLICES = {}            # all slices

        self.reset()
        self.initialize()

        # TODO
        self.mode_cross_link = False

    def __del__(self):
        pass

    def initialize(self):
        pass

    def reset(self):
        for uid, s in self.SELECTED_SLICES.items():
            s.reset()
            del s
        self.SELECTED_SLICES.clear()
        for uid, s in self.ALL_SLICES.items():
            s.reset()
            del s
        self.ALL_SLICES.clear()

        self.mode_cross_link = False

    def create_new_slice(self):
        _slice = Slice()
        _slice.sig_changed_slice.connect(self.on_changed_slice)  # TODO
        _slice.sig_change_slice_num.connect(self.on_change_slice_num)
        _slice.sig_change_wwl.connect(self.on_change_wwl)
        _slice.resize(2000, 2000)
        return _slice

    def init_vtk(self, vtk_img, patient_pos_ori, wwl, layout_idx):

        if wwl is None:
            wwl = [2000, 4000]

        for _s, _i in self.SELECTED_SLICES.items():
            _s.initial_wwl = wwl
            if _i == layout_idx:
                p = vtk.vtkImageProperty()
                p.SetColorWindow(wwl[0])
                p.SetColorLevel(wwl[1])
                p.SetInterpolationTypeToLinear()
                _s.set_vtk_img(vtk_img, patient_pos_ori)
                _s.set_actor_property(p)
                # default
                slice_num = _s.get_slice_num()
                th = _s.get_thickness()
                self.sig_change_slice_num.emit(slice_num, layout_idx)
                if vtk_img.GetDimensions()[2] > 1:
                    self.sig_change_thickness.emit(th, layout_idx)
                initial_filter = None
                self.sig_change_filter.emit(initial_filter, layout_idx)
                self.sig_change_wwl.emit(wwl[0], wwl[1], layout_idx)
                return True
        return False

    def insert_slice_obj(self, slice_obj, _target_id=None):
        # must insert to self.ALL_SLICES
        _dcm_info = slice_obj.get_dcm_info()
        if _dcm_info is None:
            return -1
        _study_uid = _dcm_info['study_uid']
        _series_uid = _dcm_info['series_uid']
        if _study_uid in self.ALL_SLICES:
            self.SELECTED_SLICES = self.ALL_SLICES[_study_uid]
        else:
            self.ALL_SLICES[_study_uid] = {}
            self.SELECTED_SLICES = self.ALL_SLICES[_study_uid]

        _keys = list(self.SELECTED_SLICES.keys())
        _values = list(self.SELECTED_SLICES.values())
        if not _target_id is None and _target_id != -1:
            _target_obj = None
            if _target_id in _values:
                _target_obj = _keys[_values.index(_target_id)]
            self.SELECTED_SLICES[slice_obj] = _target_id
            if not _target_obj is None and _target_obj.get_vtk_img():
                self.SELECTED_SLICES[_target_obj] = max(_values) + 1
        else:
            _values = list(self.SELECTED_SLICES.values())
            _target_id = 0 if len(_values) == 0 else max(_values) + 1
            self.SELECTED_SLICES[slice_obj] = _target_id

        # reconnect sig/slot
        """
        NOTE should connect sig/slot again, since sloce_obj may have been delivered by the other app.
        """
        slice_obj.sig_changed_slice.disconnect()
        slice_obj.sig_change_slice_num.disconnect()
        slice_obj.sig_change_wwl.disconnect()
        slice_obj.sig_changed_slice.connect(self.on_changed_slice)
        slice_obj.sig_change_slice_num.connect(self.on_change_slice_num)
        slice_obj.sig_change_wwl.connect(self.on_change_wwl)
        return _target_id

    def refresh_status_item(self, layout_idx):
        if not layout_idx in list(self.SELECTED_SLICES.values()):
            return
        _slice = list(self.SELECTED_SLICES.keys())[list(self.SELECTED_SLICES.values()).index(layout_idx)]
        _vtk_img = _slice.get_vtk_img()
        # if _vtk_img is None:
        #     return
        slice_num = _slice.get_slice_num()
        self.sig_change_slice_num.emit(slice_num, layout_idx)
        th = _slice.get_thickness() if _vtk_img.GetDimensions()[2] > 1 else -1
        self.sig_change_thickness.emit(th, layout_idx)
        _filter = _slice.get_image_filter_type()
        self.sig_change_filter.emit(_filter, layout_idx)
        wwl = _slice.get_windowing()
        self.sig_change_wwl.emit(wwl[0], wwl[1], layout_idx)

    # will be deprecated.
    def get_next_layout_id(self, limit=None):
        for i, s in enumerate(self.SLICES[:limit] if limit else self.SLICES):
            if s.vtk_img is None:
                return i
        return -1

    def get_next_layout_id2(self, _study_uid):
        if _study_uid in self.ALL_SLICES and len(self.ALL_SLICES[_study_uid]) > 0:
            _slices = self.ALL_SLICES[_study_uid]
            _sorted_keys = sorted(_slices, key=lambda x: _slices[x])
            for _i in range(len(_sorted_keys)-1):
                _idx0 = _slices[_sorted_keys[_i]]
                _idx1 = _slices[_sorted_keys[_i+1]]
                if _idx1 - _idx0 > 1:
                    return _idx0 + 1
            _new_idx = _slices[_sorted_keys[-1]] + 1
            return _new_idx
        else:
            _new_idx = 0
            return _new_idx

    def get_slice_obj(self, study_uid, series_uid):
        for _slice, _layout_id in self.ALL_SLICES[study_uid].items():
            _dcm_info = _slice.get_dcm_info()
            if _slice.get_vtk_img() is None:
                continue
            _study_uid = _dcm_info['study_uid']
            _series_uid = _dcm_info['series_uid']
            if study_uid == _study_uid and series_uid == _series_uid:
                return _slice
        return None

    def get_slice_objs(self, study_uid):
        _slices = []
        _indicces = []
        for _slice, _layout_id in self.ALL_SLICES[study_uid].items():
            _dcm_info = _slice.get_dcm_info()
            if _slice.get_vtk_img() is None:
                continue
            _slices.append(_slice)
            _indicces.append(_layout_id)
        return _slices, _indicces

    def select_study(self, study_uid):
        if study_uid in self.ALL_SLICES:
            self.SELECTED_SLICES = self.ALL_SLICES[study_uid]
            return True
        return False

    def move_selected_slice(self, value, indices):
        _keys = list(self.SELECTED_SLICES.keys())
        _values = list(self.SELECTED_SLICES.values())
        for _i in indices:
            try:
                _s = _keys[_values.index(_i)]
            except IndexError:
                continue
            _s.move_slice(value)
            _s.refresh()

    def reset_wwl(self):
        for _s, _i in self.SELECTED_SLICES.items():
            if hasattr(_s, 'initial_wwl'):
                _wwl = _s.initial_wwl
                _s.set_windowing(*_wwl)
                self.sig_change_wwl.emit(_wwl[0], _wwl[1], _i)
            _s.refresh()

    def fit_screen_all(self):
        for _s in self.SELECTED_SLICES.keys():
            _s.fit_img_to_screen()
            _s.refresh()

    def calc_cross_link(self, slice_num, layout_id):
        if not self.mode_cross_link:
            for _s, _i in self.SELECTED_SLICES.items():
                _s.cross_link_test(None)
            return
        _keys = list(self.SELECTED_SLICES.keys())
        _values = list(self.SELECTED_SLICES.values())
        _cur_slice = _keys[_values.index(layout_id)]
        try:
            _senders_pos_ori = _cur_slice.patient_pos_ori[slice_num]
        except IndexError:
            return
        for _s, _i in self.SELECTED_SLICES.items():
            if _i == layout_id:
                _s.cross_link_test(None)
                continue
            _s.cross_link_test(_senders_pos_ori)

    def read_dcm_test(self):
        # # DCM Read
        # f = open(dcm[0], 'r')
        # files = f.read()
        # files = eval(files)
        # f.close()
        # dcm_reader = cyCafe.cyDicomReader()
        #
        # # for f in files[len(files)//2:-1:DCM_INTERVAL]:
        # for f in files[::DCM_INTERVAL]:
        #     dcm_reader.read_next(f)
        # dcm_reader.generate_vtk_img()
        # vtk_img = dcm_reader.get_vtk_img()

        dcm_reader = cyCafe.cyDicomReader()
        dcm_reader.read_dicom(DCM_PATH)
        vtk_img = dcm_reader.get_vtk_img()
        return vtk_img

    @pyqtSlot()
    def on_refresh_all(self):
        for s in self.SELECTED_SLICES.keys():
            s.refresh()

    # TODO
    @pyqtSlot(object)
    def on_changed_slice(self, value):
        self.sig_changed_slice.emit(value, self.SELECTED_SLICES[self.sender()])

    @pyqtSlot(object)
    def on_change_slice_num(self, slice_num):
        if self.sender() in self.SELECTED_SLICES:
            self.sig_change_slice_num.emit(slice_num, self.SELECTED_SLICES[self.sender()])

    @pyqtSlot(object, object)
    def on_change_wwl(self, ww, wl):
        if self.sender() in self.SELECTED_SLICES:
            self.sig_change_wwl.emit(ww, wl, self.SELECTED_SLICES[self.sender()])

    def on_selected_menu(self, name, selected):

        if name == "select":
            _mode = 'none' if selected is True else 'none'
            for _s in self.SELECTED_SLICES.keys():
                _s.set_interactor_mode(_mode)
        elif name == "pan":
            _mode = 'pan' if selected is True else 'none'
            for _s in self.SELECTED_SLICES.keys():
                _s.set_interactor_mode(_mode)
        elif name == "zoom":
            _mode = 'zoom' if selected is True else 'none'
            for _s in self.SELECTED_SLICES.keys():
                _s.set_interactor_mode(_mode)
        elif name == "fit":
            self.fit_screen_all()
        elif name == "windowing":
            _mode = 'windowing' if selected is True else 'none'
            for _s in self.SELECTED_SLICES.keys():
                _s.set_interactor_mode(_mode)
        elif name == "auto_windowing":
            pass
        elif name == "key_image":
            pass
        elif name == "report":
            pass
        elif name == "cross_link":
            self.mode_cross_link = selected
            if selected is False:
                self.calc_cross_link(None, None)
