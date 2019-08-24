import math, time
import enum
import vtk
import numpy as np
from vtk.util import numpy_support
from PyQt5.QtCore import QObject, pyqtSignal

from COMMON import pt_on_plane, get_angle_between_vectors, get_rotation_matrix, get_vtkmat_from_list
from COMMON import intersection_of_two_planes, intersection_of_two_lines

# from _IN2GUIDE_DENTAL.blocks._CYTHON_PACKAGES import cy_probe

COLOR_ACTIVE = (0/255, 255/255, 255/255)
COLOR_NORMAL = (0/255, 255/255, 0/255)


class E_MEASURE(enum.Enum):
    NONE = enum.auto()
    RULER = enum.auto()
    TAPELINE = enum.auto()
    ANGLE3 = enum.auto()
    ANGLE4 = enum.auto()
    AREA = enum.auto()
    ARROW = enum.auto()


class Measure(QObject):

    def __init__(self, ren, target_actor):
        super().__init__()

        self.current_measures_idx = -1
        self.current_marker = None

        self.remove_actor = False
        self.screen_pos = []

        self.ren = ren

        self.measure_list = []

        self._picked_actor = None
        self.picker_for_marker = vtk.vtkPropPicker()
        self.picker_for_marker.PickFromListOn()

        self.mode = None
        self.complete_measure = False

        self.current_text_actor = None
        self.vtk_img = None

        self._picked_note_actor = None

        self.prev_time = time.time()

    def set_vtk_img_for_measure(self, _vtk_img):
        self.vtk_img = _vtk_img

    def set_activation(self, _mode):
        if _mode in E_MEASURE:
            self.mode = _mode
        else:
            self.mode = E_MEASURE.NONE

    def create_new_measure(self):
        if self.mode == E_MEASURE.RULER:
            m = MeasureRuler()
        else:
            return
        # elif self.EventMode == self.MeasureType.MEASURE_TAPELINE:
        #     m = Measure_Tapeline(self.slice_type)
        # elif self.EventMode == self.MeasureType.MEASURE_ANGLE:
        #     m = Measure_Angle(self.slice_type)
        # elif self.EventMode == self.MeasureType.MEASURE_AREA:
        #     m = Measure_Area(self.slice_type)
        # elif self.EventMode == self.MeasureType.MEASURE_PROFILE:
        #     m = Measure_Profile(self.slice_type)
        # elif self.EventMode == self.MeasureType.MEASURE_ANGLE_4PT:
        #     m = Measure_Angle_4Pt(self.slice_type)
        # elif self.EventMode == self.MeasureType.MEASURE_NOTE:
        #     m = Measure_Note(self.slice_type)
        #
        self.ren.SetDisplayPoint(0, 0, 0)
        self.ren.DisplayToWorld()
        p0 = self.ren.GetWorldPoint()
        self.ren.SetDisplayPoint(7, 7, 0)
        self.ren.DisplayToWorld()
        p1 = self.ren.GetWorldPoint()
        distance = np.linalg.norm(np.subtract(p1, p0))
        m.set_scale(distance)

        self.measure_list.append(m)
        self.current_measures_idx = self.measure_list.index(m)
        self.ren.AddViewProp(self.measure_list[self.current_measures_idx].line_actor)

    def reset_all(self):
        for m in self.measure_list:
            self.ren.RemoveViewProp(m.line_actor)
            if len(m.text_actor) > 0:
                for ta in m.text_actor:
                    self.ren.RemoveViewProp(ta)
            for n in m.M:
                self.ren.RemoveViewProp(n)
            del m
        self.current_measures_idx = -1
        self.measure_list.clear()

        # NOTE To reset 'InitializePickList' should be called.
        self.picker_for_marker.InitializePickList()

    def mouse_press(self, rwi, event):

        if self.mode is None or self.mode is E_MEASURE.NONE:
            return

        i = rwi.GetInteractor()
        x, y = i.GetEventPosition()
        if event == "LeftButtonPressEvent":

            self.ren.SetDisplayPoint(x, y, 0)
            self.ren.DisplayToWorld()
            pos = self.ren.GetWorldPoint()

            self.picker_for_marker.Pick(x, y, 0, self.ren)
            self._picked_actor = self.picker_for_marker.GetActor2D()

            if self._picked_actor:
                for i, n in enumerate(self.measure_list):
                    if self._picked_actor in n.M:
                        self.current_marker = n.M[self._picked_actor]
                        self.current_measures_idx = i
                        break
                    elif self._picked_actor in n.text_actor:
                        self._picked_note_actor = n.text_actor[0]
                        self.current_measures_idx = i
                        self._picked_actor = None
                        break
            else:
                if len(self.measure_list) == 0:
                    self.create_new_measure()
                self.current_measures_idx = len(self.measure_list) - 1
                marker = list(self.measure_list[self.current_measures_idx]._mark(pos))
                self.ren.AddViewProp(marker[2])
                self.picker_for_marker.AddPickList(marker[2])
                self.measure_list[self.current_measures_idx].append_marker(marker)
                if self.measure_list[self.current_measures_idx].action():
                    self.complete_measure = True
                    self.create_new_measure()
                else:
                    _txt_actor = self.measure_list[self.current_measures_idx].text_actor[-1]
                    if not _txt_actor in self.ren.GetActors():
                        self.ren.AddViewProp(_txt_actor)
        else:
            pass

    def mouse_move(self, rwi, event):

        if self.mode is None or self.mode is E_MEASURE.NONE:
            return

        if self.current_measures_idx == -1 or len(self.measure_list[self.current_measures_idx].M) == 0:
            return

        i = rwi.GetInteractor()
        x, y = i.GetEventPosition()

        self.ren.SetDisplayPoint(x, y, 0)
        self.ren.DisplayToWorld()
        pos = self.ren.GetWorldPoint()[:3]

        if self._picked_actor:
            if self._picked_actor in self.measure_list[self.current_measures_idx].M:
                self.current_marker[0].SetCenter(pos)
                self.current_marker[0].Update()
                self.current_marker[1].Update()
                self.measure_list[self.current_measures_idx].draw_line()
                self.measure_list[self.current_measures_idx].draw_text()
        elif self._picked_note_actor:
            self.measure_list[self.current_measures_idx].modify_text_actor(pos)
        else:
            self.measure_list[self.current_measures_idx].moving(pos)

    def mouse_release(self, rwi, event):
        self._picked_actor = None
        self._picked_note_actor = None
        self.current_measures_idx = len(self.measure_list) - 1

    def resize(self, w, h):
        self.ren.SetDisplayPoint(0, 0, 0)
        self.ren.DisplayToWorld()
        p0 = self.ren.GetWorldPoint()
        self.ren.SetDisplayPoint(7, 7, 0)
        self.ren.DisplayToWorld()
        p1 = self.ren.GetWorldPoint()
        distance = np.linalg.norm(np.subtract(p1, p0))
        for m in self.measure_list:
            m.set_scale(distance)
            m.refesh_handle()


class MeasureBase(QObject):
    def __init__(self):
        super().__init__()
        self.complete = False
        self.M = {}
        self.text_actor = []
        self.P = []
        self.index = 0
        self.name = ""
        self.scale = 1

        self.points = vtk.vtkPoints()
        self.poly_line = vtk.vtkPolyLine()
        self.cells = vtk.vtkCellArray()
        self.poly_data = vtk.vtkPolyData()

        coordinate = vtk.vtkCoordinate()
        coordinate.SetCoordinateSystemToWorld()

        self.line_mapper = vtk.vtkPolyDataMapper2D()
        self.line_mapper.SetInputData(self.poly_data)
        self.line_actor = vtk.vtkActor2D()
        self.line_actor.SetMapper(self.line_mapper)
        self.line_actor.GetProperty().SetColor(COLOR_NORMAL)

        self.line_mapper.SetTransformCoordinate(coordinate)

    def __del__(self):
        self.clear_all()
        del self.points
        del self.poly_line
        del self.cells
        del self.poly_data
        del self.line_mapper
        del self.line_actor

    def clear_all(self):
        for m in self.M.keys():
            del self.M[m][1]
            del self.M[m][0]
            del m
        self.M.clear()

    def set_scale(self, scale):
        self.scale = scale

    def _mark(self, pos_marker):
        mark_source = vtk.vtkSphereSource()
        mark_source.SetCenter(pos_marker[0], pos_marker[1], pos_marker[2])
        mark_source.SetThetaResolution(36)
        mark_source.SetRadius(self.scale/2)
        mark_mapper = vtk.vtkPolyDataMapper2D()
        mark_mapper.SetInputConnection(mark_source.GetOutputPort())

        mark_actor = vtk.vtkActor2D()
        mark_actor.SetMapper(mark_mapper)
        mark_actor.GetProperty().SetColor(COLOR_NORMAL)

        coordinate = vtk.vtkCoordinate()
        coordinate.SetCoordinateSystemToWorld()

        mark_mapper.SetTransformCoordinate(coordinate)

        return mark_source, mark_mapper, mark_actor

    def append_marker(self, _mark):
        _k, _v = _mark[2], [_mark[0], _mark[1]]
        self.M[_k] = _v

    def get_point_data(self):
        self.P = [[*self.M[key][0].GetCenter()] for key in self.M]

    def refesh_handle(self):
        for k, v in self.M.items():
            v[0].SetRadius(self.scale/2)
            v[0].Update()
            v[1].Update()
            k.Modified()

class MeasureRuler(MeasureBase):
    def __init__(self):
        super().__init__()

        self.name = "ruler"

    def draw_line(self):
        self.get_point_data()
        self.points.Reset()
        self.poly_data.Reset()
        for p in self.P:
            self.points.InsertNextPoint(p)

        self.poly_line.GetPointIds().SetNumberOfIds(len(self.P))
        for i in range(len(self.P)):
            self.poly_line.GetPointIds().SetId(i, i)
        self.cells.InsertNextCell(self.poly_line)
        self.poly_data.SetPoints(self.points)
        self.poly_data.SetLines(self.cells)

        self.line_mapper.Update()

    def update_line(self, pos):
        self.get_point_data()
        self.points.Reset()
        self.poly_data.Reset()
        self.points.InsertNextPoint(self.P[0])
        self.points.InsertNextPoint(pos[:3])
        self.poly_line.GetPointIds().SetNumberOfIds(len(self.P)+1)
        self.poly_line.GetPointIds().SetId(0, 0)
        self.poly_line.GetPointIds().SetId(1, 1)
        self.cells.InsertNextCell(self.poly_line)
        self.poly_data.SetPoints(self.points)
        self.poly_data.SetLines(self.cells)
        self.line_mapper.Update()

    def modify_text_actor(self, _pos, _idx):
        text_actor = self.text_actor[_idx]
        coord = text_actor.GetPositionCoordinate()
        coord.SetCoordinateSystemToWorld()
        coord.SetValue(_pos[0], _pos[1], _pos[2])

    def draw_text(self, pos=None, distance=None):
        if distance is None:
            distance = self.calculation_ruler(pos)
        if len(self.text_actor) < 1:
            text_actor = vtk.vtkTextActor()
            text_actor.SetInput(str(distance) + "mm")
            text_actor.GetTextProperty().SetFontSize(15)
            text_actor.GetTextProperty().SetColor([175 / 255, 238 / 255, 238 / 255])
            text_actor.GetTextProperty().SetVerticalJustificationToCentered()
            text_actor.GetTextProperty().SetJustificationToCentered()
            text_actor.GetTextProperty().SetBackgroundColor(0.2, 0.3, 0.4)
            text_actor.GetTextProperty().SetBackgroundOpacity(0.6)
            text_actor.GetTextProperty().UseTightBoundingBoxOn()

            self.text_actor.append(text_actor)
        else:
            text_actor = self.text_actor[0]
            text_actor.SetInput(str(distance) + "mm")

        if pos is None:
            p0 = (self.P[0][0] + self.P[1][0]) / 2
            p1 = (self.P[0][1] + self.P[1][1]) / 2
            p2 = (self.P[0][2] + self.P[1][2]) / 2
        else:
            p0 = (pos[0] + self.P[0][0]) / 2
            p1 = (pos[1] + self.P[0][1]) / 2
            p2 = (pos[2] + self.P[0][2]) / 2

        coord = text_actor.GetPositionCoordinate()
        coord.SetCoordinateSystemToWorld()
        coord.SetValue(p0 + 1, p1 + 1, p2 + 1)

        text_actor.GetProperty().SetColor(COLOR_NORMAL)

    def calculation_ruler(self, pos=None):
        UNITS = [1, 1, 1]
        if pos is None:
            distance = round(math.sqrt(math.pow((self.P[1][0] - self.P[0][0]) * UNITS[0], 2) +
                                       math.pow((self.P[1][1] - self.P[0][1]) * UNITS[1], 2) +
                                       math.pow((self.P[1][2] - self.P[0][2]) * UNITS[2], 2)), 2)
        else:
            distance = round(math.sqrt(math.pow((pos[0] - self.P[0][0]) * UNITS[0], 2) +
                                       math.pow((pos[1] - self.P[0][1]) * UNITS[1], 2) +
                                       math.pow((pos[2] - self.P[0][2]) * UNITS[2], 2)), 2)

        return distance

    def action(self):
        """
        :return: return true if action is completed
        """
        if len(self.M) == 2:
            self.complete = True
            self.draw_line()
            self.draw_text()
            return True

        if len(self.text_actor) < 1:
            text_actor = vtk.vtkTextActor()
            text_actor.SetInput(str(0) + "mm")
            text_actor.GetTextProperty().SetFontSize(15)
            text_actor.GetTextProperty().SetColor([175 / 255, 238 / 255, 238 / 255])
            text_actor.GetTextProperty().SetVerticalJustificationToCentered()
            text_actor.GetTextProperty().SetJustificationToCentered()
            text_actor.GetTextProperty().SetBackgroundColor(0.2, 0.3, 0.4)
            text_actor.GetTextProperty().SetBackgroundOpacity(0.6)
            text_actor.GetTextProperty().UseTightBoundingBoxOn()

            self.text_actor.append(text_actor)
        else:
            text_actor = self.text_actor[0]
            text_actor.SetInput(str(0) + "mm")

        return False

    def moving(self, pos):
        num_of_points = len(self.M)
        if num_of_points == 1:
            self.update_line(pos)
            self.draw_text(pos)
