import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0
import cyhub 1.0


Item {
  id: dbm_win_root
  width: 1000
  height: 700

  Rectangle{
    id: bg
    anchors.fill: parent
    color: 'darkgray'
  }

  // Bottom Panel
  COMMON_bottombar {
    id: bottombar_panel
    objectName: "bottombar_panel"

    height: 20

    anchors.left: parent.left
    anchors.right: parent.right
    anchors.bottom: parent.bottom
  }

  SplitView {
    id: dbm_split_view
    anchors.left: parent.left
    anchors.top: parent.top
    anchors.right: parent.right
    anchors.bottom: bottombar_panel.top
    orientation: Qt.Vertical

    Rectangle {
      color: 'red'
      height: dbm_split_view.height / 3
      Layout.minimumHeight: 100
      Layout.maximumHeight: 700
    }

    Rectangle {
      color: 'green'
      height: dbm_split_view.height / 3
      Layout.minimumHeight: 100
      Layout.maximumHeight: 700
    }

    Rectangle {
      color: 'blue'
      height: dbm_split_view.height / 3
      Layout.minimumHeight: 100
      Layout.maximumHeight: 700
    }

  }
}