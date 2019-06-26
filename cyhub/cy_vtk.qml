import QtQuick 2.0
import cyhub 1.0

Item {
    width: 400
    height: 400

    ImageHolder {
          id: vtk_image
          property var name: "vtk_image"
          objectName: name
          anchors.fill: parent
    }
}