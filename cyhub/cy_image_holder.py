import platform

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty
from PyQt5.QtCore import Qt, QTimer, QEvent, QPoint, QPointF, QLineF, QVariant, QUrl, QRectF, QSize
from PyQt5.QtGui import QImage, QScreen, QMouseEvent, QWheelEvent, QHoverEvent, qAlpha
from PyQt5.QtQuick import QQuickView, QQuickItem, QSGSimpleTextureNode
from PyQt5 import QtQml

import math
import _qapp


_IS_MAC = (platform.system() == 'Darwin')

UP = 11
DOWN = 12
RIGHT = 13
LEFT = 14

NONE = -1
HOLD_AND_DRAG = 0
DRAG = 1
SELECT = 2
DOUBLETAP = 3


class ImageHolder(QQuickItem):
    """
    QML VTK IMAGE HOLDER ITEM
    """

    _update_request_event = QEvent(QEvent.UpdateRequest)

    mouseDoubleClicked = pyqtSignal(QVariant)
    mousePressed = pyqtSignal(QVariant)
    mouseReleased = pyqtSignal(QVariant)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(QQuickItem.ItemHasContents, True)
        self.img = QImage()
        self.n = None
        self.setAcceptedMouseButtons(Qt.AllButtons)
        self.setAcceptHoverEvents(True)
        self.vtk_obj = None

        self.prev_distance = 0.0
        self.prev_x1 = None
        self.bHoldCheck, self.bTwoFingers, self.bHold, self.isZoom, self.isScroll = False, False, False, False, False
        self.pan, self.drag = False, False
        self.touchTimestamp = 0
        self.doubleTap = False
        self.Result = NONE


    @pyqtSlot(object)
    @pyqtSlot(object, int)
    def set_image(self, img, n=None):
        self.img, self.n = img, n

        """ Deprecated
        # Force update. NOTE Without update(), it does not work. This is good
        #   property, because it can be *conjectured* that other non-dirty items
        #   will not be redrawn even though enclosing window's update is requested.
        #   It reduces performance loss.
        self.update()
        _qapp.qapp.sendEvent(self.window(), ImageHolder._update_request_event)
        """

        """
        NOTE force update isn't needed from qt 5.10(?) 
        """
        self.update()

    def updatePaintNode(self, node, updatePaintNodeData):
        # print(self.n)

        if node is None:
            node = QSGSimpleTextureNode()

        # TODO Check image update.
        self.texture = self.window().createTextureFromImage(self.img)
        node.setTexture(self.texture)
        """
        NOTE  sometimes, last column line of vtk_img used to flicker. (vtk 8.1 issue)
              therefore, need to set the SourceRect as below.
        """
        node.setSourceRect(0, 0, int(self.img.width()), int(self.img.height()))
        node.setRect(0, 0, int(self.width()), int(self.height()))

        return node

    def set_vtk(self, vtk_obj):
        # Set vtk _Widget_container or _Widget_replica

        if self.vtk_obj:
        #     self.vtk_obj.resize(int(self.width()), int(self.height()))
        #     return
            self.vtk_obj.sig_rendered.disconnect(self.set_image)
            del self.vtk_obj
            self.vtk_obj = None

        self.vtk_obj = vtk_obj
        self.vtk_obj.sig_rendered.connect(self.set_image)

        # Set init size
        self.vtk_obj.resize(int(self.width()), int(self.height()))

    def geometryChanged(self, newGeom, oldGeom):
        if not self.isVisible():
            return

        super().geometryChanged(newGeom, oldGeom)

        w = newGeom.width()
        h = newGeom.height()
        # o_w = oldGeom.width()
        # o_h = oldGeom.height()

        if self.vtk_obj:
            self.vtk_obj.resize(int(w), int(h))

    def mouseMoveEvent(self, e):
        if self.vtk_obj:
            self.vtk_obj.mouseMoveEvent(e)

    def mousePressEvent(self, e):
        self.mousePressed.emit(e)
        if self.vtk_obj:
            self.vtk_obj.mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.mouseReleased.emit(e)
        if self.vtk_obj:
            self.vtk_obj.mouseReleaseEvent(e)

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.mouseDoubleClicked.emit(e)
            # TODO is it necessary?
            # if self.vtk_obj:
            #     self.vtk_obj.mouseDoubleClickEvent(e)

    # property getter
    def GetFullscreenTrigger(self):
        if not hasattr(self, '_fullsize_trigger'):
            self._fullsize_trigger = False
        return self._fullsize_trigger

    # property setter
    def SetFullscreenTrigger(self, fullsize_trigger):
        self._fullsize_trigger = fullsize_trigger
        self.fullscreenTriggerChanged.emit()

    fullscreenTriggerChanged = pyqtSignal()
    fullscreenTrigger = pyqtProperty(QVariant, GetFullscreenTrigger, SetFullscreenTrigger, notify=fullscreenTriggerChanged)

    def hoverMoveEvent(self, e):
        if self.vtk_obj:
            self.vtk_obj.hoverMoveEvent(e)

    def hoverEnterEvent(self, e):
        pass

    def hoverLeaveEvent(self, e):
        pass

    def keyPressEvent(self, e):
        if self.vtk_obj:
            self.vtk_obj.keyPressEvent(e)

    def keyReleaseEvent(self, e):
        if self.vtk_obj:
            self.vtk_obj.keyReleaseEvent(e)

    def wheelEvent(self, e):
        if self.vtk_obj:
            self.vtk_obj.wheelEvent(e)
        # self.wheelEventByAngleDelta(e.angleDelta())

    def wheelEventByAngleDelta(self, delta):
        d = delta.y()

        if self.vtk_obj:
            self.vtk_obj.istyle.SetMouseWheelMotionFactor(abs(d) / 120)

            if d > 0:
                self.vtk_obj.view._Iren.MouseWheelForwardEvent()
            elif d < 0:
                self.vtk_obj.view._Iren.MouseWheelBackwardEvent()

    def touchEvent(self, e):
        if len(e.touchPoints()) == 1:
            if e.touchPointStates() == Qt.TouchPointPressed:
                self.bHoldCheck = True
                self.x = e.touchPoints()[0].startPos().x()
                self.y = e.touchPoints()[0].startPos().y()
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.isHold)
                self.timer.setSingleShot(True)
                self.timer.start(1000)
                self.pan, self.drag = True, True
                self.scenePosX, self.scenePosY = e.touchPoints()[0].scenePos().x(), e.touchPoints()[0].scenePos().y()
                print("TouchEvent Start(One Finger) -------------------------------------------------------")
            elif e.touchPointStates() == Qt.TouchPointMoved or e.touchPointStates() == Qt.TouchPointStationary:
                if self.bTwoFingers is False:
                    if self.bHold is True:
                        print("One Finger hold and drag")
                        self.Result = HOLD_AND_DRAG
                        if self.pan is True:
                            self.mousePressEvent(QMouseEvent(QEvent.MouseButtonPress, QPointF(e.touchPoints()[0].pos()),
                                                             QPointF(e.touchPoints()[0].screenPos()),
                                                             QPointF(e.touchPoints()[0].scenePos()),
                                                             Qt.RightButton, Qt.RightButton,
                                                             Qt.ControlModifier, Qt.MouseEventSynthesizedByApplication))
                            self.pan = False

                        self.mouseMoveEvent(QMouseEvent(QEvent.MouseMove, QPointF(e.touchPoints()[0].pos()),
                                                        QPointF(e.touchPoints()[0].screenPos()),
                                                        QPointF(e.touchPoints()[0].scenePos()),
                                                        Qt.RightButton, Qt.RightButton, Qt.ControlModifier,
                                                        Qt.MouseEventSynthesizedByApplication))

                    else:
                        self.bHoldCheck = False
                        self.timer.stop()
                        print("One Finger drag")
                        self.Result = DRAG
                        if self.drag is True:
                            self.mousePressEvent(QMouseEvent(QEvent.MouseButtonPress, QPointF(e.touchPoints()[0].pos()),
                                                             QPointF(e.touchPoints()[0].screenPos()),
                                                             QPointF(e.touchPoints()[0].scenePos()),
                                                             Qt.LeftButton, Qt.LeftButton,
                                                             Qt.NoModifier, Qt.MouseEventSynthesizedByApplication))
                            self.drag = False
                        self.mouseMoveEvent(QMouseEvent(QEvent.MouseMove, QPointF(e.touchPoints()[0].pos()),
                                                        QPointF(e.touchPoints()[0].screenPos()),
                                                        QPointF(e.touchPoints()[0].scenePos()),
                                                        Qt.LeftButton, Qt.LeftButton, Qt.NoModifier,
                                                        Qt.MouseEventSynthesizedByApplication))

            elif e.touchPointStates() == Qt.TouchPointReleased:
                self.prev_x1 = None
                if self. bHoldCheck is True:
                    self.bHoldCheck = False
                    self.timer.stop()
                self.bTwoFingers = False
                self.bHold = False
                self.isZoom = False
                self.isScroll = False
                self.pan, self.drag = False, False
                self.doubleTap = e.timestamp() - self.touchTimestamp < 200
                if self.doubleTap:
                    self.Result = DOUBLETAP
                    self.doubleTap = False
                self.touchTimestamp = e.timestamp()
                print("TouchEvent End(One Finger) -------------------------------------------------------")

                if self.Result == HOLD_AND_DRAG:
                    self.mouseReleaseEvent(QMouseEvent(QEvent.MouseButtonRelease, QPointF(e.touchPoints()[0].pos()),
                                                       QPointF(e.touchPoints()[0].screenPos()),
                                                       QPointF(e.touchPoints()[0].scenePos()),
                                                       Qt.RightButton, Qt.RightButton,
                                                       Qt.ControlModifier,
                                                       Qt.MouseEventSynthesizedByApplication))

                elif self.Result == DRAG:
                    self.mouseReleaseEvent(QMouseEvent(QEvent.MouseButtonRelease, QPointF(e.touchPoints()[0].pos()),
                                                       QPointF(e.touchPoints()[0].screenPos()),
                                                       QPointF(e.touchPoints()[0].scenePos()),
                                                       Qt.LeftButton, Qt.LeftButton,
                                                       Qt.NoModifier,
                                                       Qt.MouseEventSynthesizedByApplication))

                elif self.Result == NONE and (self.vtk_obj.bid == 'i2g_pano' or self.vtk_obj.bid == 'i2g_3d'):
                    self.mousePressEvent(QMouseEvent(QEvent.MouseButtonPress, QPointF(e.touchPoints()[0].pos()),
                                                     QPointF(e.touchPoints()[0].screenPos()),
                                                     QPointF(e.touchPoints()[0].scenePos()),
                                                     Qt.LeftButton, Qt.LeftButton,
                                                     Qt.NoModifier, Qt.MouseEventSynthesizedByApplication))

                    self.mouseReleaseEvent(QMouseEvent(QEvent.MouseButtonRelease, QPointF(e.touchPoints()[0].pos()),
                                                       QPointF(e.touchPoints()[0].screenPos()),
                                                       QPointF(e.touchPoints()[0].scenePos()),
                                                       Qt.LeftButton, Qt.LeftButton,
                                                       Qt.NoModifier,
                                                       Qt.MouseEventSynthesizedByApplication))
                elif self.Result == DOUBLETAP:
                    self.mouseDoubleClickEvent(QMouseEvent(QEvent.MouseButtonRelease, QPointF(e.touchPoints()[0].pos()),
                                                     QPointF(e.touchPoints()[0].screenPos()),
                                                     QPointF(e.touchPoints()[0].scenePos()),
                                                     Qt.LeftButton, Qt.LeftButton,
                                                     Qt.NoModifier, Qt.MouseEventSynthesizedByApplication))
                self.Result = NONE

        elif len(e.touchPoints()) == 2:
            if e.touchPointStates() == Qt.TouchPointPressed:
                print("TouchEvent Start(Two Fingers) -------------------------------------------------------")
                self.prev_x1 = e.touchPoints()[0].startPos().x()
                self.prev_y1 = e.touchPoints()[0].startPos().y()
                self.prev_x2 = e.touchPoints()[1].startPos().x()
                self.prev_y2 = e.touchPoints()[1].startPos().y()
                if self.bHoldCheck is True:
                    self.bHoldCheck = False
                    self.timer.stop()
                self.bTwoFingers = True
                self.pan = True
            elif e.touchPointStates() == Qt.TouchPointMoved or e.touchPointStates() == Qt.TouchPointStationary:
                self.bTwoFingers = True
                if self.bHoldCheck is True:
                    self.bHoldCheck = False
                    self.timer.stop()
                x1 = e.touchPoints()[0].pos().x()
                y1 = e.touchPoints()[0].pos().y()
                x2 = e.touchPoints()[1].pos().x()
                y2 = e.touchPoints()[1].pos().y()

                if self.prev_x1 is None:
                    self.prev_x1 = e.touchPoints()[0].startPos().x()
                    self.prev_y1 = e.touchPoints()[0].startPos().y()
                    self.prev_x2 = e.touchPoints()[1].startPos().x()
                    self.prev_y2 = e.touchPoints()[1].startPos().y()

                d = self.getDistance(x1, x2, y1, y2)

                direction1 = self.getDirection(self.prev_x1, self.prev_y1,
                                               e.touchPoints()[0].pos().x(), e.touchPoints()[0].pos().y())
                direction2 = self.getDirection(self.prev_x2, self.prev_y2,
                                               e.touchPoints()[1].pos().x(), e.touchPoints()[1].pos().y())


                if self.isZoom is False and direction1 is direction2:
                    self.isScroll = True

                if direction1 is direction2 and self.isZoom is False:
                    self.Result = HOLD_AND_DRAG
                    if self.pan is True:
                        self.mousePressEvent(QMouseEvent(QEvent.MouseButtonPress, QPointF(e.touchPoints()[0].pos()),
                                                         QPointF(e.touchPoints()[0].screenPos()),
                                                         QPointF(e.touchPoints()[0].scenePos()),
                                                         Qt.RightButton, Qt.RightButton,
                                                         Qt.ControlModifier, Qt.MouseEventSynthesizedByApplication))
                        self.pan = False

                    self.mouseMoveEvent(QMouseEvent(QEvent.MouseMove, QPointF(e.touchPoints()[0].pos()),
                                                QPointF(e.touchPoints()[0].screenPos()),
                                                QPointF(e.touchPoints()[0].scenePos()),
                                                Qt.RightButton, Qt.RightButton, Qt.ControlModifier,
                                                Qt.MouseEventSynthesizedByApplication))

                elif self.isScroll is False:
                    if math.fabs(d - self.prev_distance) < 5:
                        self.isZoom = True

                    s = QLineF(e.touchPoints()[0].pos(), e.touchPoints()[1].pos()).length() \
                               / QLineF(self.prev_x1, self.prev_y1, self.prev_x2, self.prev_y2).length()

                    direction = 10 if s > 1 else -10

                    p = (e.touchPoints()[0].pos() + e.touchPoints()[1].pos()) / 2
                    self.wheelEvent(QWheelEvent(p, p, QPoint(0,0), QPoint(0, direction), 0, 0, Qt.AllButtons, Qt.NoModifier, 0, 0))

                self.prev_distance = d
                self.prev_x1 = e.touchPoints()[0].pos().x()
                self.prev_y1 = e.touchPoints()[0].pos().y()
                self.prev_x2 = e.touchPoints()[1].pos().x()
                self.prev_y2 = e.touchPoints()[1].pos().y()
            elif e.touchPointStates() == Qt.TouchPointReleased:
                if self.Result == HOLD_AND_DRAG:
                    self.mouseReleaseEvent(QMouseEvent(QEvent.MouseButtonRelease, QPointF(e.touchPoints()[0].pos()),
                                                       QPointF(e.touchPoints()[0].screenPos()),
                                                       QPointF(e.touchPoints()[0].scenePos()),
                                                       Qt.RightButton, Qt.RightButton,
                                                       Qt.ControlModifier,
                                                       Qt.MouseEventSynthesizedByApplication))

                self.prev_x1 = None
                self.bHoldCheck = False
                if self.bHoldCheck is True:
                    self.bHoldCheck = False
                    self.timer.stop()
                self.bHold = False
                self.isZoom = False
                self.isScroll = False
                self.Result = NONE
                self.bTwoFingers = False
                print("TouchEvent End(Two Fingers) -------------------------------------------------------")

    def isHold(self):
        if self.bHoldCheck is True and self.bTwoFingers is False:
            self.bHold = True
            self.timer.stop()
            print("One Finger Hold")
            self._msg = []
            self._msg.append(self.scenePosX)
            self._msg.append(self.scenePosY)
            self.msgChanged.emit(self._msg)

    def getMsg(self):
        return self._msg

    def setMsg(self, msg):
        self._msg = msg

    msgChanged = pyqtSignal(QVariant)
    msg = pyqtProperty(QVariant, getMsg, setMsg, notify=msgChanged)


    def getDirection(self, x1, y1, x2, y2):
        angle = self.getAngle(x1, y1, x2, y2)
        return self.get(angle)

    def getCenterPos(self, points):
        centerx = (points[0].startPos().x() + points[1].startPos().x()) / 2
        centery = (points[0].startPos().y() + points[1].startPos().y()) / 2

        return centerx, centery

    def getDistance(self, x1, x2, y1, y2):
        return math.sqrt((x2-x1) ** 2 + (y2-y1) ** 2)

    def getAngle(self, x1, y1, x2, y2):
        rad = math.atan2(y1-y2, x2-x1) + math.pi
        return (rad*180/math.pi + 180) % 360

    def get(self, angle):
        if self.inRange(angle, 45, 135):
            return UP
        elif self.inRange(angle, 0, 45) or self.inRange(angle, 315, 360):
            return RIGHT
        elif self.inRange(angle, 225, 315):
            return DOWN
        else:
            return LEFT

    def inRange(self, angle, init, end):
        return (angle >= init and angle < end)


class MaskedMouseArea(QQuickItem):
    pressedChanged = pyqtSignal()
    maskSourceChanged = pyqtSignal()
    containsMouseChanged = pyqtSignal()
    alphaThresholdChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(QQuickItem.ItemHasContents, True)
        self.setAcceptedMouseButtons(Qt.AllButtons)
        self.setAcceptHoverEvents(False)
        self._pressed = False
        self._maskSource = None
        self._maskImage = None
        self._pressPoint = None
        self._alphaThreshold = 0.0
        self._containsMouse = False

    def qBound(self, _minVal, _current, _maxVal):
        return max(min(_current, _maxVal), _minVal)

    @pyqtProperty(bool, notify=pressedChanged)
    def pressed(self):
        return self._pressed

    @pressed.setter
    def pressed(self, pressed):
        if pressed != self._pressed:
            self._pressed = pressed
            self.pressedChanged.emit()

    @pyqtProperty(bool, notify=containsMouseChanged)
    def containsMouse(self):
        return self._containsMouse

    @containsMouse.setter
    def containsMouse(self, containsMouse):
        if self._containsMouse != containsMouse:
            self._containsMouse = containsMouse
            self.containsMouseChanged.emit()

    @pyqtProperty(QUrl, notify=maskSourceChanged)
    def maskSource(self):
        return self._maskSource

    @maskSource.setter
    def maskSource(self, source):
        if self._maskSource != source:
            self._maskSource = source
            self._maskImage = QImage()
            _path = self._maskSource.toString()
            if _IS_MAC:
                if _path.find('qrc:') > -1:
                    _path = _path[3:]
                elif _path.find('file:') > -1:
                    _path = _path[5:]
            else:
                if _path.find('file:') > -1:
                    _path = _path[8:]
            self._maskImage.load(_path)
            self.maskSourceChanged.emit()

    @pyqtProperty(float, notify=alphaThresholdChanged)
    def alphaThreshold(self):
        return self._alphaThreshold

    @alphaThreshold.setter
    def alphaThreshold(self, threshold):
        if self._alphaThreshold != threshold:
            self._alphaThreshold = threshold
            self.alphaThresholdChanged.emit()

    def contains(self, Union, QPointF=None, QPoint=None):
        if not super().contains(Union) or self._maskImage is None:
            return False
        p = Union.toPoint()

        if p.x() < 0 or p.x() >= self._maskImage.width() or \
            p.y() < 0 or p.y() >= self._maskImage.height():
            return False

        r = int(self.qBound(0, self._alphaThreshold * 255, 255))
        return qAlpha(self._maskImage.pixel(p)) > r

    def mousePressEvent(self, e):
        self._pressed = True
        self._pressPoint = e.pos()
        self.pressedChanged.emit()

    def mouseReleaseEvent(self, e):
        self._pressed = False
        # self.pressedChanged.emit()

        # _qapp.qApp = QCoreApplication(sys.argv)
        #
        # threshold = _qapp.qApp.styleHints.stratDragDistance()
        # isClick = (threshold >= qAbs(e.x() - self._pressPoint.x()) and
        #            threshold >= qAbs(e.y() - self._pressPoint.y()))
        # if isClick:
        #     self.sig_clicked.emit()

    def mouseUngrabEvent(self):
        self._pressed = False
        self.pressedChanged.emit()

    def hoverEnterEvent(self, e):
        self._containsMouse = True
        self.containsMouseChanged.emit()

    def hoverLeaveEvent(self, e):
        self._containsMouse = False
        self.containsMouseChanged.emit()


class CyQQuickView(QQuickView):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.screenChanged.connect(self.on_screen_changed)
        # self.setFlags(self.flags() | Qt.FramelessWindowHint)
        self.isFullscreen = False
        self.isScreenChanged = False
        QtQml.qmlRegisterType(ImageHolder, "cyhub", 1, 0, "ImageHolder")
        QtQml.qmlRegisterType(MaskedMouseArea, "cymaskarea", 1, 0, "MaskedMouseArea")

    def show(self, isMaximize=True):
        """
        Overriden Method

        NOTE Make sure that QQuickView is shown with "_delayed_start()" !!
          Because, Some machines(Windows/Mac) can cause qtquick's renderer problems.
        """

        def _delayed_start():
            super(QQuickView, self).showMaximized() if isMaximize else super(QQuickView, self).show()
        QTimer.singleShot(500, _delayed_start)

        # self.align_center_on_screen()

    def align_center_on_screen(self):
        # align center on screen
        _x = (self.screen().geometry().width()/2) - (self.width()/2)
        _y = (self.screen().geometry().height()/2) - (self.height()/2)
        self.setPosition(_x, _y)

    def initializeTitleBar(self, use_magnet=False):
        self.use_magnet = use_magnet
        self.titleBar = self.rootObject().findChild(QObject, 'titleBar')
        assert self.titleBar
        self.titleBar.sig_close.connect(self.on_close)
        self.titleBar.sig_minimize.connect(self.on_minimize)
        self.titleBar.sig_maximize.connect(self.on_maximize)
        self.titleBar.sig_moved.connect(self.on_titlebar_moved)
        self.titleBar.sig_released.connect(self.on_titlebar_released)

    @pyqtSlot()
    def on_close(self):
        self.close()

    @pyqtSlot()
    def on_minimize(self):
        self.setWindowState(Qt.WindowMinimized)

    @pyqtSlot()
    def on_maximize(self):
        if self.isFullscreen == False:
            self.setWindowState(Qt.WindowFullScreen) if _IS_MAC else self.setWindowState(Qt.WindowMaximized)
            self.isFullscreen = True
        else:
            self.setWindowState(Qt.WindowNoState)
            self.isFullscreen = False

    @pyqtSlot(float, float)
    def on_titlebar_moved(self, _x, _y):
        if self.windowState() == Qt.WindowFullScreen or self.windowState() == Qt.WindowMaximized:
            return

        displacement_x = self.framePosition().x() + _x
        displacement_y = self.framePosition().y() + _y
        self.setFramePosition(QPoint(int(displacement_x), int(displacement_y)))

    @pyqtSlot(float, float)
    def on_titlebar_released(self, _x, _y):
        if not self.use_magnet:
            return

        # Hot Corner Magnet
        offset = [40, 65] if _IS_MAC else [40, 40]
        if self.framePosition().x() - self.screen().geometry().x() < offset[0] \
                and self.framePosition().y() - self.screen().geometry().y() < offset[1]:
            self.setFramePosition(QPoint(self.screen().geometry().x(), self.screen().geometry().y()))
        elif (self.screen().geometry().x() + self.screen().geometry().width()) - \
                (self.frameGeometry().x() + self.frameGeometry().width()) < offset[0] \
                and self.framePosition().y() - self.screen().geometry().y() < offset[1]:
            new_x = (self.screen().geometry().x() + self.screen().geometry().width()) - self.frameGeometry().width()
            new_y = self.screen().geometry().y()
            new_point = QPoint(new_x, new_y)
            self.setFramePosition(new_point)

    @pyqtSlot(QScreen)
    def on_screen_changed(self, screen):
        if self.isScreenChanged == False:
            self.isScreenChanged = True
        else:
            self.isScreenChanged = False

    @pyqtSlot(object)
    def repaint_item(self, item):
        """
        NOTE Force update.
        """
        item.update()
        _qapp.qapp.sendEvent(item.window(), QEvent(QEvent.UpdateRequest))


class MAIN_QWIN():
    _win = None
