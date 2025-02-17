import math

from cyCafe import cyBoostConversion
from cyCafe import cyVtkInteractorStyles
import numpy as np
import vtk
from vtk.util import numpy_support

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.Qt import QApplication, Qt
from PyQt5.QtGui import QCursor

from COMMON import I2G_IMG_HOLDER, Sphere, Sphere2D, LINE, LINE2D, Glyph3D
from COMMON import SliceImage, pt_on_plane, get_angle_between_vectors, get_rotation_matrix, get_vtkmat_from_list, intersection_of_two_planes, intersection_of_two_lines
from _qapp import create_task
from APP._InterpretationViewer.blocks.Measure import Measure, E_MEASURE

import platform
IS_OSX = (platform.system() == 'Darwin')

CY_VTK_STATE_LOCK = 9919


class Slice(I2G_IMG_HOLDER):

    sig_changed_slice = pyqtSignal(object)
    sig_change_slice_num = pyqtSignal(object)
    sig_change_wwl = pyqtSignal(object, object)

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.l_btn_pressed = False
        self.r_btn_pressed = False

        self.initialize()

    def initialize(self):
        # self.init_sub_renderer([0.75, 0, 1, 0.3])

        # NOTE !!!
        self.cyistyle_wrapper = cyVtkInteractorStyles.cyVtkInteractorStyles()
        istyle = self.cyistyle_wrapper.get_interactor("image")
        # istyle = self.cyistyle_wrapper.get_vtk_interactor_style_volume_3d()
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

        self.event_mode = E_MEASURE.NONE

    def resize(self, w, h):
        super().resize(w, h)

        if hasattr(self, 'measure') and type(self.measure) is Measure:
            self.measure.resize(w, h)
            self.refresh()

    def reset(self):
        self.ren.RemoveAllViewProps()

        def _remove(X):
            if type(X) is not dict:
                for o in X:
                    del o
            X.clear()

        if hasattr(self, 'event_mode'):
            del self.event_mode

        if hasattr(self, 'measure'):
            # self.measure.reset()
            del self.measure

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

        if hasattr(self, 'initial_wwl'):
            del self.initial_wwl

        if hasattr(self, 'patient_pos_ori'):
            self.patient_pos_ori.clear()
            del self.patient_pos_ori

        if hasattr(self, '_line_intersection'):
            self.ren.RemoveActor(self._line_intersection.get_actor())
            del self._line_intersection

        self.l_btn_pressed = False
        self.r_btn_pressed = False

        # NOTE!!! must call "super().reset()"
        super().reset()
        # and then, re initialize()
        self.initialize()

    def clear_all_actors(self):
        self.ren.RemoveAllViewProps()

    def reset_measure(self):
        if hasattr(self, 'measure'):
            self.measure.reset_all()

    def set_patient_info(self, patient_info):
        self.patient_info = patient_info

    def get_patient_info(self):
        return self.patient_info if hasattr(self, 'patient_info') else None

    def set_dcm_info(self, dcm_info):
        self.dcm_info = dcm_info

    def get_dcm_info(self):
        return self.dcm_info if hasattr(self, 'dcm_info') else None

    def set_vtk_img(self, vtk_img, patient_pos_ori=None):
        assert vtk_img, 'vtk_img is invalid!!!'
        self.vtk_img = vtk_img
        self.patient_pos_ori = patient_pos_ori
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
        _params = [plane_pos, np.array([0, 0, -1]), np.array([0, -1, 0])]

        # set plane and camera
        self.set_plane(_params[0], _params[1], _params[2], _camera_fit_type=1)
        self.fit_img_to_screen()

        # create measure
        self.measure = Measure(self.ren, self.get_plane_obj(), self.get_thickness())

    def get_vtk_img(self):
        return self.vtk_img if hasattr(self, 'vtk_img') else None

    def set_camera_scale(self, scale):
        cam = self.ren.GetActiveCamera()
        cam.ParallelProjectionOn()
        cam.SetParallelScale(scale)

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

    def get_plane_obj(self):
        return self.slice_img.get_plane()

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
    def on_mouse_move(self, rwi, event):
        if self.event_mode is not E_MEASURE.NONE and self.event_mode in E_MEASURE:
            self.measure.mouse_move(rwi, event)
            self.refresh()
        else:
            self.on_mouse_move_normal(rwi, event)

    def on_mouse_press(self, rwi, event):
        i = rwi.GetInteractor()
        x, y = i.GetEventPosition()
        prev_x, prev_y = i.GetLastEventPosition()

        if event == "LeftButtonPressEvent":
            self.l_btn_pressed = True

            # TODO check handle type(move or rotate) of picked obj
            if not hasattr(self, 'vtk_img') or not self.vtk_img:
                return

        elif event == "RightButtonPressEvent":
            self.r_btn_pressed = True

        # Measure
        if self.event_mode is not E_MEASURE.NONE and self.event_mode in E_MEASURE:
            self.measure.mouse_press(rwi, event)
            self.refresh()
        else:
            self.on_mouse_press_normal(rwi, event)

    def on_mouse_release(self, rwi, event):
        self.l_btn_pressed = False
        self.r_btn_pressed = False

        # Measure
        if self.event_mode is not E_MEASURE.NONE and self.event_mode in E_MEASURE:
            self.measure.mouse_release(rwi, event)
            self.refresh()
        else:
            self.on_mouse_release_normal(rwi, event)

    def on_mouse_wheel(self, _rwi, _event=""):
        # if self.EventMode is ENUM_EVENT.E_NORMAL:
        #     self.on_mouse_wheel_normal(_rwi, _event)
        # # Measure
        # if self.EventMode_Measure is not ENUM_EVENT_MEASURE.E_NONE:
        #     self.on_mouse_wheel_measure(_rwi, _event)

        self.on_mouse_wheel_normal(_rwi, _event)

        self.measure.plane_check()

        self.refresh()

    """
    Mouse Event Normal
    """
    def on_mouse_move_normal(self, rwi, event):
        i = rwi.GetInteractor()
        x, y = i.GetEventPosition()
        prev_x, prev_y = i.GetLastEventPosition()

        if rwi.GetState() == vtk.VTKIS_WINDOW_LEVEL:
            ww, wl = self.get_windowing()
            self.sig_change_wwl.emit(ww, wl)
            self.refresh()

    def on_mouse_press_normal(self, rwi, event):
        i = rwi.GetInteractor()
        x, y = i.GetEventPosition()
        if event == "LeftButtonPressEvent":
            pass
        elif event == "RightButtonPressEvent":
            pass

    def on_mouse_release_normal(self, rwi, event):
        i = rwi.GetInteractor()
        x, y = i.GetEventPosition()

        if event == "LeftButtonReleaseEvent":
            pass

        elif event == "RightButtonReleaseEvent":
            pass

    def on_mouse_wheel_normal(self, rwi, event):
        _ctrl = rwi.GetInteractor().GetControlKey()
        _shift = rwi.GetInteractor().GetShiftKey()
        _alt = rwi.GetInteractor().GetAltKey()

        if self.vtk_img is None:
            return

        _sign = 1 if event == r'MouseWheelForwardEvent' else -1
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
        self.sig_changed_slice.emit(_interval * _sign)
        self.set_plane(o, n)

    def move_slice(self, value):
        thickness = self.spacing[2] if hasattr(self, 'spacing') else 0.2
        o, n = self.get_plane()
        o = list(np.array(o) + np.array(n) * (thickness * value))
        # TODO !!!!!!!!!!!!
        src_d = np.array(self.vtk_img.GetDimensions())
        src_s = np.array(self.vtk_img.GetSpacing())
        src_o = np.array(self.vtk_img.GetOrigin())
        slice_num = int(((o - src_o)[2] / src_s[2]))
        if slice_num < 0 or slice_num >= src_d[2]:  # TODO
            return
        self.sig_change_slice_num.emit(slice_num)
        self.set_plane(o, n)

    def refresh(self):
        super().refresh()

    # def check_plane(self):
    #     self.Measure.check_plane_measure(self.get_plane())

    def set_mode(self, _mode):

        if _mode is None:
            self.event_mode = E_MEASURE.NONE
            self.measure.set_activation(self.event_mode)
            self.set_interactor_mode('none')
            return

        _mode = _mode.upper()

        if not _mode in [e.name for e in E_MEASURE]:
            self.event_mode = E_MEASURE.NONE
            self.measure.set_activation(self.event_mode)
            self.set_interactor_mode('none')
            return

        self.event_mode = E_MEASURE[_mode]

        if self.event_mode is E_MEASURE.NONE:
            pass
        elif self.event_mode is E_MEASURE.RULER:
            self.measure.set_activation(self.event_mode)

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

    def get_scout_img(self):
        _vtk_img = self.get_vtk_img()
        if _vtk_img is None:
            return None, None, None
        _scout_dims = _vtk_img.GetFieldData().GetArray('SCOUT_IMG_DIMS')
        _scout_arr = _vtk_img.GetFieldData().GetArray('SCOUT_IMG')
        if _scout_dims is None or _scout_arr is None:
            return self.get_thumbnail_img()
        _scout_dims = numpy_support.vtk_to_numpy(_scout_dims)
        _scout_arr = numpy_support.vtk_to_numpy(_scout_arr)
        _scout_arr = _scout_arr.reshape(_scout_dims[1], _scout_dims[0], _scout_dims[2])
        return _scout_arr, _scout_dims, 8

    def get_thumbnail_img(self):
        _vtk_img = self.get_vtk_img()
        if _vtk_img is None:
            return None, None, None
        _thumbnail_dims = _vtk_img.GetFieldData().GetArray('THUMBNAIL_IMG_DIMS')
        _thumbnail_arr = _vtk_img.GetFieldData().GetArray('THUMBNAIL_IMG')
        if _thumbnail_dims is None or _thumbnail_arr is None:
            return None, None, None
        _thumbnail_dims = numpy_support.vtk_to_numpy(_thumbnail_dims)
        _thumbnail_arr = numpy_support.vtk_to_numpy(_thumbnail_arr)
        _thumbnail_arr = _thumbnail_arr.reshape(_thumbnail_dims[1], _thumbnail_dims[0])
        return _thumbnail_arr, _thumbnail_dims, 16

    def mouseDoubleClickEvent(self, e):
        super().mouseDoubleClickEvent(e)

    def set_interactor_mode(self, mode):
        assert hasattr(self, 'cyistyle_wrapper'), "!!!"
        self.cyistyle_wrapper.set_state(mode)

    def fit_img_to_screen(self):
        _o, _n = self.get_plane()
        d = self.vtk_img.GetDimensions()
        s = self.vtk_img.GetSpacing()
        w = self.ren.GetRenderWindow().GetSize()

        ratio_screen = w[0] / w[1]
        ratio_img = d[0] / d[1]

        if ratio_screen < ratio_img:
            scale = (w[1] * d[0] / w[0]) * s[0] * 0.5  # dx
        else:
            scale = d[1] * s[1] * 0.5  # dy

        self.set_camera_scale(scale)
        cam = self.ren.GetActiveCamera()
        cam_pos = np.array(_o) + (np.array(_n) * 100)
        cam.SetFocalPoint(_o)
        cam.SetPosition(cam_pos)

    def cross_link(self, _senders_pos_ori):
        if not hasattr(self, '_line_intersection'):
            self._line_intersection = LINE2D(radius=0.2, color=[0,1,1], opacity=0.3)
            self.ren.AddActor(self._line_intersection.get_actor())
        # if not hasattr(self, '_glyph'):
        #     self._glyph = Glyph3D(radius=1.0, color=[1, 0, 1])
        #     self.ren.AddActor(self._glyph.get_actor())

        if _senders_pos_ori is None:
            self._line_intersection.get_actor().SetVisibility(False)
            # self._glyph.get_actor().SetVisibility(False)
            self.refresh()
            return

        # itself
        _cur_num = self.get_slice_num()
        _cur_pos, _cur_ori = self.patient_pos_ori[_cur_num]

        # sender's
        _senders_pos, _senders_ori = _senders_pos_ori

        mat = np.column_stack([np.append(_cur_ori[:3], [0]),
                               np.append(_cur_ori[3:], [0]),
                               np.append(np.cross(_cur_ori[:3], _cur_ori[3:]), [0]),
                               _cur_pos+[1]])
        mat_inv = np.linalg.inv(mat)
        disp = np.array(_senders_pos)
        _pt0 = np.matmul(mat_inv, np.asmatrix(np.append(disp, [1])).transpose())[:3]
        _pt1 = np.matmul(mat_inv, np.asmatrix(np.append((disp + np.multiply(_senders_ori[:3], 100)), [1])).transpose())[:3]
        _pt2 = np.matmul(mat_inv, np.asmatrix(np.append((disp + np.multiply(_senders_ori[3:], 100)), [1])).transpose())[:3]

        vec_a = np.asarray(_pt1).flatten() - np.asarray(_pt0).flatten()
        vec_a = vec_a / np.linalg.norm(vec_a)
        vec_b = np.asarray(_pt2).flatten() - np.asarray(_pt0).flatten()
        vec_b = vec_b / np.linalg.norm(vec_b)
        vec_c = np.cross(vec_a, vec_b)
        vec_c = vec_c / np.linalg.norm(vec_c)

        _pt3 = np.multiply(vec_c, 100)

        _, vec_d = self.get_plane()
        vec_d = vec_d / np.linalg.norm(vec_d)

        # calc intersection line of two planes
        _plane1 = np.asarray(_pt0).flatten(), vec_c.flatten()
        _p, _n = self.get_plane()
        _plane2 = np.asarray(_p), np.asarray(_n)
        _p, _v = intersection_of_two_planes(*_plane1, *_plane2)
        _p1_of_i = _p
        _p2_of_i = _p + _v

        # bound check
        _bds = self.slice_img.get_actor().GetBounds()
        _bounding_pt0 = np.array([_bds[0], _bds[2], _bds[4]])
        _bounding_pt1 = np.array([_bds[1], _bds[2], _bds[4]])
        _bounding_pt2 = np.array([_bds[1], _bds[3], _bds[4]])
        _bounding_pt3 = np.array([_bds[0], _bds[3], _bds[4]])
        _bounding_vec0 = _bounding_pt1 - _bounding_pt0
        _bounding_vec0 = _bounding_vec0 / np.linalg.norm(_bounding_vec0)
        _bounding_vec1 = _bounding_pt2 - _bounding_pt1
        _bounding_vec1 = _bounding_vec1 / np.linalg.norm(_bounding_vec1)
        _bounding_vec2 = _bounding_pt3 - _bounding_pt2
        _bounding_vec2 = _bounding_vec2 / np.linalg.norm(_bounding_vec2)
        _bounding_vec3 = _bounding_pt0 - _bounding_pt3
        _bounding_vec3 = _bounding_vec3 / np.linalg.norm(_bounding_vec3)
        results = []

        for _line in [[_bounding_pt0, _bounding_pt1], [_bounding_pt1, _bounding_pt2],
                      [_bounding_pt2, _bounding_pt3], [_bounding_pt3, _bounding_pt0]]:
            _xyz = intersection_of_two_lines([_p1_of_i, _p2_of_i], _line)
            results.append(_xyz)
        _center = np.mean([_bounding_pt0, _bounding_pt1, _bounding_pt2, _bounding_pt3], axis=0)
        results = sorted(results, key=lambda _key: np.fabs(np.linalg.norm(_key - _center)))

        _p1_of_i = results[0]
        _p2_of_i = results[1]
        # self._glyph.set_pts(np.asarray(results))

        """
        """

        if np.abs(np.inner(vec_c, vec_d)) > 0.7:
            self._line_intersection.get_actor().SetVisibility(False)
            # self._glyph.get_actor().SetVisibility(False)
        else:
            self._line_intersection.get_actor().SetVisibility(True)
            # self._glyph.get_actor().SetVisibility(True)

        self._line_intersection.set_points([_p1_of_i, _p2_of_i])
        self.refresh()
