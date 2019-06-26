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
from PyQt5.QtCore import QObject, QUrl, QTimer, Qt, pyqtSlot
from PyQt5.QtQml import QQmlProperty

# from cgal.cython import cy_cgal

import gc

from .MPR2DSlice import MPR2DSlice
from .DicomWeb import cyDicomWeb


from COMMON import WorkerThread


# DCM_PATH = "/Users/scott/Dicom/OD3DData/20180425/S0000000099/"
DCM_PATH = "/Users/scott/Dicom/1/"
DCM_INTERVAL = 1


class MPRManager(QObject):
    def __init__(self, *args, **kdws):
        super().__init__()

        self.coronal = None
        self.sagittal = None
        self.axial = None

        self.reset()
        self.initialize()

    def initialize(self):
        # TODO!!!
        self.vtk_img = self.read_dcm_test2()
        vol_center = self.vtk_img.GetCenter()

        p = vtk.vtkImageProperty()
        p.SetColorWindow(3000)
        p.SetColorLevel(1000)
        p.SetInterpolationTypeToLinear()

        # coronal
        self.coronal = MPR2DSlice('coronal')
        self.coronal.sig_update_slabplane.connect(self.on_update_slabplane)
        self.coronal.set_vtk_img(self.vtk_img)
        self.coronal.set_actor_property(p)
        # sagittal
        self.sagittal = MPR2DSlice('sagittal')
        self.sagittal.sig_update_slabplane.connect(self.on_update_slabplane)
        self.sagittal.set_vtk_img(self.vtk_img)
        self.sagittal.set_actor_property(p)
        # axial
        self.axial = MPR2DSlice('axial')
        self.axial.sig_update_slabplane.connect(self.on_update_slabplane)
        self.axial.set_vtk_img(self.vtk_img)
        self.axial.set_actor_property(p)

        # initialize dsi
        coronal_plane = self.coronal.get_plane()
        sagittal_plane = self.sagittal.get_plane()
        axial_plane = self.axial.get_plane()
        self.coronal.guide_line.update({'sagittal': sagittal_plane, 'axial': axial_plane, 'handle': vol_center})
        self.sagittal.guide_line.update({'coronal': coronal_plane, 'axial': axial_plane, 'handle': vol_center})
        self.axial.guide_line.update({'coronal': coronal_plane, 'sagittal': sagittal_plane, 'handle': vol_center})

    def reset(self):
        self.coronal = None
        self.sagittal = None
        self.axial = None

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

    def read_dcm_test2(self):
        dcm_reader = cyDicomWeb()
        dcm_reader.initialize()
        dcm_reader.sig_update_imgbuf.connect(self.on_update_imgbuf)
        dim = [dcm_reader.width, dcm_reader.height, dcm_reader.length]
        o = dcm_reader.origin
        s = [dcm_reader.spacing[0], dcm_reader.spacing[1], dcm_reader.thickness]

        vtk_img = vtk.vtkImageData()
        vtk_img.SetDimensions(dim)
        vtk_img.SetOrigin(o)
        vtk_img.SetSpacing(s)
        # # vtk_img.SetExtent(e)
        vtk_img.AllocateScalars(vtk.VTK_CHAR, 1)
        vtk_img.GetPointData().SetScalars(dsa.numpyTovtkDataArray(np.zeros(np.product(dim))))

        WorkerThread.start_worker(dcm_reader.requests_buf16, _finished_func=lambda: print("ALL DICOM Files had been loaded!! :)"))

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

    @pyqtSlot(object, object)
    def on_update_imgbuf(self, imgbuf, offset):
        d = self.vtk_img.GetDimensions()
        narray = numpy_support.vtk_to_numpy(self.vtk_img.GetPointData().GetScalars())
        narray = narray.reshape(d, order='F')
        narray[:, :, offset] = imgbuf.reshape(d[:2], order='F')

        self.vtk_img.Modified()
        for _attr in [getattr(self, i) for i in ['coronal', 'sagittal', 'axial']]:
            _attr.refresh()
