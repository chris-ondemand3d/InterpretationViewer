import math

import cyCafe
import numpy as np
import vtk
from vtk.util import numpy_support

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.Qt import QApplication, Qt
from PyQt5.QtGui import QCursor

from COMMON import I2G_IMG_HOLDER
from COMMON import SliceImage, pt_on_plane, get_angle_between_vectors, get_rotation_matrix
from _qapp import create_task
# from _IN2GUIDE_DENTAL.blocks.I2G.Measure.MeasureMgr import MeasureMgr

import platform
IS_OSX = (platform.system() == 'Darwin')

CY_VTK_STATE_LOCK = 9919
CAM_SCALE_NORMAL = 0.50
CAM_SCALE_NORMAL_X = 0.35


""" MouseEvent Mode """
# from enum import Enum
# ENUM_EVENT = Enum('event', 'E_NORMAL E_NEW_NERVE E_VERIFICATION E_Reserved')
# ENUM_EVENT_MEASURE = Enum('event', 'E_NONE E_MEASURE_RULER E_MEASURE_ANGLE E_MEASURE_AREA E_MEASURE_TAPELINE E_MEASURE_PROFILE E_MEASURE_ANGLE_4PT E_MEASURE_NOTE')

class Slice(I2G_IMG_HOLDER):

    sig_update_slabplane = pyqtSignal(object)
    sig_change_slice_num = pyqtSignal(object)
    sig_change_wwl = pyqtSignal(object, object)
    sig_refresh_all = pyqtSignal()

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.l_btn_pressed = False
        self.r_btn_pressed = False

        self.initialize()

    def initialize(self):
        # self.init_sub_renderer([0.75, 0, 1, 0.3])

        ISTYLES = cyCafe.cyVtkInteractorStyles()
        # istyle = ISTYLES.get_vtk_interactor_style_image()
        istyle = ISTYLES.get_vtk_interactor_style_image(False, 0)
        # istyle = ISTYLES.get_vtk_interactor_style_volume_3d()
        # istyle = vtk.vtkInteractorStyleUser()
        istyle.AddObserver('MouseWheelForwardEvent', self.on_mouse_wheel)
        istyle.AddObserver('MouseWheelBackwardEvent', self.on_mouse_wheel)
        istyle.AddObserver('MouseMoveEvent', self.on_mouse_move)
        istyle.AddObserver('LeftButtonPressEvent', self.on_mouse_press)
        istyle.AddObserver('RightButtonPressEvent', self.on_mouse_press)
        istyle.AddObserver('LeftButtonReleaseEvent', self.on_mouse_release)
        istyle.AddObserver('RightButtonReleaseEvent', self.on_mouse_release)
        self.view._Iren.SetInteractorStyle(istyle)

        # Make once!!!
        self.slice_img = SliceImage()

        # Picker
        self.picker_vol = vtk.vtkVolumePicker()
        self.picker_vol.PickFromListOn()
        self.picker_vol.InitializePickList()
        self.picker_vol.AddPickList(self.slice_img.get_actor())

    def reset(self):
        self.ren.RemoveAllViewProps()

        def _remove(X):
            if type(X) is not dict:
                for o in X:
                    del o
            X.clear()

        if hasattr(self, 'vtk_img'):
            del self.vtk_img

        if hasattr(self, 'slice_img'):
            del self.slice_img

        if hasattr(self, 'picker_vol'):
            del self.picker_vol

        if hasattr(self, 'patient_info'):
            del self.patient_info

        if hasattr(self, 'dcm_info'):
            del self.dcm_info

        if hasattr(self, 'self.spacing'):
            del self.rendering_type

        if hasattr(self, 'image_filter_type'):
            del self.image_filter_type

        self.l_btn_pressed = False
        self.r_btn_pressed = False

        # NOTE!!! must call "super().reset()"
        super().reset()
        # and then, re initialize()
        self.initialize()

    def clear_all_actors(self):
        self.ren.RemoveAllViewProps()

    def set_patient_info(self, patient_info):
        self.patient_info = patient_info

    def get_patient_info(self):
        return self.patient_info if hasattr(self, 'patient_info') else None

    def set_dcm_info(self, dcm_info):
        self.dcm_info = dcm_info

    def get_dcm_info(self):
        return self.dcm_info if hasattr(self, 'dcm_info') else None

    def set_vtk_img(self, vtk_img):
        assert vtk_img, 'vtk_img is invalid!!!'
        self.vtk_img = vtk_img
        self.slice_img.set_vtk_img(self.vtk_img)

        self.spacing = self.vtk_img.GetSpacing()

        # add actor to renderer, once
        if not self.slice_img.get_actor() in self.ren.GetActors():
            self.ren.AddViewProp(self.slice_img.get_actor())

        d = self.vtk_img.GetDimensions()
        s = self.vtk_img.GetSpacing()
        o = self.vtk_img.GetOrigin()
        c = self.vtk_img.GetCenter()

        plane_pos = [c[0], c[1], o[2]]
        _scale, _axis = (CAM_SCALE_NORMAL_X, 'x') if d[0] / d[1] >= 1.3 else (CAM_SCALE_NORMAL, 'y')
        _params = [plane_pos, np.array([0, 0, -1]), np.array([0, -1, 0]), _scale, _axis]

        # set plane and camera
        self.set_plane(_params[0], _params[1], _params[2], _camera_fit_type=1)
        self.set_camera_scale(_params[3], _params[4])

    def get_vtk_img(self):
        return self.vtk_img if hasattr(self, 'vtk_img') else None

    def set_camera_scale(self, scale, axis='y'):
        axis = axis.upper()
        if axis == 'X':
            B = self.slice_img.get_actor().GetMaxXBound() - self.slice_img.get_actor().GetMinXBound()
        elif axis == 'Y':
            B = self.slice_img.get_actor().GetMaxYBound() - self.slice_img.get_actor().GetMinYBound()
        else:
            B = self.slice_img.get_actor().GetMaxYBound() - self.slice_img.get_actor().GetMinYBound()
        cam = self.ren.GetActiveCamera()
        cam.ParallelProjectionOn()
        cameraResetParallelScale = B * scale
        cam.SetParallelScale(cameraResetParallelScale)

    def set_actor_property(self, img_prop):
        assert self.slice_img
        self.slice_img.set_actor_property(img_prop)

    def set_windowing(self, w, l):
        if hasattr(self, 'slice_img') and self.slice_img:
            self.slice_img.property.SetColorWindow(w)
            self.slice_img.property.SetColorLevel(l)

    def get_windowing(self):
        if hasattr(self, 'slice_img') and self.slice_img:
            w = self.slice_img.property.GetColorWindow()
            l = self.slice_img.property.GetColorLevel()
            return w, l
        return None, None

    def reset_all(self, w, l):
        if hasattr(self, 'slice_img') and self.slice_img and self.slice_img.get_actor():
            self.slice_img.get_actor().GetProperty().SetColorWindow(w)
            self.slice_img.get_actor().GetProperty().SetColorLevel(l)

    def visible_actor(self, actor_type, visible):
        # if actor_type is 'dsi':
        #     self.dsi_cross.get_actor().SetVisibility(visible)
        #     self.dsi_parallel.get_actor().SetVisibility(visible)
        #     self.dsi_axial.get_actor().SetVisibility(visible)
        # elif actor_type is 'dsi_cross':
        #     self.dsi_cross.get_actor().SetVisibility(visible)
        # elif actor_type is 'dsi_parallel':
        #     self.dsi_parallel.get_actor().SetVisibility(visible)
        # elif actor_type is 'dsi_axial':
        #     self.dsi_axial.get_actor().SetVisibility(visible)
        # elif actor_type is 'model':
        #     if 'model' in self.CONTOURS:
        #         self.CONTOURS['model'].get_actor().SetVisibility(visible)
        pass

    # def set_plane(self, origin, normal, view_up=None, _camera_fit=False):
    def set_plane(self, origin, normal, view_up=None, _camera_fit_type=None):
        cam = self.ren.GetActiveCamera()
        self.slice_img.set_plane(origin, normal)

        if _camera_fit_type is None:
            return

        if view_up is not None:
            view_up_vec = view_up
        else:
            view_up_vec = cam.GetViewUp()

        if _camera_fit_type == 1:
            focal_pt = origin
            cam_pos = np.array(focal_pt) + (np.array(normal) * 100)
        elif _camera_fit_type == 2:
            focal_pt = cam.GetFocalPoint()
            cam_pos = np.array(focal_pt) + (np.array(normal) * 100)
        else:
            return

        cam.SetFocalPoint(focal_pt)
        cam.SetPosition(cam_pos)
        cam.SetViewUp(view_up_vec)

    def get_plane(self, _ignore_mirror=False):
        # NOTE plane normal must be multiplied by -1 if self.slice_img.mirrored is true
        _plane = self.slice_img.get_plane()
        _origin = list(_plane.GetOrigin())
        _normal = list(_plane.GetNormal())
        if not _ignore_mirror and self.slice_img.mirrored:
            _normal = (np.array(_normal) * -1).tolist()
        return _origin, _normal

    def set_camera_view_up(self, up_vec):
        cam = self.ren.GetActiveCamera()
        cam.SetViewUp(up_vec)

    def scroll(self, _interval):
        # if self.slice_type == 'axial':
        #     _origin, _normal = self.get_plane()
        #     _new_pos = np.array(_origin) + (np.array(_normal) * _interval)
        #     self.set_plane(_new_pos, _normal)
        pass

    def rotate(self, _angle, _axis):
        # _origin, _normal = self.get_plane()
        # _rot_axis = _axis / np.linalg.norm(_axis)
        # _result_mat = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        # # NOTE!!! Quaternion Q : w, x, y, z  =>  cos(theta/2), v*sin(theta/2)
        # _v = np.multiply(_rot_axis, math.sin(_angle / 2))
        # vtk.vtkMath.QuaternionToMatrix3x3([math.cos(_angle / 2), _v[0], _v[1], _v[2]], _result_mat)
        # _new_normal = np.matmul(np.array(_result_mat).reshape(3, 3), _normal)
        # _new_normal = _new_normal / np.linalg.norm(_new_normal)
        # self.set_plane(_origin, _new_normal, _camera_fit=True)
        pass

    """
    Mouse Event Generic
    """
    def on_mouse_move(self, _rwi, _event):
        # if self.EventMode is ENUM_EVENT.E_NORMAL:
        #     self.on_mouse_move_normal(_rwi, _event)
        # # Measure
        # if self.EventMode_Measure is not ENUM_EVENT_MEASURE.E_NONE:
        #     self.on_mouse_move_measure(_rwi, _event)

        self.on_mouse_move_normal(_rwi, _event)

    def on_mouse_press(self, _rwi, _event):
        i = _rwi.GetInteractor()
        x, y = i.GetEventPosition()
        prev_x, prev_y = i.GetLastEventPosition()

        if _event == "LeftButtonPressEvent":
            self.l_btn_pressed = True

            # TODO check handle type(move or rotate) of picked obj
            if not hasattr(self, 'vtk_img') or not self.vtk_img:
                return

        elif _event == "RightButtonPressEvent":
            self.r_btn_pressed = True
        # # Measure
        # if self.EventMode_Measure is not ENUM_EVENT_MEASURE.E_NONE:
        #     self.on_mouse_press_measure(_rwi, _event)
        #     return
        # if self.EventMode is ENUM_EVENT.E_NORMAL:
        #     self.on_mouse_press_normal(_rwi, _event)

    def on_mouse_release(self, _rwi, _event):
        self.l_btn_pressed = False
        self.r_btn_pressed = False

        # # Measure
        # if self.EventMode_Measure is not ENUM_EVENT_MEASURE.E_NONE:
        #     self.on_mouse_release_measure(_rwi, _event)
        #     return
        # if self.EventMode is ENUM_EVENT.E_NORMAL:
        #     self.on_mouse_release_normal(_rwi, _event)

    def on_mouse_wheel(self, _rwi, _event=""):
        # if self.EventMode is ENUM_EVENT.E_NORMAL:
        #     self.on_mouse_wheel_normal(_rwi, _event)
        # # Measure
        # if self.EventMode_Measure is not ENUM_EVENT_MEASURE.E_NONE:
        #     self.on_mouse_wheel_measure(_rwi, _event)

        self.on_mouse_wheel_normal(_rwi, _event)
        self.refresh()

    """
    Mouse Event Normal
    """
    def on_mouse_move_normal(self, _rwi, _event):
        i = _rwi.GetInteractor()
        x, y = i.GetEventPosition()
        prev_x, prev_y = i.GetLastEventPosition()

        # if _rwi.GetState() == vtk.VTKIS_WINDOW_LEVEL:
        #     self.need_to_refresh_all = True

        if self.l_btn_pressed:
            pass

        elif self.r_btn_pressed:
            if _rwi.GetState() == vtk.VTKIS_WINDOW_LEVEL:
                ww, wl = self.get_windowing()
                self.sig_change_wwl.emit(ww, wl)
                self.sig_refresh_all.emit()
        else:
            pass

        self.refresh()

    def on_mouse_press_normal(self, _rwi, _event):
        i = _rwi.GetInteractor()
        x, y = i.GetEventPosition()
        if _event == "LeftButtonPressEvent":
            pass
        elif _event == "RightButtonPressEvent":
            pass

    def on_mouse_release_normal(self, _rwi, _event):
        i = _rwi.GetInteractor()
        x, y = i.GetEventPosition()

        if _event == "LeftButtonReleaseEvent":

            if hasattr(self, 'need_to_refresh_all') and self.need_to_refresh_all:
                self.need_to_refresh_all = False

                async def _do():
                    await self.i2g_mgr.refresh_all()
                create_task(_do())

        elif _event == "RightButtonReleaseEvent":
            if self.slice_type == "axial":
                pass

    def on_mouse_wheel_normal(self, _rwi, _event):
        _ctrl = _rwi.GetInteractor().GetControlKey()
        _shift = _rwi.GetInteractor().GetShiftKey()
        _alt = _rwi.GetInteractor().GetAltKey()

        if self.vtk_img is None:
            return

        _sign = 1 if _event == r'MouseWheelForwardEvent' else -1
        _sign *= -1 if IS_OSX else 1
        _interval = 5 if _ctrl else 1

        thickness = self.spacing[2] if hasattr(self, 'spacing') else 0.2

        o, n = self.get_plane()
        o = list(np.array(o) + np.array(n) * (thickness * _interval * _sign))

        # TODO !!!!!!!!!!!!
        src_d = np.array(self.vtk_img.GetDimensions())
        src_s = np.array(self.vtk_img.GetSpacing())
        src_o = np.array(self.vtk_img.GetOrigin())
        slice_num = int(((o - src_o)[2] / src_s[2]))
        if slice_num < 0 or slice_num >= src_d[2]: # TODO
            return
        self.sig_change_slice_num.emit(slice_num)
        self.set_plane(o, n)

    def refresh(self):
        super().refresh()

    # def check_plane(self):
    #     self.Measure.check_plane_measure(self.get_plane())

    def set_mode(self, _mode):
        # if _mode == 'measure_ruler':
        #     self.EventMode = ENUM_EVENT.E_MEASURE_RULER
        # elif _mode == 'measure_angle':
        #     self.EventMode = ENUM_EVENT.E_MEASURE_ANGLE
        # else:
        #     self.EventMode = ENUM_EVENT.E_NORMAL
        #     self.visible_actor('dsi', True) # TODO
        #     self.remove_dsi_implant()
        #     if self.slice_type == 'cross':
        #         self.set_camera_scale(CAM_SCALE_NORMAL_THREE[0])
        #     elif self.slice_type == 'parallel':
        #         self.set_camera_scale(CAM_SCALE_NORMAL_THREE[1])
        #     elif self.slice_type == 'axial':
        #         self.arch_line.set_visible(True)
        #         self.set_camera_scale(CAM_SCALE_NORMAL_THREE[2])
        pass

    def set_measure_mode(self, _mode):
        # if _mode == 'ruler':
        #     self.EventMode_Measure = ENUM_EVENT_MEASURE.E_MEASURE_RULER
        #     self.Measure.set_active_mode(_mode)
        #     self.Measure.create_new_measure()
        # elif _mode == 'point3':
        #     self.EventMode_Measure = ENUM_EVENT_MEASURE.E_MEASURE_ANGLE
        #     self.Measure.set_active_mode(_mode)
        #     self.Measure.create_new_measure()
        # elif _mode == 'area':
        #     self.EventMode_Measure = ENUM_EVENT_MEASURE.E_MEASURE_AREA
        #     self.Measure.set_active_mode(_mode)
        #     self.Measure.create_new_measure()
        # elif _mode == 'tapeline':
        #     self.EventMode_Measure = ENUM_EVENT_MEASURE.E_MEASURE_TAPELINE
        #     self.Measure.set_active_mode(_mode)
        #     self.Measure.create_new_measure()
        # elif _mode == 'profile':
        #     self.EventMode_Measure = ENUM_EVENT_MEASURE.E_MEASURE_PROFILE
        #     self.Measure.set_active_mode(_mode)
        #     self.Measure.create_new_measure()
        # elif _mode == 'point4':
        #     self.EventMode_Measure = ENUM_EVENT_MEASURE.E_MEASURE_ANGLE_4PT
        #     self.Measure.set_active_mode(_mode)
        #     self.Measure.create_new_measure()
        # elif _mode == 'note':
        #     self.EventMode_Measure = ENUM_EVENT_MEASURE.E_MEASURE_NOTE
        #     self.Measure.set_active_mode(_mode)
        #     self.Measure.create_new_measure()
        # else:
        #     self.EventMode_Measure = ENUM_EVENT_MEASURE.E_NONE
        pass

    def measure_reset(self):
        # self.Measure.reset_all()
        # self.refresh()
        pass

    # def _make_profile(self, _intensity, _distance):
    #     # self.i2g_mgr.make_profile(_intensity, _distance)
    #     pass
    #
    # def _edit_note(self, _str):
    #     await self.i2g_mgr.edit_note(_str, self.slice_type)

    # def save_note(self, _str):
    #     self.Measure.save_note(_str)

    def get_slice_num(self):
        # TODO !!!!!!!!!!!!
        o, n = self.get_plane()
        src_d = np.array(self.vtk_img.GetDimensions())
        src_s = np.array(self.vtk_img.GetSpacing())
        src_o = np.array(self.vtk_img.GetOrigin())
        slice_num = int(((o - src_o)[2] / src_s[2]))
        return slice_num

    def set_thickness(self, _value):
        self.slice_img.set_thickness(_value)

    def get_thickness(self):
        return self.slice_img.get_thickness()

    def set_rendering_type(self, _value):
        self.rendering_type = _value
        self.slice_img.set_rendering_type(self.rendering_type)

    def set_image_filter_type(self, _value):
        self.image_filter_type = _value

        if self.image_filter_type == "Gaussian":
            self.slice_img.cy_img_reslice_mapper.set_filter_gaussian(True)
            self.slice_img.cy_img_reslice_mapper.set_filter_sharpen(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_unsharpen(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_bilateral(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_anisotropic(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_highboost(False)
            self.refresh()

        elif self.image_filter_type == "Sharpen":
            self.slice_img.cy_img_reslice_mapper.set_filter_gaussian(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_sharpen(True)
            self.slice_img.cy_img_reslice_mapper.set_filter_unsharpen(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_bilateral(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_anisotropic(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_highboost(False)
            self.refresh()

        elif self.image_filter_type == "Unsharpen":
            self.slice_img.cy_img_reslice_mapper.set_filter_gaussian(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_sharpen(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_unsharpen(True)
            self.slice_img.cy_img_reslice_mapper.set_filter_bilateral(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_anisotropic(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_highboost(False)
            self.refresh()

        elif self.image_filter_type == "Bilateral":
            self.slice_img.cy_img_reslice_mapper.set_filter_gaussian(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_sharpen(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_unsharpen(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_bilateral(True)
            self.slice_img.cy_img_reslice_mapper.set_filter_anisotropic(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_highboost(False)
            self.refresh()

        elif self.image_filter_type == "Anisotropic":
            self.slice_img.cy_img_reslice_mapper.set_filter_gaussian(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_sharpen(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_unsharpen(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_bilateral(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_anisotropic(True)
            self.slice_img.cy_img_reslice_mapper.set_filter_highboost(False)
            self.refresh()

        elif self.image_filter_type == "Highboost":
            self.slice_img.cy_img_reslice_mapper.set_filter_gaussian(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_sharpen(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_unsharpen(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_bilateral(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_anisotropic(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_highboost(True)
            self.refresh()

        elif self.image_filter_type == "Filter Off":
            self.slice_img.cy_img_reslice_mapper.set_filter_gaussian(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_sharpen(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_unsharpen(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_bilateral(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_anisotropic(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_highboost(False)
            self.refresh()

        else:
            self.slice_img.cy_img_reslice_mapper.set_filter_gaussian(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_sharpen(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_unsharpen(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_bilateral(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_anisotropic(False)
            self.slice_img.cy_img_reslice_mapper.set_filter_highboost(False)
            self.refresh()

    def get_image_filter_type(self):
        return self.image_filter_type if hasattr(self, 'image_filter_type') else 'Filter Off'

    # def get_project_info(self):
    #     info = dict()
    #     info["Type"] = self.slice_type
    #     info["Thickness"] = self.get_thickness()
    #     info["Filter"] = self.image_filter_type if hasattr(self, 'image_filter_type') else 'None'
    #     return info

    def mouseDoubleClickEvent(self, e):
        super().mouseDoubleClickEvent(e)
