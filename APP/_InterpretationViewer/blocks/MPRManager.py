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

from .MPR2DSlice import MPR2DSlice
from .DicomWeb import cyDicomWeb, HEADERS1, HEADERS2, requests_buf16

from COMMON import WorkerThread

import multiprocessing
from multiprocessing.managers import BaseManager


# DCM_PATH = "/Users/scott/Dicom/OD3DData/20180425/S0000000099/"
# DCM_PATH = "/Users/scott/Dicom/1/"
DCM_PATH = "/Users/scott/Dicom/uncompressed/S0000000007/"
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
        # TODO!!!
        self.vtk_img = self.read_dcm_test3()
        vol_center = self.vtk_img.GetCenter()

        p = vtk.vtkImageProperty()
        p.SetColorWindow(3000)
        p.SetColorLevel(1000)
        p.SetInterpolationTypeToLinear()

        # coronal
        self.coronal = MPR2DSlice('coronal')
        self.coronal.sig_update_slabplane.connect(self.on_update_slabplane)
        self.coronal.sig_refresh_all.connect(self.on_refresh_all)
        self.coronal.set_vtk_img(self.vtk_img)
        self.coronal.set_actor_property(p)
        # sagittal
        self.sagittal = MPR2DSlice('sagittal')
        self.sagittal.sig_update_slabplane.connect(self.on_update_slabplane)
        self.sagittal.sig_refresh_all.connect(self.on_refresh_all)
        self.sagittal.set_vtk_img(self.vtk_img)
        self.sagittal.set_actor_property(p)
        # axial
        self.axial = MPR2DSlice('axial')
        self.axial.sig_update_slabplane.connect(self.on_update_slabplane)
        self.axial.sig_refresh_all.connect(self.on_refresh_all)
        self.axial.set_vtk_img(self.vtk_img)
        self.axial.set_actor_property(p)

        # initialize dsi
        coronal_plane = self.coronal.get_plane()
        sagittal_plane = self.sagittal.get_plane()
        axial_plane = self.axial.get_plane()
        self.coronal.guide_line.update({'sagittal': sagittal_plane, 'axial': axial_plane, 'handle': vol_center})
        self.sagittal.guide_line.update({'coronal': coronal_plane, 'axial': axial_plane, 'handle': vol_center})
        self.axial.guide_line.update({'coronal': coronal_plane, 'sagittal': sagittal_plane, 'handle': vol_center})

        self.sig_refresh_all.connect(self.on_refresh_all)

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
        dim = dcm_reader.get_dimensions()
        o = dcm_reader.get_origin()
        s = [*dcm_reader.get_spacing(), dcm_reader.get_thickness()]

        vtk_img = vtk.vtkImageData()
        vtk_img.SetDimensions(dim)
        vtk_img.SetOrigin(o)
        vtk_img.SetSpacing(s)
        # # vtk_img.SetExtent(e)
        vtk_img.AllocateScalars(vtk.VTK_CHAR, 1)
        buf = np.zeros(np.product(dim))
        buf.fill(-1000)
        vtk_img.GetPointData().SetScalars(dsa.numpyTovtkDataArray(buf))

        self.vtk_dims = dim
        self.vtk_img_narray = buf.reshape(dim, order='F')

        # Thread function
        def _do(_mode):
            instance_uids = dcm_reader.get_instance_uids()
            num_of_img = len(instance_uids)

            if _mode == 'upper':
                b, e = num_of_img // 2, num_of_img
                uids = instance_uids[b:e]
                def _get_index(x):
                    return x + b
            elif _mode == 'lower':
                b, e = 0, num_of_img // 2
                uids = list(reversed(instance_uids[b:e]))
                def _get_index(x):
                    return e - x - 1
            else:
                b, e = 0, num_of_img
                uids = instance_uids
                def _get_index(x):
                    return x

            for i, uid in enumerate(uids):
                i = _get_index(i)
                new_frame = dcm_reader.requests_buf16((uid, 0))
                self.vtk_img_narray[:, :, i] = new_frame[0].reshape(dim[:2], order='F')
                vtk_img.Modified()
                self.sig_refresh_all.emit()

        # upper
        WorkerThread.start_worker2(_do, 'upper',
                                   _finished_func=lambda: print("DICOM Files(Upper) had been loaded!! :)"))
        # lower
        WorkerThread.start_worker(_do, 'lower',
                                  _finished_func=lambda: print("DICOM Files(Lower) had been loaded!! :)"))

        return vtk_img

    def read_dcm_test3(self):
        dcm_reader = cyDicomWeb()
        dcm_reader.initialize()
        dim = dcm_reader.get_dimensions()
        o = dcm_reader.get_origin()
        s = [*dcm_reader.get_spacing(), dcm_reader.get_thickness()]

        vtk_img = vtk.vtkImageData()
        vtk_img.SetDimensions(dim)
        vtk_img.SetOrigin(o)
        vtk_img.SetSpacing(s)
        # # vtk_img.SetExtent(e)
        vtk_img.AllocateScalars(vtk.VTK_CHAR, 1)
        buf = np.zeros(np.product(dim))
        buf.fill(-1000)
        vtk_img.GetPointData().SetScalars(dsa.numpyTovtkDataArray(buf))

        self.vtk_dims = dim
        self.vtk_img_narray = buf.reshape(dim, order='F')

        url = "%s/%s/studies/%s/series/%s/" % (dcm_reader.host_url, dcm_reader.wadors_prefix,
                                               dcm_reader.study_uid, dcm_reader.series_uid)
        header = HEADERS2
        rescale_params = dcm_reader.rescale_slope, dcm_reader.rescale_intercept

        # Thread function
        def _do(_mode):
            instance_uids = dcm_reader.get_instance_uids()
            num_of_img = len(instance_uids)

            if _mode == 'upper':
                b, e = num_of_img // 2, num_of_img
                uids = instance_uids[b:e]
                def _get_index(x):
                    return x + b
            elif _mode == 'lower':
                b, e = 0, num_of_img // 2
                uids = list(reversed(instance_uids[b:e]))
                def _get_index(x):
                    return e - x - 1
            else:
                b, e = 0, num_of_img
                uids = instance_uids
                def _get_index(x):
                    return x

            def _update(_frame_info):
                for _frame, _idx in _frame_info:
                    self.vtk_img_narray[:, :, _idx] = _frame.reshape(dim[:2], order='F')
                vtk_img.Modified()
                self.sig_refresh_all.emit()

            pool = multiprocessing.Pool(processes=4)
            uid_infos = [[url + "instances/%s/frames/1" % uid, header, _get_index(i), rescale_params] for i, uid in enumerate(uids)]
            a = len(uid_infos) // 4
            b = len(uid_infos) % 4
            for i in range(a):
                pool.map_async(requests_buf16, uid_infos[i*4:i*4+4], callback=_update)
            pool.close()
            pool.join()

        # upper
        WorkerThread.start_worker2(_do, 'upper',
                                   _finished_func=lambda: print("DICOM Files(Upper) had been loaded!! :)"))
        # lower
        WorkerThread.start_worker(_do, 'lower',
                                  _finished_func=lambda: print("DICOM Files(Lower) had been loaded!! :)"))

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
