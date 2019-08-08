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

    sig_refresh_all = pyqtSignal()
    sig_change_slice_num = pyqtSignal(object, object)
    sig_change_wwl = pyqtSignal(object, object, object)

    sig_change_thickness = pyqtSignal(object, object)
    sig_change_filter = pyqtSignal(object, object)

    def __init__(self, *args, **kdws):
        super().__init__()

        self.SLICES = []
        self.dummy_slice = Slice()  # dummy to show empty vtk img

        self.reset()
        self.initialize()

    def initialize(self):
        pass

    def reset(self):
        for s in self.SLICES:
            s.reset()
            del s
        self.SLICES.clear()

    def init_slice(self, num):
        self.SLICES = []
        for i in range(num):
            slice = Slice()
            slice.sig_refresh_all.connect(self.on_refresh_all)
            slice.sig_change_slice_num.connect(self.on_change_slice_num)
            slice.sig_change_wwl.connect(self.on_change_wwl)
            self.SLICES.append(slice)
        self.sig_refresh_all.connect(self.on_refresh_all)

    def init_vtk(self, vtk_img, wwl, dcm_info, layout_idx):

        if wwl is None:
            wwl = [2000, 4000]

        p = vtk.vtkImageProperty()
        p.SetColorWindow(wwl[0])
        p.SetColorLevel(wwl[1])
        p.SetInterpolationTypeToLinear()
        self.SLICES[layout_idx].set_vtk_img(vtk_img)
        self.SLICES[layout_idx].set_dcm_info(dcm_info)
        self.SLICES[layout_idx].set_actor_property(p)

        # default
        slice_num = self.SLICES[layout_idx].get_slice_num()
        th = self.SLICES[layout_idx].get_thickness()
        self.sig_change_slice_num.emit(slice_num, layout_idx)
        if vtk_img.GetDimensions()[2] > 1:
            self.sig_change_thickness.emit(th, layout_idx)
        intial_filter = None
        self.sig_change_filter.emit(intial_filter, layout_idx)
        self.sig_change_wwl.emit(wwl[0], wwl[1], layout_idx)

    def clear_all_actors(self):
        for s in self.SLICES:
            s.clear_all_actors()

    def refresh_text_items(self, layout_idx):
        _slice = self.SLICES[layout_idx]
        _vtk_img = _slice.get_vtk_img()
        # if _vtk_img is None:
        #     return
        slice_num = _slice.get_slice_num()
        self.sig_change_slice_num.emit(slice_num, layout_idx)
        th = _slice.get_thickness() if _vtk_img.GetDimensions()[2] > 1 else -1
        self.sig_change_thickness.emit(th, layout_idx)
        intial_filter = _slice.get_image_filter_type()
        self.sig_change_filter.emit(intial_filter, layout_idx)
        wwl = _slice.get_windowing()
        self.sig_change_wwl.emit(wwl[0], wwl[1], layout_idx)

    def get_next_layout_id(self, limit=None):
        for i, s in enumerate(self.SLICES[:limit] if limit else self.SLICES):
            if s.vtk_img is None:
                return i
        return -1

    def get_vtk_img_count(self):
        return len(list(filter(lambda x: x.vtk_img is not None, self.SLICES)))

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
        for slice in self.SLICES:
            slice.refresh()

    @pyqtSlot(object)
    def on_change_slice_num(self, slice_num):
        self.sig_change_slice_num.emit(slice_num, self.SLICES.index(self.sender()))

    @pyqtSlot(object, object)
    def on_change_wwl(self, ww, wl):
        self.sig_change_wwl.emit(ww, wl, self.SLICES.index(self.sender()))
