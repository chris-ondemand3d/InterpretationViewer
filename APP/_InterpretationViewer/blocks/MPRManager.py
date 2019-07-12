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

from .MPR2DSlice import MPR2DSlice
from .DicomWeb import cyDicomWeb, HEADERS1, HEADERS2, requests_buf16

from COMMON import WorkerThread

import multiprocessing
from multiprocessing.managers import BaseManager


# DCM_PATH = "/Users/scott/Dicom/OD3DData/20180425/S0000000099/"
# DCM_PATH = "/Users/scott/Dicom/1/"
# DCM_PATH = "/Users/scott/Dicom/uncompressed/S0000000007/"
DCM_INTERVAL = 1


class MPRManager(QObject):

    sig_refresh_all = pyqtSignal()

    def __init__(self, *args, **kdws):
        super().__init__()

        self.coronal = None
        self.sagittal = None
        self.axial = None

        self.reset()
        self.initialize()

    def initialize(self):
        # coronal
        self.coronal = MPR2DSlice('coronal')
        self.coronal.sig_update_slabplane.connect(self.on_update_slabplane)
        self.coronal.sig_refresh_all.connect(self.on_refresh_all)
        # sagittal
        self.sagittal = MPR2DSlice('sagittal')
        self.sagittal.sig_update_slabplane.connect(self.on_update_slabplane)
        self.sagittal.sig_refresh_all.connect(self.on_refresh_all)
        # axial
        self.axial = MPR2DSlice('axial')
        self.axial.sig_update_slabplane.connect(self.on_update_slabplane)
        self.axial.sig_refresh_all.connect(self.on_refresh_all)

        self.sig_refresh_all.connect(self.on_refresh_all)

    def reset(self):
        if self.coronal:
            self.coronal.reset()
            self.coronal = None

        if self.sagittal:
            self.sagittal.reset()
            self.sagittal = None

        if self.axial:
            self.axial.reset()
            self.axial = None

        if hasattr(self, 'vtk_img'):
            del self.vtk_img

    def init_vtk(self, vtk_img):
        if hasattr(self, 'vtk_img'):
            self.vtk_img.ReleaseData()
            del self.vtk_img
            gc.collect()

        self.clear_all_actors()

        self.vtk_img = vtk_img
        vol_center = self.vtk_img.GetCenter()
        p = vtk.vtkImageProperty()
        p.SetColorWindow(3000)
        p.SetColorLevel(1000)
        p.SetInterpolationTypeToLinear()

        # set vtk_img
        self.coronal.set_vtk_img(self.vtk_img)
        self.coronal.set_actor_property(p)
        self.sagittal.set_vtk_img(self.vtk_img)
        self.sagittal.set_actor_property(p)
        self.axial.set_vtk_img(self.vtk_img)
        self.axial.set_actor_property(p)

        # initialize dsi
        coronal_plane = self.coronal.get_plane()
        sagittal_plane = self.sagittal.get_plane()
        axial_plane = self.axial.get_plane()
        self.coronal.guide_line.update({'sagittal': sagittal_plane, 'axial': axial_plane, 'handle': vol_center})
        self.sagittal.guide_line.update({'coronal': coronal_plane, 'axial': axial_plane, 'handle': vol_center})
        self.axial.guide_line.update({'coronal': coronal_plane, 'sagittal': sagittal_plane, 'handle': vol_center})

    def clear_all_actors(self):
        self.coronal.clear_all_actors()
        self.sagittal.clear_all_actors()
        self.axial.clear_all_actors()

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

    def get_vtk_img(self):
        if hasattr(self, 'vtk_img'):
            return self.vtk_img
        else:
            return None

    @pyqtSlot(object)
    def on_update_slabplane(self, slabplanes):
        for _attr in [getattr(self, i) for i in ['coronal', 'sagittal', 'axial']]:
            if _attr is None or _attr is self.sender():
                continue
            _attr.update_slabplane(slabplanes)
            _attr.refresh()

    @pyqtSlot(object, object, object)
    def on_update_imgbuf(self, imgbuf, offset, refresh):
        # self.vtk_img_narray[:, :, offset] = imgbuf.reshape(self.vtk_dims[:2], order='F')
        if refresh:
            # self.vtk_img.Modified()
            for _attr in [getattr(self, i) for i in ['coronal', 'sagittal', 'axial']]:
                _attr.refresh()

    @pyqtSlot()
    def on_refresh_all(self):
        for _attr in [getattr(self, i) for i in ['coronal', 'sagittal', 'axial']]:
            _attr.refresh()
