import io
import platform

import vtk
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QImage, QMouseEvent
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

# from cyhub.block_support.event_interactor.cy_interactor import Geometry3DCameraInteractor

_IS_MAC = (platform.system() == 'Darwin')


outlog = vtk.vtkFileOutputWindow()
outlog.SetFileName("./vtklog.txt")
outlog.SetInstance(outlog)


class Vtk_image_holder(QObject):
    """
    __image_dirty: indicator stating image needs to be captured
    """

    sig_rendered = pyqtSignal(object)
    sig_resize = pyqtSignal(int, int)
    sig_refresh = pyqtSignal()

    def __init__(self, parent=None, wcont=None, istyle=None, *args, **kwds):
        super().__init__(parent)

        self._cy__VtkImageHolder = "Dummy"
        self.wcont = wcont

        self.view = QVTKRenderWindowInteractor()
        self.img = QImage()
        self.__last_image_num, self.__image_num = 0, 0

        self.ren = vtk.vtkRenderer()
        self.view._RenderWindow.AddRenderer(self.ren)
        self.view._RenderWindow.AddObserver('EndEvent', self.__on_image_rendered)

        self.set_interactor_style(istyle)

        self.view.Start()

        # self._IS_INTEL_GRAPHIC = self.__check_intel()
        # if _IS_MAC and not self._IS_INTEL_GRAPHIC:
        if _IS_MAC:
            # NOTE!!! "OffScreenRenderingOn()" is worked well on MAC except INTEL Graphic Card unlike Windows
            self.view._RenderWindow.InitializeFromCurrentContext()
            self.view._RenderWindow.OffScreenRenderingOn()

        # TODO is this necessary?
        # self.sig_refresh.connect(self.refresh)
        # self.sig_resize.connect(self.resize, Qt.DirectConnection)

    def finalize(self):
        self.view.Finalize()

    def reset(self):
        """ reset """

        if not hasattr(self, '__check_once__'):
            setattr(self, '__check_once__', True)

            """ renderer """
            # remove & delete
            self.view._RenderWindow.RemoveRenderer(self.ren)
            self.view._Iren.GetInteractorStyle().RemoveAllObservers()
            del self.ren
            # init
            self.ren = vtk.vtkRenderer()

            """ render window """
            # keep interactor style
            _istyle = self.view._Iren.GetInteractorStyle()
            # delete
            del self.view
            # init
            self.view = QVTKRenderWindowInteractor()
            self.view._RenderWindow.AddRenderer(self.ren)
            self.view._RenderWindow.AddObserver('EndEvent', self.__on_image_rendered)

            self.set_interactor_style(_istyle)
            self.view.Start()

            if _IS_MAC:
            # if _IS_MAC and not self._IS_INTEL_GRAPHIC:
            #     NOTE!!! "OffScreenRenderingOn()" is worked well on MAC except INTEL Graphic Card unlike Windows
                self.view._RenderWindow.InitializeFromCurrentContext()
                self.view._RenderWindow.OffScreenRenderingOn()
        else:
            self.view._Iren.GetInteractorStyle().RemoveAllObservers()
            self.view.RemoveAllObservers()

    def __check_intel(self):
        str_capa = self.view._RenderWindow.ReportCapabilities()
        str_buf = io.StringIO(str_capa)
        for txt in str_buf.readlines():
            if "OpenGL vendor string" in txt:
                if "Intel" in txt:
                    print("This is INTEL!!!")
                    return True
                else:
                    print("This is not INTEL!!!")
                    return False

    def __on_image_rendered(self, _o, _e):
        # print('    1. rendered!!!')

        self.__image_num += 1

        # print('    2. paint ', end='')
        if self.__last_image_num < self.__image_num:
            # print('+ capture ', end='')
            w, h = self.view._RenderWindow.GetSize()

            if self.img.width() != w or self.img.height() != h:
                self.img = QImage(w, h, QImage.Format_RGB32)

            b = self.img.bits()  # sip.voidptr object
            if not b:
                return
            b.setsize(self.img.byteCount())  # enabling Python buffer protocol

            va = vtk.vtkUnsignedCharArray()
            # va.SetVoidArray(b, self.img.byteCount(), 1)
            va.SetVoidArray(b, w * h * 4, 1)
            self.view._RenderWindow.GetRGBACharPixelData(0, 0, w - 1, h - 1, 1, va)

            self.img = self.img.rgbSwapped()
            self.img = self.img.mirrored(False, True)

            self.__last_image_num = self.__image_num

            self.sig_rendered.emit(self.img)

    def set_interactor_style(self, istyle):
        self.istyle = istyle or vtk.vtkInteractorStyleTrackballCamera()
        self.view._Iren.SetInteractorStyle(self.istyle)

    def resize(self, w, h):
        # NOTE Even though we request view.resize() here, view.resizeEvent()
        #   will not be triggered, because view is not shown. Hence, we do
        #   necessary things here.
        print('  resize', w, h)

        if w == 0 or h == 0:
            print("  Resize Event SKIP - invalid size w:%s, h:%s" % (w, h))
            return

        self.view.resize(w, h)
        self.view._RenderWindow.SetSize(w, h)
        self.view._Iren.SetSize(w, h)
        self.view._Iren.ConfigureEvent()
        self.view.update()

        # NOTE make sure the vtk render window size
        print("  applied size : ", self.view._RenderWindow.GetSize())

        if _IS_MAC:
        #     # NOTE As of Python 3.5 and PyQt 5.7, without this, scene is not
        #     #   transformed appropriately during resize on Mac.
        #     # TODO? Due to the below, rendering is done twice during resize.
        #     if self._IS_INTEL_GRAPHIC:
        #         self.view.show()
        #         self.view.hide()
        #     else:
        #         # NOTE!!! "OffScreenRenderingOn()" is worked well on MAC except INTEL Graphic Card unlike Windows
        #         #   and then, need to update via "UpdateContext()"
            self.view._RenderWindow.UpdateContext()

        self.view._RenderWindow.Render()

        # print('        ', e.size(), 'resize')

    def hoverMoveEvent(self, e):
        # NOTE As of QQuickItem, Mouse move events are separated into move and hover-move.
        #   so, implemented the HoverMoveEvent method.

        _MB, _KM = Qt.MouseButtons, Qt.KeyboardModifiers
        ev = QMouseEvent(QEvent.MouseMove, e.pos(), Qt.NoButton, _MB(Qt.NoButton), _KM(Qt.NoModifier))
        self.view.mouseMoveEvent(ev)

        # p = e.pos()
        # self.view._Iren.SetEventInformationFlipY(p.x(), p.y(),
        #                                     0, 0, chr(0), 0, None)
        # self.view._Iren.MouseMoveEvent()

        # TODO!!! mouse hover moved event doesn't works well in pyqt 5.8 later. i think that it must be Qt 5.8 bug!!!


    def mouseMoveEvent(self, e):
        self.view.mouseMoveEvent(e)

    def mousePressEvent(self, e):
        self.view.mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.view.mouseReleaseEvent(e)

    def wheelEvent(self, e):

        ctrl, shift = self.view._GetCtrlShift(e)

        self.view._Iren.SetEventInformationFlipY(e.x(), e.y(),
                                                 ctrl, shift, chr(0), 0, None)
        d = e.angleDelta().y()

        self.istyle.SetMouseWheelMotionFactor(abs(d) / 120)

        if d > 0:
            self.view._Iren.MouseWheelForwardEvent()
        elif d < 0:
            self.view._Iren.MouseWheelBackwardEvent()

    def keyPressEvent(self, e):
        self.view.keyPressEvent(e)

    def keyReleaseEvent(self, e):
        self.view.keyReleaseEvent(e)

    def mouseDoubleClickEvent(self, e):
        # TODO
        print("mouse double clicked :: ", e)

    @pyqtSlot()
    def refresh(self):
        self.view._RenderWindow.Render()


#
# Install vtk message hook.

def hook_vtk_message():
    """
    Duplicate vtk message to qCritical/qWarning and stdout.

    NOTE At least up to vtk 6.3, it is almost impossible to hide 'vtk output
      window.' This seems best.

    NOTE Sometimes this is called when vtk is trying to paint, which can lead
      to 'recursive repaint' in view of Qt, which results in Qt warning message
      that users get additionally. (TODO?)
    """
    from PyQt5.QtCore import qCritical, qWarning
    def display_error(obj, evt):
        qCritical('vtk %s: Check vtk output window for detail.' % evt)

    def display_warning(obj, evt):
        qWarning('vtk %s: Check vtk output window for detail.' % evt)

    o = vtk.vtkOutputWindow.GetInstance()
    o.AddObserver(vtk.vtkCommand.ErrorEvent, display_error)
    o.AddObserver(vtk.vtkCommand.WarningEvent, display_warning)
    # Duplicate message to stderr (Windows only).
    try:
        o.SendToStdErrOn()
    except:
        pass


hook_vtk_message()


#
# A few example pipelines

def actor_cone():
    s, m, a = vtk.vtkConeSource(), vtk.vtkPolyDataMapper(), vtk.vtkActor()
    m.SetInputConnection(s.GetOutputPort())
    a.SetMapper(m)
    return a

def actor_balls():
    ss, gl = vtk.vtkSphereSource(), vtk.vtkGlyph3D()
    B, Bm, Ba = vtk.vtkAppendPolyData(), vtk.vtkPolyDataMapper(), vtk.vtkActor()
    gl.SetInputConnection(ss.GetOutputPort())
    gl.SetSourceConnection(ss.GetOutputPort())
    gl.SetVectorModeToUseNormal()
    gl.SetScaleModeToScaleByVector()
    gl.SetScaleFactor(0.15)
    B.AddInputConnection(ss.GetOutputPort())
    B.AddInputConnection(gl.GetOutputPort())
    Bm.SetInputConnection(B.GetOutputPort())
    Ba.SetMapper(Bm)
    return Ba

# if __name__ == "__main__":
#     from cyhub.cy_image_holder import CyQQuickView
#     w = CyQQuickView()
#     # w.setResizeMode(QQuickView.SizeRootObjectToView)
#     w.setSource(QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), './cy_vtk.qml')))
#
#     cone = actor_cone()
#     v = Vtk_image_holder()
#     v.ren.AddViewProp(cone)
#     v.resize(700, 300)
#     v.resize(700, 300)
#
#     vtk_item = w.rootObject().findChild(QObject, 'vtk_image')
#     vtk_item.set_vtk(v)
#     w.show()
#
#     _qapp.exec_(interactive_msg=False)
