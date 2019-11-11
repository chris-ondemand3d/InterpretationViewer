import sys, os
import vtk
import numpy as np
from vtk.util import numpy_support
from vtk.numpy_interface import dataset_adapter as dsa
import math
from _qapp import create_task
# from cyhub.block import Block_meta
from cyhub.cy_vtk import Vtk_image_holder

from cyCafe import cyBoostConversion
from cyCafe import cyPCMLoader
from cyCafe import cyVtkImageResliceMapper


# cube source
# MINI_PATH, MINI_SCALE, MINI_ROTATE = None, 5, 0
# mario
# MINI_PATH, MINI_SCALE, MINI_ROTATE = r"./stl/mario.stl", 200, 90
# bob(minions)
# MINI_PATH, MINI_SCALE, MINI_ROTATE = r"./stl/minions bob.stl", 350, 90
# stuart(minions)
# MINI_PATH, MINI_SCALE, MINI_ROTATE = r"./stl/minions stuart.stl", 200, 90
# gaonasi
# MINI_PATH, MINI_SCALE, MINI_ROTATE = r"./stl/gaonasi.stl", 3500, 95
# spiderman
# MINI_PATH, MINI_SCALE, MINI_ROTATE = r"./stl/spiderman.stl", 200, 90
# ironman
# MINI_PATH, MINI_SCALE, MINI_ROTATE = r"./stl/Ironman.stl", 600, 17
# groot
# MINI_PATH, MINI_SCALE, MINI_ROTATE = r"./stl/babygroot.stl", 250, 0
# Unicorn
# MINI_PATH, MINI_SCALE, MINI_ROTATE = r"./stl/Unicorn.stl", 180, 90
# Man
# MINI_PATH, MINI_SCALE, MINI_ROTATE = r"./stl/M.stl", 800, 0
# Dog
# MINI_PATH, MINI_SCALE, MINI_ROTATE = r"./stl/Dog.stl", 130, 90
# Woman
# MINI_PATH, MINI_SCALE, MINI_ROTATE = r"./stl/woman.stl", 50, 90
# Tooth
# MINI_PATH, MINI_SCALE, MINI_ROTATE, MINI_AXIS = r"./stl/tooth.stl", 8.5, 180, 'Z'
# Man
# MINI_PATH, MINI_SCALE, MINI_ROTATE, MINI_AXIS = r"./stl/man.stl", 110, 0, 'Z'
# Female
# MINI_PATH, MINI_SCALE, MINI_ROTATE, MINI_AXIS = r"./stl/female.stl", 6.5, 0, 'Z'
# Tooth2
MINI_PATH, MINI_SCALE, MINI_ROTATE, MINI_AXIS = r"./stl/TEETH_01.stl", 3.5, 90, 'X'


class I2G_IMG_HOLDER(Vtk_image_holder):

    class MINIMI:
        def __init__(self):
            if MINI_PATH is None:
                # Cube Source
                self.source = vtk.vtkCubeSource()
            else:
                _path = get_bundle_path()
                _path = os.path.join(_path, MINI_PATH) if _path else MINI_PATH

                # STL
                self.source = vtk.vtkSTLReader()
                self.source.SetFileName(_path)

            self.mapper = vtk.vtkPolyDataMapper()
            self.mapper.SetInputConnection(self.source.GetOutputPort())
            self.actor = vtk.vtkActor()
            self.actor.SetMapper(self.mapper)
            # self.actor.GetProperty().SetRepresentationToWireframe()

            if MINI_PATH is None:
                self.actor.GetProperty().SetRepresentationToWireframe()
            else:
                if 'MINI_AXIS' in globals():
                    _FN_ROT = getattr(self.actor, 'Rotate' + MINI_AXIS)
                else:
                    _FN_ROT = self.actor.RotateX
                _FN_ROT(MINI_ROTATE)

            # self.init_materials()

        def __del__(self):
            del self.actor
            del self.mapper
            del self.source

        def get_actor(self):
            return self.actor

        def init_materials(self):
            # color = (97 / 255, 51 / 255, 24 / 255)
            # color = (119 / 255, 20 / 255, 20 / 255)
            # color = (0.2, 0.3, 0.4)
            color = (1.0, 1.0, 1.0)
            self.actor.GetProperty().SetColor(color)
            self.actor.GetProperty().SetAmbient(0.3)
            self.actor.GetProperty().SetAmbientColor([0.2, 0.2, 0.2])
            self.actor.GetProperty().SetDiffuse(0.6)
            self.actor.GetProperty().SetDiffuseColor(color)
            self.actor.GetProperty().SetSpecular(1)
            self.actor.GetProperty().SetSpecularPower(10)
            # self.actor.GetProperty().SetSpecularColor([0.6, 0.2, 0.1])
            # self.actor.GetProperty().SetSpecularColor([0.8, 0.1, 0.1])
            self.actor.GetProperty().SetSpecularColor([0.8, 0.8, 0.8])

        def visible(self, visible):
            self.actor.SetVisibility(visible)


    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.vtk_img = None

        self.BG_COLOR = [0.0, 0.0, 0.0]
        self.ren.SetBackground(self.BG_COLOR)

    def clear(self, _refresh=True):
        if hasattr(self, 'ren'):
            self.ren.RemoveAllViewProps()
        if hasattr(self, 'ren2'):
            self.ren2.RemoveAllViewProps()

        if _refresh:
            self.refresh()

    def reset(self):
        if hasattr(self, 'vtk_img'):
            del self.vtk_img
        self.vtk_img = None

        if hasattr(self, 'camera'):
            del self.camera

        if hasattr(self, 'ren2'):
            self.ren2.RemoveAllViewProps()
            self.ren2.Clear()
            del self.ren2

        if hasattr(self, 'minimi'):
            del self.minimi

        try:
            self.sig_resize.disconnect(self.__resized)
        except TypeError as e:
            print("*** CATCH *** " + str(e))

        # TODO!!!!!!!!!!!!
        # is the Clear() better way than reset() ???
        super().reset()
        # self.ren.Clear()
        # and then, re-set bg color
        self.ren.SetBackground(self.BG_COLOR)
        if hasattr(self, "BG_COLOR2"):
            self.ren.SetBackground2(self.BG_COLOR2)
            self.ren.SetGradientBackground(True)

    def refresh(self):
        super().refresh()

    def init_sub_renderer(self, _visible=False, _size=(0.8, 0, 1, 0.25)):
        # viewport size (xmin, ymin, xmax, ymax)
        size = _size

        # Renderer Setting
        self.view._RenderWindow.SetNumberOfLayers(2)

        # Main Renderer
        self.ren.SetLayer(0)
        self.ren.SetViewport(0, 0, 1, 1)

        # Sub Renderer for Minimi (Right-Bottom)
        self.ren2 = vtk.vtkRenderer()
        self.ren2.SetLayer(1)
        self.view._RenderWindow.AddRenderer(self.ren2)
        self.ren2.SetViewport(size)
        # transparent renderer
        self.ren2.SetPreserveColorBuffer(1)
        # only for observer interactor
        self.ren2.SetInteractive(False)

        # creation
        # Minimi
        self.minimi = self.MINIMI()
        self.ren2.AddViewProp(self.minimi.get_actor())
        self.minimi.visible(_visible)
        # default camera setting to look front of minimi
        cam = self.ren.GetActiveCamera()
        cam.SetViewUp(0, 0, 1)
        cam.SetFocalPoint(0, 0, 0)
        cam.SetPosition(0, -1, 0)
        self.sync_cameras()

        # connect resize sig to slot
        self.sig_resize.connect(self.__resized)

    def set_depthpeeling(self, isOn):
        # Depth Peeling
        self.view._RenderWindow.SetAlphaBitPlanes(1)
        self.view._RenderWindow.SetMultiSamples(0)
        self.ren.SetUseDepthPeeling(isOn)
        self.ren.SetUseDepthPeelingForVolumes(isOn)
        # self.ren.SetMaximumNumberOfPeels(100)
        # self.ren.SetOcclusionRatio(0.01)

    """
    Renderer2
    """
    def sync_cameras(self):
        if not hasattr(self, 'minimi'):
            return False

        if not hasattr(self, 'camera'):
            self.camera = self.ren.GetActiveCamera()

        up_vec = self.camera.GetViewUp()
        p = self.camera.GetPosition()
        f = self.camera.GetFocalPoint()

        scale = MINI_SCALE
        view_vec = np.subtract(p, f)
        view_vec = view_vec / np.linalg.norm(view_vec) * scale
        # o = self.ren2.GetActors().GetItemAsObject(0).GetCenter()
        o = self.minimi.get_actor().GetCenter()
        self.ren2.GetActiveCamera().SetFocalPoint(o)
        self.ren2.GetActiveCamera().SetPosition(o + view_vec)
        self.ren2.GetActiveCamera().SetViewUp(up_vec)
        #         self.ren2.ResetCamera()
        self.ren2.ResetCameraClippingRange()

    def __resized(self):
        if hasattr(self, 'ren2'):
            self.sync_cameras()


class PolyData:
    def __init__(self, path, filter_type=None, *args, **kwds):
        self.tpd = vtk.vtkTransformPolyDataFilter()
        self.t = vtk.vtkTransform()
        self.t.Identity()
        self.tpd.SetTransform(self.t)
        self.tpd.AddObserver('EndEvent', self.on_update)
        self.mapper = vtk.vtkPolyDataMapper()

        self.filter_type = filter_type
        if self.filter_type == 'smooth':
            self.filter = vtk.vtkSmoothPolyDataFilter()
            self.filter.SetInputData(self.tpd.GetOutput())
            self.filter.SetNumberOfIterations(50)
            self.normals = vtk.vtkPolyDataNormals()
            self.normals.SetInputData(self.filter.GetOutput())
            self.normals.FlipNormalsOn()
            self.mapper.SetInputData(self.normals.GetOutput())
        elif self.filter_type == 'decimate':
            self.filter = vtk.vtkDecimatePro()
            self.filter.SetInputData(self.tpd.GetOutput())
            self.filter.SetTargetReduction(0.5)
            self.filter.PreserveTopologyOn()
            self.normals = vtk.vtkPolyDataNormals()
            self.normals.SetInputData(self.filter.GetOutput())
            self.normals.FlipNormalsOn()
            self.mapper.SetInputData(self.normals.GetOutput())
        else:
            self.mapper.SetInputData(self.tpd.GetOutput())

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)

        # To prevent crash.
        _mat = vtk.vtkMatrix4x4()
        _mat.Identity()
        self.actor.SetUserMatrix(_mat)

        # init from stl or pcm
        if path[-3:] == 'stl':
            self.init_from_stl(path)
        elif path[-3:] == 'ply':
            self.init_from_ply(path)
        elif path[-3:] == 'pcm':
            self.init_from_pcm(path)

    def init_from_stl(self, stl_path):
        self.reader = vtk.vtkSTLReader()
        self.reader.SetFileName(stl_path)
        self.reader.Update()

        self.tpd.SetInputData(self.reader.GetOutput())
        self.tpd.Update()

    def init_from_ply(self, stl_path):
        self.reader = vtk.vtkPLYReader()
        self.reader.SetFileName(stl_path)
        self.reader.Update()

        self.tpd.SetInputData(self.reader.GetOutput())
        self.tpd.Update()

    def init_from_pcm(self, pcm_path):
        vertexlist = list()
        facelist = list()

        pcmloader = cyPCMLoader.cyPCMLoader()
        pcmloader.loadpcmfile(pcm_path)

        pcmloader.getVertex(vertexlist)
        pcmloader.getFace(facelist)

        numberOfFaces = len(facelist)

        points = vtk.vtkPoints()
        for i in range(len(vertexlist)):
            points.InsertNextPoint(vertexlist[i])

        dodechedronFacesIdList = vtk.vtkIdList()
        dodechedronFacesIdList.InsertNextId(numberOfFaces)

        for face in facelist:
            dodechedronFacesIdList.InsertNextId(len(face))
            [dodechedronFacesIdList.InsertNextId(i) for i in face]

        uGrid = vtk.vtkUnstructuredGrid()
        uGrid.InsertNextCell(vtk.VTK_POLYHEDRON, dodechedronFacesIdList)
        uGrid.SetPoints(points)

        surfaceFilter = vtk.vtkDataSetSurfaceFilter()
        surfaceFilter.SetInputData(uGrid)
        surfaceFilter.Update()

        self.tpd.SetInputData(surfaceFilter.GetOutput())
        self.tpd.Update()

    def on_update(self, _o, _e):
        if self.filter_type:
            self.filter.Update()
            self.normals.Update()

    def __del__(self):
        del self.actor
        del self.mapper
        if hasattr(self, 'reader'):
            del self.reader
        del self.tpd
        del self.t
        if hasattr(self, 'filter'):
            del self.filter
        if hasattr(self, 'normals'):
            del self.normals

    def get_actor(self):
        return self.actor

    def get_tpd(self):
        return self.tpd

    def set_color(self, color):
        self.actor.GetProperty().SetColor(color)

    def set_opacity(self, opacity):
        self.actor.GetProperty().SetOpacity(opacity)

    def set_material_preset(self):
        color = [0.9, 0.9, 0]
        self.actor.GetProperty().SetColor(color)
        self.actor.GetProperty().SetAmbient(0.3)
        self.actor.GetProperty().SetAmbientColor([0.2, 0.2, 0.2])
        self.actor.GetProperty().SetDiffuse(0.5)
        self.actor.GetProperty().SetDiffuseColor(color)
        self.actor.GetProperty().SetSpecular(1)
        self.actor.GetProperty().SetSpecularPower(10)
        self.actor.GetProperty().SetSpecularColor([0.9, 0.9, 0.1])

    def transform(self, angle, axis, move=[0,0,0]):
        _result_mat = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        _v = np.multiply(axis, math.sin(angle / 2))
        vtk.vtkMath.QuaternionToMatrix3x3([math.cos(angle / 2), _v[0], _v[1], _v[2]], _result_mat)

        _mat = get_vtkmat_from_list([_result_mat[0][0], _result_mat[0][1], _result_mat[0][2], move[0],
                                     _result_mat[1][0], _result_mat[1][1], _result_mat[1][2], move[1],
                                     _result_mat[2][0], _result_mat[2][1], _result_mat[2][2], move[2],
                                      0, 0, 0, 1])


        _t = self.tpd.GetTransform()
        __m = vtk.vtkMatrix4x4()
        __m.DeepCopy(_t.GetMatrix())
        __m2 = _mat
        __m3 = vtk.vtkMatrix4x4()
        vtk.vtkMatrix4x4.Multiply4x4(__m2, __m, __m3)
        _t.SetMatrix(__m3)
        _t.Update()
        self.tpd.Update()


class GeomScene:
    def __init__(self, _geom, _matrix, _infos):
        self.parent = None
        self.geom = _geom
        self.geom_scenes = []

        self.type = _infos.pop('Type') if 'Type' in _infos else None
        self.transform = _matrix
        self.infos = _infos

        # Set Transforms
        if _geom:
            self.geom.get_actor().SetUserMatrix(self.transform)

    def __del__(self):
        del self.geom

        for g in self.geom_scenes:
            del g
        del self.geom_scenes

    def add_geom_scene(self, _geom_scene):
        _geom_scene.parent = self
        self.geom_scenes.append(_geom_scene)

        # Set Transform
        if _geom_scene.geom:
            _geom_scene.geom.get_actor().SetUserMatrix(_geom_scene.get_transform_from_top())

    def get_transform_from_top(self):
        if self.parent is None:
            return self.transform
        else:
            mat1 = self.parent.get_transform_from_top()
            mat2 = self.transform
            mat3 = vtk.vtkMatrix4x4()
            vtk.vtkMatrix4x4.Multiply4x4(mat1, mat2, mat3)
            return mat3

    def find(self, type):
        result = []
        for scene in self.geom_scenes:
            if scene.type == type:
                result.append(scene)

        for scene in self.geom_scenes:
            result += scene.find(type)

        return result


class Sphere:
    def __init__(self, pos=[0,0,0], radius=1, color=[1,0,0], opacity=1):
        self.pos = pos
        self.s = vtk.vtkSphereSource()
        self.s.SetCenter(pos)
        self.s.SetRadius(radius)
        self.s.Update()
        self.m = vtk.vtkPolyDataMapper()
        self.m.SetInputData(self.s.GetOutput())
        self.m.Update()
        self.a = vtk.vtkActor()
        self.a.SetMapper(self.m)
        self.a.GetProperty().SetColor(color)
        self.a.GetProperty().SetOpacity(opacity)

    def __del__(self):
        del self.a
        del self.m
        del self.s
        del self.pos

    def get_actor(self):
        return self.a

    def set_position(self, pos):
        self.pos = pos
        self.s.SetCenter(pos)
        self.s.Update()
        self.m.Update()
        self.a.Modified()


class Sphere2D:
    def __init__(self, pos=[0,0,0], radius=1, color=[1,0,0], opacity=1):
        self.pos = pos
        self.s = vtk.vtkSphereSource()
        self.s.SetCenter(pos)
        self.s.SetRadius(radius)
        self.s.Update()
        self.m = vtk.vtkPolyDataMapper2D()
        self.m.SetInputData(self.s.GetOutput())
        self.m.Update()
        self.a = vtk.vtkActor2D()
        self.a.SetMapper(self.m)
        self.a.GetProperty().SetColor(color)
        self.a.GetProperty().SetOpacity(opacity)

        coordinate = vtk.vtkCoordinate()
        coordinate.SetCoordinateSystemToWorld()
        self.m.SetTransformCoordinate(coordinate)

    def __del__(self):
        del self.a
        del self.m
        del self.s
        del self.pos

    def get_actor(self):
        return self.a

    def set_position(self, pos):
        self.pos = pos
        self.s.SetCenter(pos)
        self.s.Update()
        self.m.Update()
        self.a.Modified()


class Glyph3D:
    def __init__(self, pts=None, radius=1, color=[1,0,0]):
        self.pts = pts
        # _vpts = vtk.vtkPoints()
        # _vpts.SetData(dsa.numpyTovtkDataArray(pts))
        # _subsampled = vtk.vtkStructuredGrid()
        # _subsampled.SetPoints(_vpts)
        self.sphere_source = vtk.vtkSphereSource()
        self.sphere_source.SetRadius(radius)
        self.glyp = vtk.vtkGlyph3D()
        self.glyp.ScalingOff()
        self.glyp.SetSourceConnection(self.sphere_source.GetOutputPort())
        # self.glyp.SetInputData(_subsampled)
        # self.glyp.Update()
        self.polymapper = vtk.vtkPolyDataMapper()
        self.polymapper.SetInputData(self.glyp.GetOutput())
        self.polyactor = vtk.vtkActor()
        self.polyactor.SetMapper(self.polymapper)

    def get_actor(self):
        return self.polyactor

    def set_pts(self, pts):
        self.pts = pts
        _vpts = vtk.vtkPoints()
        _vpts.SetData(dsa.numpyTovtkDataArray(np.asarray(pts)))
        _subsampled = vtk.vtkStructuredGrid()
        _subsampled.SetPoints(_vpts)
        self.glyp.SetInputData(_subsampled)
        self.glyp.Update()
        self.polymapper.Update()
        self.polyactor.Modified()


class CurveLine:
    def __init__(self, _LINES, fn_coord_convert=None):
        if fn_coord_convert:
            for i, n in enumerate(_LINES):
                _LINES[i] = fn_coord_convert(n)
        self.L = _LINES

        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()
        points.SetNumberOfPoints(len(self.L))
        for i, _p in enumerate(self.L):
            points.SetPoint(i, *_p)
            if i == 0:
                lines.InsertNextCell(len(self.L))
            lines.InsertCellPoint(i)

        polygon = vtk.vtkPolyData()
        polygon.SetPoints(points)
        polygon.SetLines(lines)
        polygonMapper = vtk.vtkPolyDataMapper()
        polygonMapper.SetInputData(polygon)
        polygonMapper.Update()
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(polygonMapper)

    def __del__(self):
        del self.actor
        del self.L

    def get_actor(self):
        return self.actor

    def set_color(self, color):
        self.actor.GetProperty().SetColor(color)

    def set_width(self, width):
        self.actor.GetProperty().SetLineWidth(width)


class CurveLineTube:
    def __init__(self, _LINES, fn_coord_convert=None):
        if fn_coord_convert:
            # TODO!!!! Temporarily... :(
            __prev_x = -999999
            _L = []
            for n in _LINES:
                _x, _y, _z = fn_coord_convert(n)
                if _x != __prev_x:
                    _L.append([_x, _y, _z])
                __prev_x = _x
            _LINES = _L
        self.L = _LINES
        self.actor = vtk.vtkActor()

        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()
        points.SetNumberOfPoints(len(self.L))
        for i, _p in enumerate(self.L):
            points.SetPoint(i, *_p)
            if i == 0:
                lines.InsertNextCell(len(self.L))
            lines.InsertCellPoint(i)

        self.polygon = vtk.vtkPolyData()
        self.polygon.SetPoints(points)
        self.polygon.SetLines(lines)

        self.tube = vtk.vtkTubeFilter()
        self.tube.SetInputData(self.polygon)
        self.tube.SetNumberOfSides(100)
        self.tube.Update()

        self.tubeMapper = vtk.vtkPolyDataMapper()
        self.tubeMapper.SetInputConnection(self.tube.GetOutputPort())
        self.actor.SetMapper(self.tubeMapper)

    def __del__(self):
        del self.L
        del self.actor
        del self.tubeMapper
        del self.tube
        del self.polygon

    def get_actor(self):
        return self.actor

    def set_color(self, color):
        self.actor.GetProperty().SetColor(color)

    def set_radius(self, radius):
        self.tube.SetRadius(radius)
        self.tube.Update()
        self.tubeMapper.Update()
        self.actor.Modified()


class AxisLine:
    def __init__(self, _T):
        self.s = vtk.vtkArrowSource()
        self.s.SetShaftResolution(100)
        self.s.SetShaftRadius(0.3)
        self.s.SetTipResolution(100)
        self.s.SetTipLength(0.04)
        self.s.SetTipRadius(1)
        self.s.Update()
        mat = vtk.vtkMatrix4x4()
        mat.Identity()
        t = vtk.vtkTransform()
        t.Translate(0, 0, 20)
        t.RotateY(90)
        t.Concatenate(mat)
        t.Scale(40, 1, 1)
        tpd = vtk.vtkTransformPolyDataFilter()
        tpd.SetTransform(t)
        tpd.SetInputConnection(self.s.GetOutputPort())
        self.m = vtk.vtkPolyDataMapper()
        self.m.SetInputConnection(tpd.GetOutputPort())
        self.a = vtk.vtkActor()
        self.a.SetMapper(self.m)

        self.a.SetUserMatrix(_T)

        self.COLOR = [1, 1, 1]
        # self.COLOR_ACTIVE = [0.35, 0.35, 1]
        # self.COLOR_ACTIVE = [236/255, 0/255, 68/255]
        self.COLOR_ACTIVE = [1, 0, 0.5]

    def __del__(self):
        del self.a
        del self.m
        del self.s

    def get_actor(self):
        return self.a

    def set_active(self, is_active=False):
        c = self.COLOR_ACTIVE if is_active else self.COLOR
        self.a.GetProperty().SetColor(c)


class TEXT_2D:
    def __init__(self, txt, w_coord, size=20, color=[175/255, 238/255, 238/255], style=0):
        self.w_coord = w_coord

        self.txt_actor = vtk.vtkTextActor()
        self.txt_actor.SetInput(txt)

        c = self.txt_actor.GetPositionCoordinate()
        c.SetCoordinateSystemToWorld()
        c.SetValue(w_coord)

        if style == 0:
            self.txt_actor.GetTextProperty().SetFontSize(size)
            self.txt_actor.GetTextProperty().SetColor(color)
            self.txt_actor.GetTextProperty().SetVerticalJustificationToCentered()
            self.txt_actor.GetTextProperty().SetJustificationToCentered()
            self.txt_actor.GetTextProperty().SetBackgroundColor(0.2, 0.3, 0.4)
            self.txt_actor.GetTextProperty().SetBackgroundOpacity(0.6)
            self.txt_actor.GetTextProperty().UseTightBoundingBoxOn()
            self.txt_actor.GetTextProperty().BoldOn()
        elif style == 1:
            self.txt_actor.GetTextProperty().SetFontSize(size)
            self.txt_actor.GetTextProperty().SetColor(color)
            self.txt_actor.GetTextProperty().SetVerticalJustificationToCentered()
            self.txt_actor.GetTextProperty().SetJustificationToCentered()
            self.txt_actor.GetTextProperty().BoldOn()
            self.txt_actor.GetTextProperty().SetOpacity(0.7)
        elif style == 2:
            self.txt_actor.GetTextProperty().SetFontSize(size)
            self.txt_actor.GetTextProperty().SetColor([0, 0, 0])
            self.txt_actor.GetTextProperty().SetVerticalJustificationToCentered()
            self.txt_actor.GetTextProperty().SetJustificationToCentered()
            self.txt_actor.GetTextProperty().SetBackgroundColor(1, 1, 1)
            self.txt_actor.GetTextProperty().SetBackgroundOpacity(0.6)

    def __del__(self):
        del self.txt_actor
        del self.w_coord

    def copy_from(self, origin):
        self.w_coord = origin.w_coord
        self.txt_actor.SetInput(origin.txt_actor.GetInput())
        self.txt_actor.SetTextProperty(origin.txt_actor.GetTextProperty())

    def get_actor(self):
        return self.txt_actor

    def set_text(self, txt):
        self.txt_actor.SetInput(txt)
        self.txt_actor.Modified()

    def set_position(self, w_coord):
        self.w_coord = w_coord
        c = self.txt_actor.GetPositionCoordinate()
        c.SetValue(w_coord)
        c.Modified()
        self.txt_actor.Modified()

    def move_by_displacement(self, disp):
        c = self.txt_actor.GetPositionCoordinate()
        self.w_coord = np.add(c.GetValue(), disp)
        c.SetValue(self.w_coord)
        c.Modified()
        self.txt_actor.Modified()

    def set_visibility(self, show):
        self.txt_actor.SetVisibility(show)


class LINE:
    def __init__(self, radius=0.2, color=[0,0,1], opacity=1, *args, **kwds):
        self.radius = radius
        self.color = color

        self.points = vtk.vtkPoints()
        self.polyline = vtk.vtkPolyLine()
        self.cells = vtk.vtkCellArray()
        self.polyData = vtk.vtkPolyData()
        self.tube = vtk.vtkTubeFilter()
        self.tube.SetInputData(self.polyData)
        self.tube.SetNumberOfSides(36)
        self.tube.SetRadius(radius)
        self.tube.SetCapping(True)
        self.tube.Update()

        self.mapper_line = vtk.vtkPolyDataMapper()
        self.mapper_line.SetInputData(self.tube.GetOutput())
        self.mapper_line.Update()

        self.actor_line = vtk.vtkActor()
        self.actor_line.SetMapper(self.mapper_line)
        self.actor_line.GetProperty().SetColor(color)
        self.actor_line.GetProperty().SetOpacity(opacity)

    def __del__(self):
        del self.actor_line
        del self.mapper_line
        del self.tube
        del self.polyData
        del self.cells
        del self.polyline
        del self.points

    def set_points(self, points):
        self.points.Reset()
        self.cells.Reset()
        self.polyData.Reset()

        for p in points:
            self.points.InsertNextPoint(p)
        self.polyline.GetPointIds().SetNumberOfIds(len(points))
        for i in range(len(points)):
            self.polyline.GetPointIds().SetId(i, i)

        self.cells.InsertNextCell(self.polyline)
        self.polyData.SetPoints(self.points)
        self.polyData.SetLines(self.cells)

        self.points.Modified()
        self.polyline.Modified()
        self.cells.Modified()
        self.polyData.Modified()
        self.tube.Update()
        self.tube.Modified()
        self.mapper_line.Update()
        self.actor_line.Modified()

    def get_actor(self):
        return self.actor_line


class LINE2D:
    def __init__(self, radius=0.2, color=[0,0,1], opacity=1, *args, **kwds):
        self.radius = radius
        self.color = color

        self.points = vtk.vtkPoints()
        self.polyline = vtk.vtkPolyLine()
        self.cells = vtk.vtkCellArray()
        self.polyData = vtk.vtkPolyData()
        self.tube = vtk.vtkTubeFilter()
        self.tube.SetInputData(self.polyData)
        self.tube.SetNumberOfSides(36)
        self.tube.SetRadius(radius)
        self.tube.SetCapping(True)
        self.tube.Update()

        self.mapper_line = vtk.vtkPolyDataMapper2D()
        self.mapper_line.SetInputData(self.tube.GetOutput())
        self.mapper_line.Update()

        self.actor_line = vtk.vtkActor2D()
        self.actor_line.SetMapper(self.mapper_line)
        self.actor_line.GetProperty().SetColor(color)
        self.actor_line.GetProperty().SetOpacity(opacity)

        coordinate = vtk.vtkCoordinate()
        coordinate.SetCoordinateSystemToWorld()
        self.mapper_line.SetTransformCoordinate(coordinate)

    def __del__(self):
        del self.actor_line
        del self.mapper_line
        del self.tube
        del self.polyData
        del self.cells
        del self.polyline
        del self.points

    def set_points(self, points):
        self.points.Reset()
        self.cells.Reset()
        self.polyData.Reset()

        for p in points:
            self.points.InsertNextPoint(p)
        self.polyline.GetPointIds().SetNumberOfIds(len(points))
        for i in range(len(points)):
            self.polyline.GetPointIds().SetId(i, i)

        self.cells.InsertNextCell(self.polyline)
        self.polyData.SetPoints(self.points)
        self.polyData.SetLines(self.cells)

        self.points.Modified()
        self.polyline.Modified()
        self.cells.Modified()
        self.polyData.Modified()
        self.tube.Update()
        self.tube.Modified()
        self.mapper_line.Update()
        self.actor_line.Modified()

    def get_actor(self):
        return self.actor_line


class LINE_SHAPE:
    def __init__(self, line_radius, line_color, shape_color, opacity=0.45, *args, **kwds):
        self.polydata = vtk.vtkPolyData()
        self.points = vtk.vtkPoints()
        self.cells = vtk.vtkCellArray()
        self.polydata.SetPoints(self.points)
        self.polydata.SetPolys(self.cells)
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(self.polydata)
        self.mapper.Modified()
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)
        self.actor.GetProperty().SetColor(shape_color)
        self.actor.GetProperty().SetOpacity(opacity)

        self.pano_line = LINE(radius=line_radius, color=line_color)

    def __del__(self):
        del self.actor
        del self.mapper
        del self.cells
        del self.points
        del self.polydata
        del self.pano_line

    def set_shape_info(self, points, horizontal_vecs, thickness):

        self.pano_line.set_points(points)

        self.points.Reset()
        self.cells.Reset()
        self.polydata.Reset()
        direction = np.multiply(horizontal_vecs, thickness / 2)
        pts_inside = np.add(points, -direction)
        pts_outside = np.add(points, direction)
        pts_all = np.append(pts_inside, pts_outside).reshape(-1, 3)
        self.points.SetNumberOfPoints(len(pts_all))
        for i, _p in enumerate(pts_all):
            self.points.SetPoint(i, *_p)
        faces = np.array([])
        for i in range(len(points) - 1):
            faces = np.append(faces, [i, i + 1, len(points) + i])
            faces = np.append(faces, [i + 1, len(points) + i + 1, len(points) + i])
        faces = faces.reshape(-1, 3).astype(int)
        for i in faces:
            tri = vtk.vtkTriangle()
            for _idx, _face in enumerate(i):
                tri.GetPointIds().SetId(_idx, _face)
            self.cells.InsertNextCell(tri)
        self.cells.Modified()
        self.polydata.SetPoints(self.points)
        self.polydata.SetPolys(self.cells)
        self.polydata.Modified()
        self.mapper.Update()
        self.actor.Modified()

    def get_actors(self):
        return self.pano_line.get_actor(), self.actor


# TODO!!
# class LineOnMesh:
#     def __init__(self, mesh_obj, pts, *args, **kwds):
#         self.obj_mesh = mesh_obj
#
#         self.tolerance = 0.001
#
#         self.locator = vtk.vtkCellLocator()
#         self.locator.SetDataSet(mesh_obj)
#         self.locator.BuildLocator()
#
#         vec = np.subtract(*pts)
#         norm = np.linalg.norm(vec)
#         norm_vec = vec / norm
#         c = norm / 50
#         tic = norm_vec * c
#
#         self.points = vtk.vtkPoints()
#         for _ in range(50):
#             p = list(pts[0])
#             p1 = np.add(p, tic).tolist()
#             p1[2] -= 5
#             p2 = np.add(p, tic).tolist()
#             p2[2] += 5
#
#             # Outputs (we need only pos which is the x, y, z position
#             # of the intersection)
#             t = vtk.mutable(0)
#             pos = [0.0, 0.0, 0.0]
#             pcoords = [0.0, 0.0, 0.0]
#             subId = vtk.mutable(0)
#             self.locator.IntersectWithLine(p1, p2, self.tolerance, t, pos, pcoords, subId)
#
#             # Add a slight offset in z
#             pos[2] += 0.01
#             # Add the x, y, z position of the intersection
#             self.points.InsertNextPoint(pos)
#
#         # Create a spline and add the points
#         self.spline = vtk.vtkParametricSpline()
#         self.spline.SetPoints(self.points)
#         self.functionSource = vtk.vtkParametricFunctionSource()
#         self.functionSource.SetUResolution(50)
#         self.functionSource.SetParametricFunction(self.spline)
#
#         # Map the spline
#         self.mapper = vtk.vtkPolyDataMapper()
#         self.mapper.SetInputConnection(self.functionSource.GetOutputPort())
#
#         # Define the line actor
#         self.actor = vtk.vtkActor()
#         self.actor.SetMapper(self.mapper)
#         self.actor.GetProperty().SetColor([1.0, 0.0, 0.0])
#         self.actor.GetProperty().SetLineWidth(3)
#
#     def get_actor(self):
#         return self.actor


class SliceImage:
    def __init__(self):

        self.cy_img_reslice_mapper = cyVtkImageResliceMapper.cyVtkImageResliceMapper()
        m = self.cy_img_reslice_mapper.get_mapper()
        self.mapper = m

        # self.mapper = vtk.vtkImageResliceMapper()
        self.mapper.SetSlicePlane(vtk.vtkPlane())
        # self.actor = vtk.vtkImageSlice()
        self.actor = vtk.vtkImageActor()
        self.actor.SetMapper(self.mapper)
        self.property = None
        self.vtk_img = None
        self.mirrored = False

    def __del__(self):
        del self.mapper
        del self.actor
        del self.property
        del self.vtk_img

    def set_vtk_img(self, vtk_img):
        if hasattr(self, 'vtk_img'):
            del self.vtk_img
        self.vtk_img = vtk_img
        self.mapper.SetInputData(self.vtk_img)

    def set_actor_property(self, img_prop):
        self.property = img_prop
        self.actor.SetProperty(img_prop)
        self.actor.Modified()

    def set_plane(self, origin, normal):
        _p = self.mapper.GetSlicePlane()
        _p.SetOrigin(origin)
        _p.SetNormal(normal)
        _p.Modified()
        self.mapper.Update()

    def get_plane(self):
        return self.mapper.GetSlicePlane()

    def get_actor(self):
        return self.actor

    def set_thickness(self, thickness):
        if not self.vtk_img is None:
            # self.mapper.SetSlabTypeToMean()
            self.mapper.SetSlabThickness(thickness)
            self.mapper.Update()

    def get_thickness(self):
        if not self.vtk_img is None: # self.mapper.SetSlabTypeToMean()
            return self.mapper.GetSlabThickness()
        else:
            return None

    def set_rendering_type(self, _value):
        if not self.vtk_img is None:
            if _value == "MIP":
                self.mapper.SetSlabTypeToMax()
            elif _value == "minIP":
                self.mapper.SetSlabTypeToMin()
            elif _value == "MPR":
                self.mapper.SetSlabTypeToMean()
            self.mapper.Update()


"""
Matrix
"""

def get_matrix_from_vtkmat(vtk_mat):
    mat = [[0 for x in range(4)] for y in range(4)]
    for i in range(16):
        r = i // 4
        c = i - r * 4
        mat[r][c] = vtk_mat.GetElement(r, c)
    return mat

def get_vtkmat_from_list(list_mat, transpose=False):
    matrix = vtk.vtkMatrix4x4()
    for i, v in enumerate(list_mat):
        r = i // 4
        c = i - r * 4
        matrix.SetElement(r, c, v)

    if transpose:
        matrix.Transpose()

    return matrix

def pt_on_plane(pt, plane, tolerance):
    val = np.abs(np.inner((np.subtract(plane[0], pt)), plane[1]))
    return val <= tolerance or np.isclose(val, tolerance)

def get_angle_between_vectors(vec1, vec2):
    cos_theta = np.inner(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    if not (-1.0 <= cos_theta <= 1.0) or np.isnan(cos_theta):
        """
        check range (-1 ~ +1) because of floating point inaccuracy
        """
        return 0
    return np.arccos(cos_theta)

def quaternion_to_mat(w, x, y, z, return_type='list'):
    """
    NOTE
    Quaternion Q : w, x, y, z  =>  cos(theta/2), v*sin(theta/2)
    """
    col0 = list()
    col0.append(1 - (2 * (y**2)) - (2 * (z**2)))
    col0.append((2 * x * y) + (2 * w * z))
    col0.append((2 * x * z) - (2 * w * y))
    col0.append(0)
    col1 = list()
    col1.append((2 * x * y) - (2 * w * z))
    col1.append(1 - (2 * (x**2)) - (2 * (z**2)))
    col1.append((2 * y * z) + (2 * w *  x))
    col1.append(0)
    col2 = list()
    col2.append((2 * x * z) + (2 * w * y))
    col2.append((2 * y * z) - (2 * w * x))
    col2.append(1 - (2 * (x**2)) - (2 * (y**2)))
    col2.append(0)

    result_mat = np.column_stack((col0, col1, col2, [0, 0, 0, 1]))

    if return_type == 'list':
        return result_mat
    elif return_type == 'vtkmat':
        return get_vtkmat_from_list(result_mat.ravel())
    return result_mat

def get_rotation_matrix(angle, axis, return_type='list'):
    v = np.multiply(axis, math.sin(angle / 2))
    return quaternion_to_mat(math.cos(angle / 2), v[0], v[1], v[2], return_type)

def intersection_of_two_planes(plane1_o, plane1_n, plane2_o, plane2_n):
    """
    calc intersection line of two planes
    """
    # two planes
    plane1_o = np.asarray(plane1_o).flatten()
    plane1_n = np.asarray(plane1_n).flatten()
    plane2_o = np.asarray(plane2_o).flatten()
    plane2_n = np.asarray(plane2_n).flatten()
    # equation
    d1 = (-1 * plane1_n[0] * plane1_o[0]) + \
         (-1 * plane1_n[1] * plane1_o[1]) + \
         (-1 * plane1_n[2] * plane1_o[2])
    d2 = (-1 * plane2_n[0] * plane2_o[0]) + \
         (-1 * plane2_n[1] * plane2_o[1]) + \
         (-1 * plane2_n[2] * plane2_o[2])
    a = np.array([plane1_n, plane2_n])
    b = np.array([-1 * d1, -1 * d2])
    # solve
    i = np.linalg.pinv(a)
    b = np.matmul(i, b)
    _pos_of_intersection = np.asarray(b).flatten()
    _vector_of_intersection = np.cross(plane2_n, plane1_n)
    return _pos_of_intersection, _vector_of_intersection


def intersection_of_two_lines(line1, line2):
    line1_vec = np.subtract(line1[1], line1[0])
    line1_vec = line1_vec / np.linalg.norm(line1_vec)
    line2_vec = np.subtract(line2[1], line2[0])
    line2_vec = line2_vec / np.linalg.norm(line2_vec)
    # param T, S
    _aa = np.array([[line1_vec[0], line2_vec[0] * -1],
                    [line1_vec[1], line2_vec[1] * -1],
                    [line1_vec[2], line2_vec[2] * -1]])
    _bb = np.array([[line2[0][0] - line1[0][0]],
                    [line2[0][1] - line1[0][1]],
                    [line2[0][2] - line1[0][2]]])
    pi_aa = np.linalg.pinv(_aa)
    val = np.matmul(pi_aa, _bb)
    _x = float((line1_vec[0] * val[0]) + line1[0][0])
    _y = float((line1_vec[1] * val[0]) + line1[0][1])
    _z = float((line1_vec[2] * val[0]) + line1[0][2])
    return _x, _y, _z


"""
Bundle Path (path for deployment using the pyinstaller)
"""
def get_bundle_path():
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return base_path


"""
Detect peaks in data based on their amplitude and other features.
"""
def detect_peaks(x, mph=None, mpd=1, threshold=0, edge='rising',
                 kpsh=False, valley=False, show=False, ax=None):

    """Detect peaks in data based on their amplitude and other features.

    Parameters
    ----------
    x : 1D array_like
        data.
    mph : {None, number}, optional (default = None)
        detect peaks that are greater than minimum peak height.
    mpd : positive integer, optional (default = 1)
        detect peaks that are at least separated by minimum peak distance (in
        number of data).
    threshold : positive number, optional (default = 0)
        detect peaks (valleys) that are greater (smaller) than `threshold`
        in relation to their immediate neighbors.
    edge : {None, 'rising', 'falling', 'both'}, optional (default = 'rising')
        for a flat peak, keep only the rising edge ('rising'), only the
        falling edge ('falling'), both edges ('both'), or don't detect a
        flat peak (None).
    kpsh : bool, optional (default = False)
        keep peaks with same height even if they are closer than `mpd`.
    valley : bool, optional (default = False)
        if True (1), detect valleys (local minima) instead of peaks.
    show : bool, optional (default = False)
        if True (1), plot data in matplotlib figure.
    ax : a matplotlib.axes.Axes instance, optional (default = None).

    Returns
    -------
    ind : 1D array_like
        indeces of the peaks in `x`.
   """

    x = np.atleast_1d(x).astype('float64')
    if x.size < 3:
        return np.array([], dtype=int)
    if valley:
        x = -x
    # find indices of all peaks
    dx = x[1:] - x[:-1]
    # handle NaN's
    indnan = np.where(np.isnan(x))[0]
    if indnan.size:
        x[indnan] = np.inf
        dx[np.where(np.isnan(dx))[0]] = np.inf
    ine, ire, ife = np.array([[], [], []], dtype=int)
    if not edge:
        ine = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) > 0))[0]
    else:
        if edge.lower() in ['rising', 'both']:
            ire = np.where((np.hstack((dx, 0)) <= 0) & (np.hstack((0, dx)) > 0))[0]
        if edge.lower() in ['falling', 'both']:
            ife = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) >= 0))[0]
    ind = np.unique(np.hstack((ine, ire, ife)))
    # handle NaN's
    if ind.size and indnan.size:
        # NaN's and values close to NaN's cannot be peaks
        ind = ind[np.in1d(ind, np.unique(np.hstack((indnan, indnan-1, indnan+1))), invert=True)]
    # first and last values of x cannot be peaks
    if ind.size and ind[0] == 0:
        ind = ind[1:]
    if ind.size and ind[-1] == x.size-1:
        ind = ind[:-1]
    # remove peaks < minimum peak height
    if ind.size and mph is not None:
        ind = ind[x[ind] >= mph]
    # remove peaks - neighbors < threshold
    if ind.size and threshold > 0:
        dx = np.min(np.vstack([x[ind]-x[ind-1], x[ind]-x[ind+1]]), axis=0)
        ind = np.delete(ind, np.where(dx < threshold)[0])
    # detect small peaks closer than minimum peak distance
    if ind.size and mpd > 1:
        ind = ind[np.argsort(x[ind])][::-1]  # sort ind by peak height
        idel = np.zeros(ind.size, dtype=bool)
        for i in range(ind.size):
            if not idel[i]:
                # keep peaks with the same height if kpsh is True
                idel = idel | (ind >= ind[i] - mpd) & (ind <= ind[i] + mpd) \
                    & (x[ind[i]] > x[ind] if kpsh else True)
                idel[i] = 0  # Keep current peak
        # remove the small peaks and sort back the indices by their occurrence
        ind = np.sort(ind[~idel])

    if show:
        if indnan.size:
            x[indnan] = np.nan
        if valley:
            x = -x
        _plot(x, mph, mpd, threshold, edge, valley, ax, ind)

    return ind


def _plot(x, mph, mpd, threshold, edge, valley, ax, ind):
    """
    Plot results of the detect_peaks function
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print('matplotlib is not available.')
    else:
        if ax is None:
            _, ax = plt.subplots(1, 1, figsize=(8, 4))

        ax.plot(x, 'b', lw=1)
        if ind.size:
            label = 'valley' if valley else 'peak'
            label = label + 's' if ind.size > 1 else label
            ax.plot(ind, x[ind], '+', mfc=None, mec='r', mew=2, ms=8,
                    label='%d %s' % (ind.size, label))
            ax.legend(loc='best', framealpha=.5, numpoints=1)
        ax.set_xlim(-.02*x.size, x.size*1.02-1)
        ymin, ymax = x[np.isfinite(x)].min(), x[np.isfinite(x)].max()
        yrange = ymax - ymin if ymax > ymin else 1
        ax.set_ylim(ymin - 0.1*yrange, ymax + 0.1*yrange)
        ax.set_xlabel('Data #', fontsize=14)
        ax.set_ylabel('Amplitude', fontsize=14)
        mode = 'Valley detection' if valley else 'Peak detection'
        ax.set_title("%s (mph=%s, mpd=%d, threshold=%s, edge='%s')"
                     % (mode, str(mph), mpd, str(threshold), edge))
        # plt.grid()
        plt.show()