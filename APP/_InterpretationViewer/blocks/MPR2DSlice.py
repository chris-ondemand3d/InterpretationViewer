import math

from cyCafe import cyBoostConversion
from cyCafe import cyVtkInteractorStyles
import numpy as np
import vtk

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


# 0: sagittal, 1: coronal, 2: axial
PLANETYPE = ['coronal', 'sagittal', 'axial']


""" MouseEvent Mode """
# from enum import Enum
# ENUM_EVENT = Enum('event', 'E_NORMAL E_NEW_NERVE E_VERIFICATION E_Reserved')
# ENUM_EVENT_MEASURE = Enum('event', 'E_NONE E_MEASURE_RULER E_MEASURE_ANGLE E_MEASURE_AREA E_MEASURE_TAPELINE E_MEASURE_PROFILE E_MEASURE_ANGLE_4PT E_MEASURE_NOTE')

class MPR2DSlice(I2G_IMG_HOLDER):

    class GUIDE_LINE_DSI:

        _COLOR_default = [0, 0.75294, 0.95294]

        class GUIDE_LINE:

            _COLOR_axial = [205 / 255, 62 / 255, 0 / 255]
            # _COLOR_axial = [107/255, 63/255, 160/255]
            _COLOR_coronal = [0 / 255, 145 / 255, 205 / 255]
            _COLOR_sagittal = [191 / 255, 255 / 255, 0 / 255]

            def __init__(self, parent_type, type, parent_plane, ren):
                self.parent_type = parent_type
                self.type = type
                self.parent_plane = parent_plane
                self.ren = ren
                self.camera = ren.GetActiveCamera()

                # line
                self.line = vtk.vtkLineSource()
                self.mapper = vtk.vtkPolyDataMapper2D()
                self.mapper.SetInputConnection(self.line.GetOutputPort())
                coordinate = vtk.vtkCoordinate()
                coordinate.SetCoordinateSystemToWorld()
                self.mapper.SetTransformCoordinate(coordinate)

                self.actor = vtk.vtkActor2D()
                self.actor.SetMapper(self.mapper)
                _col = getattr(self, '_COLOR_' + type) if hasattr(self, '_COLOR_' + type) else self._COLOR_default
                self.actor.GetProperty().SetColor(_col)
                self.actor.SetPickable(False)

                self.plane = vtk.vtkPlane()

            def __del__(self):
                del self.actor
                del self.mapper
                del self.line
                del self.camera
                del self.ren
                del self.parent_plane
                del self.parent_type
                del self.type
                del self.plane

            def get_actor(self):
                return self.actor

            def update(self, plane_info):
                self.plane.SetOrigin(plane_info[0])
                self.plane.SetNormal(plane_info[1])
                self.plane.Modified()

                # pos = self.plane.GetOrigin()

                # TODO!!!
                plane_a_o = self.plane.GetOrigin()  # axial
                plane_a_v = self.plane.GetNormal()  # axial
                plane_b_o = self.parent_plane.GetOrigin()  # may be cross
                plane_b_v = self.parent_plane.GetNormal()  # may be cross
                # equation
                d1 = (-1 * plane_a_v[0] * plane_a_o[0]) + (-1 * plane_a_v[1] * plane_a_o[1]) + \
                     (-1 * plane_a_v[2] * plane_a_o[2])
                d2 = (-1 * plane_b_v[0] * plane_b_o[0]) + (-1 * plane_b_v[1] * plane_b_o[1]) + \
                     (-1 * plane_b_v[2] * plane_b_o[2])
                a = np.array([plane_a_v, plane_b_v])
                b = np.array([-1 * d1, -1 * d2])
                # solve
                i = np.linalg.pinv(a)
                b = np.matmul(i, b)
                pos = b

                v = self.camera.GetViewPlaneNormal()
                hor = np.cross(self.plane.GetNormal(), v)
                size = 500
                x = hor * size
                pt1 = (np.array(pos) + x).tolist()
                pt2 = (np.array(pos) + (x * -1)).tolist()

                self.line.SetPoint1(pt1)
                self.line.SetPoint2(pt2)
                self.line.Update()
                self.line.Modified()
                self.actor.Modified()


        def __init__(self, parent_type, parent_plane, ren):

            self.parent_type = parent_type
            self.parent_plane = parent_plane
            self.ren = ren
            self.camera = ren.GetActiveCamera()

            # lines
            # 0: sagittal, 1: coronal, 2: axial
            for t in PLANETYPE:
                if self.parent_type == t: continue
                setattr(self, 'dsi_%s' % t, self.GUIDE_LINE(self.parent_type, t, self.parent_plane, self.ren))

            # handle
            self.handle_sphere = vtk.vtkSphereSource()
            self.handle_sphere.SetRadius(10.0)
            self.handle_mapper = vtk.vtkPolyDataMapper2D()
            self.handle_mapper.SetInputConnection(self.handle_sphere.GetOutputPort())

            coordinate = vtk.vtkCoordinate()
            coordinate.SetCoordinateSystemToWorld()
            self.handle_mapper.SetTransformCoordinate(coordinate)

            self.handle_actor = vtk.vtkActor2D()
            self.handle_actor.SetMapper(self.handle_mapper)
            self.handle_actor.GetProperty().SetOpacity(0)

            # activation flag
            self.move_activated = False
            self.rotate_activated = False

        def __del__(self):
            del self.camera
            del self.ren
            del self.parent_plane
            del self.parent_type
            del self.handle_actor
            del self.handle_mapper
            del self.handle_sphere
            for t in PLANETYPE:
                if hasattr(self, 'dsi_%s' % t):
                    delattr(self, 'dsi_%s' % t)

        def get_actors(self):
            actors = []
            for t in PLANETYPE:
                if hasattr(self, 'dsi_%s' % t):
                    actors.append(getattr(self, 'dsi_%s' % t).get_actor())
            actors.append(self.handle_actor)
            return actors

        def update(self, planes):
            # line update
            for k, v in planes.items():
                if hasattr(self, 'dsi_%s' % k):
                    getattr(self, 'dsi_%s' % k).update(v)
            # handle update
            if planes.get('handle'):
                self.handle_sphere.SetCenter(planes['handle'])
                self.handle_sphere.Update()
                self.handle_sphere.Modified()
                self.handle_mapper.Update()
                self.handle_actor.Modified()

        def move_handle(self, pos):
            # handle update
            self.handle_sphere.SetCenter(pos)
            self.handle_sphere.Update()
            self.handle_sphere.Modified()
            self.handle_mapper.Update()
            self.handle_actor.Modified()
            # line update
            for t in PLANETYPE:
                if hasattr(self, 'dsi_%s' % t):
                    _dsi = getattr(self, 'dsi_%s' % t)
                    _dsi.update([pos, _dsi.plane.GetNormal()])

        def rotate_handle(self, theta, rot_axis):
            _o = self.handle_sphere.GetCenter()
            for t in PLANETYPE:
                if hasattr(self, 'dsi_%s' % t):
                    _dsi = getattr(self, 'dsi_%s' % t)
                    # _o = list(_dsi.plane.GetOrigin())
                    _n = list(_dsi.plane.GetNormal())
                    rot_mat = get_rotation_matrix(theta, rot_axis)
                    result_mat = np.matmul(rot_mat, _n + [1])
                    _dsi.update([_o, result_mat[:3]])

        def get_slabplanes(self):
            slabplanes = dict()
            for t in PLANETYPE:
                if hasattr(self, 'dsi_%s' % t):
                    _dsi = getattr(self, 'dsi_%s' % t)
                    slabplanes[t] = [_dsi.plane.GetOrigin(), _dsi.plane.GetNormal()]
            return slabplanes


    class CONTOUR:
        def __init__(self, actor, tpd, plane, slice_type, *args, **kwds):
            self.plane = plane
            self.slice_type = slice_type

            self.cutter = vtk.vtkCutter()

            if tpd:
                self.cutter.SetInputData(tpd.GetOutput())
            else:
                _mapper = actor.GetMapper()
                _poly_data = _mapper.GetInput()
                _tpd = vtk.vtkTransformPolyDataFilter()
                _transform = vtk.vtkTransform()
                _transform.SetMatrix(actor.GetUserMatrix())
                _tpd.SetTransform(_transform)
                _tpd.SetInputData(_poly_data)
                _tpd.Update()
                self.cutter.SetInputData(_tpd.GetOutput())
            self.cutter.SetCutFunction(self.plane)

            self.cutter_mapper = vtk.vtkPolyDataMapper2D()
            self.cutter_mapper.SetInputConnection(self.cutter.GetOutputPort())

            coordinate = vtk.vtkCoordinate()
            coordinate.SetCoordinateSystemToWorld()
            self.cutter_mapper.SetTransformCoordinate(coordinate)

            self.contour_actor = vtk.vtkActor2D()
            self.contour_actor.SetMapper(self.cutter_mapper)
            self.contour_actor.GetProperty().SetColor(actor.GetProperty().GetColor())
            self.contour_actor.GetProperty().SetLineWidth(1.5)

        def __del__(self):
            del self.contour_actor
            del self.plane
            del self.slice_type
            del self.cutter_mapper
            del self.cutter

        def get_actor(self):
            return self.contour_actor

        def update(self):
            self.contour_actor.Modified()

        def set_scarlar_visibility(self, is_show):
            self.cutter_mapper.SetScalarVisibility(is_show)
            self.filter.Update()
            self.cutter.Update()
            self.cutter_mapper.Update()
            self.contour_actor.Modified()


    """
    Outer Class
    """

    sig_update_slabplane = pyqtSignal(object)
    sig_refresh_all = pyqtSignal()

    def __init__(self, slice_type=None, *args, **kwds):
        super().__init__(*args, **kwds)

        self.l_btn_pressed = False
        self.r_btn_pressed = False

        """
        NOTE!!! Don't delete slice_type when doing reset()!!!!
        """
        if type(slice_type) is str \
                and (slice_type.lower() == 'coronal' or slice_type.lower() == "sagittal"
                     or slice_type.lower() == "axial"):
            self.slice_type = slice_type
        else:
            self.slice_type = None

        self.initialize()

    def initialize(self):
        # self.init_sub_renderer([0.75, 0, 1, 0.3])

        ISTYLES = cyVtkInteractorStyles.cyVtkInteractorStyles()
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

        # DSI
        self.guide_line = self.GUIDE_LINE_DSI(self.slice_type, self.slice_img.get_plane(), self.ren)

        # Picker
        self.picker_vol = vtk.vtkVolumePicker()
        self.picker_vol.PickFromListOn()
        self.picker_vol.InitializePickList()
        self.picker_vol.AddPickList(self.slice_img.get_actor())
        self.picker_dsi = vtk.vtkPropPicker()
        self.picker_dsi.PickFromListOn()
        self.picker_dsi.InitializePickList()
        self.picker_dsi.AddPickList(self.guide_line.get_actors()[-1])

        self.CONTOURS = {}

    def reset(self):
        self.ren.RemoveAllViewProps()

        def _remove(X):
            if type(X) is not dict:
                for o in X:
                    del o
            X.clear()

        if hasattr(self, 'slice_img'):
            del self.slice_img

        if hasattr(self, 'picker_vol'):
            del self.picker_vol

        if hasattr(self, 'picker_dsi'):
            del self.picker_dsi

        self.l_btn_pressed = False
        self.r_btn_pressed = False

        # NOTE!!! must call "super().reset()"
        super().reset()
        # and then, re initialize()
        self.initialize()

    def clear_all_actors(self):
        self.ren.RemoveAllViewProps()

    def set_vtk_img(self, vtk_img):
        assert vtk_img, 'vtk_img is invalid!!!'
        self.vtk_img = vtk_img
        self.slice_img.set_vtk_img(self.vtk_img)

        self.spacing = self.vtk_img.GetSpacing()

        # add actor to renderer, once
        if not self.slice_img.get_actor() in self.ren.GetActors():
            self.ren.AddViewProp(self.slice_img.get_actor())

        # add dsi actor
        for a in self.guide_line.get_actors():
            if not a in self.ren.GetActors():
                self.ren.AddViewProp(a)

        if self.slice_type == "axial":
            _params = [self.vtk_img.GetCenter(), np.array([0, 0, -1]), np.array([0, -1, 0]), CAM_SCALE_NORMAL]
        elif self.slice_type == "coronal":
            _params = [self.vtk_img.GetCenter(), np.array([0, -1, 0]), np.array([0, 0, 1]), CAM_SCALE_NORMAL]
        elif self.slice_type == "sagittal":
            _params = [self.vtk_img.GetCenter(), np.array([1, 0, 0]), np.array([0, 0, 1]), CAM_SCALE_NORMAL]
        else:
            _params = [self.vtk_img.GetCenter(), np.array([0, 0, -1]), np.array([0, -1, 0]), CAM_SCALE_NORMAL]

        # set plane and camera
        self.set_plane(_params[0], _params[1], _params[2], _camera_fit_type=1)
        self.set_camera_scale(_params[3])

    def set_camera_scale(self, scale):
        cam = self.ren.GetActiveCamera()
        cam.ParallelProjectionOn()
        B = self.slice_img.get_actor().GetMaxYBound() - self.slice_img.get_actor().GetMinYBound()
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

    def set_model(self, _model_actor):
        # TODO!! model test
        if 'model' in self.CONTOURS:
            _c = self.CONTOURS.pop('model')
            self.ren.RemoveActor(_c.get_actor())
            del _c
        _c = self.CONTOUR(actor=_model_actor, tpd=None, plane=self.slice_img.get_plane(), slice_type=self.slice_type)
        self.CONTOURS['model'] = _c
        self.ren.AddActor(_c.get_actor())

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

            obj_move = self.guide_line.get_actors()[-1]
            obj_rotate = None #self.guide_line.get_actors()[...] # TODO!!!
            if self.picker_dsi.Pick(x, y, 0, self.ren):
                if self.picker_dsi.GetActor2D() is obj_move:
                    self.guide_line.move_activated = True
                    self.guide_line.rotate_activated = False
                elif self.picker_dsi.GetActor2D() is obj_rotate:
                    renwin_size = self.ren.GetRenderWindow().GetSize()
                    if x / renwin_size[0] < 0.15 or x / renwin_size[0] > 0.85 or \
                            y / renwin_size[1] < 0.15 or y / renwin_size[1] > 0.85:
                        self.guide_line.move_activated = False
                        self.guide_line.rotate_activated = True
            # TEST
            else:
                renwin_size = self.ren.GetRenderWindow().GetSize()
                if x / renwin_size[0] < 0.15 or x / renwin_size[0] > 0.85 or \
                        y / renwin_size[1] < 0.15 or y / renwin_size[1] > 0.85:
                    self.guide_line.move_activated = False
                    self.guide_line.rotate_activated = True
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
        self.guide_line.move_activated = False
        self.guide_line.rotate_activated = False

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
            if self.guide_line.move_activated:
                self.picker_vol.Pick(x, y, 0, self.ren)
                pos = list(self.picker_vol.GetPickPosition())
                self.guide_line.move_handle(pos)
                slabplanes = self.guide_line.get_slabplanes()
                slabplanes['handle'] = pos
                self.sig_update_slabplane.emit(slabplanes)
            elif self.guide_line.rotate_activated:
                self.ren.SetWorldPoint(*self.guide_line.handle_sphere.GetCenter(), 1)
                self.ren.WorldToDisplay()
                origin_of_dsi = self.ren.GetDisplayPoint()
                vec_u = np.subtract([x, y, 1], origin_of_dsi)
                vec_v = np.subtract([prev_x, prev_y, 1], origin_of_dsi)
                theta = get_angle_between_vectors(vec_u, vec_v)
                sign = 1 if np.inner(np.cross(vec_v, vec_u), [0,0,1]) > 0 else -1
                rot_axis = np.array(self.get_plane()[1]) * sign
                self.guide_line.rotate_handle(theta, rot_axis)
                slabplanes = self.guide_line.get_slabplanes()
                slabplanes['camera_fit_type'] = 2   # TODO need to define by enum..?
                self.sig_update_slabplane.emit(slabplanes)

        elif self.r_btn_pressed:
            if _rwi.GetState() == vtk.VTKIS_WINDOW_LEVEL:
                self.sig_refresh_all.emit()
        else:
            obj_move = self.guide_line.get_actors()[-1]
            obj_rotate = None  # self.guide_line.get_actors()[...] # TODO!!!
            if self.picker_dsi.Pick(x, y, 0, self.ren):
                if self.picker_dsi.GetActor2D() is obj_move:
                    # QApplication.setOverrideCursor(QCursor(Qt.DragMoveCursor))
                    pass
            else:
                renwin_size = self.ren.GetRenderWindow().GetSize()
                if x / renwin_size[0] < 0.15 or x / renwin_size[0] > 0.85 or \
                        y / renwin_size[1] < 0.15 or y / renwin_size[1] > 0.85:
                    # QApplication.setOverrideCursor(QCursor(Qt.SizeAllCursor))
                    pass
                else:
                    # QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
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

        _sign = 1 if _event == r'MouseWheelForwardEvent' else -1
        _sign *= -1 if IS_OSX else 1
        _interval = 5 if _ctrl else 1

        thickness = self.spacing[2] if hasattr(self, 'spacing') else 0.2

        o, n = self.get_plane()
        o = list(np.array(o) + np.array(n) * (thickness * _interval * _sign))
        self.set_plane(o, n)

        handle_cen = self.guide_line.handle_sphere.GetCenter()
        handle_cen = list(np.array(handle_cen) + np.array(n) * (thickness * _interval * _sign))
        self.guide_line.move_handle(handle_cen)
        slabplanes = self.guide_line.get_slabplanes()
        slabplanes[self.slice_type] = [o, n]
        slabplanes['handle'] = handle_cen
        self.sig_update_slabplane.emit(slabplanes)

    def update_slabplane(self, slabplanes):
        plane = slabplanes.get(self.slice_type)
        camera_fit_type = slabplanes.get('camera_fit_type')
        if plane:
            self.set_plane(plane[0], plane[1], _camera_fit_type=camera_fit_type)
        self.guide_line.update(slabplanes)

    def refresh(self):
        # if hasattr(self, 'guide_line'):
        #     self.guide_line.update()
        # if hasattr(self, '_CONTOURS'):
        #     for _c in self._CONTOURS:
        #         _c.update()
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

    # def get_project_info(self):
    #     info = dict()
    #     info["Type"] = self.slice_type
    #     info["Thickness"] = self.get_thickness()
    #     info["Filter"] = self.image_filter_type if hasattr(self, 'image_filter_type') else 'None'
    #     return info
