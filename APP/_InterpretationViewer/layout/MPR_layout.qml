import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0
import cyhub 1.0


Item {
  id: win_root
  width: 1000
  height: 700

  Rectangle{
    id: bg
    anchors.fill: parent
    color: 'darkgray'
  }

  // Topbar Panel
  MPR_topbar_panel {
    id: mpr_topbar_panel
    objectName: "mpr_topbar_panel"
    height: 35

    anchors.left: mpr_menu_panel.right
    anchors.top: parent.top
    anchors.right: parent.right
  }

  // Menu Panel
  MPR_menu_panel {
    id: mpr_menu_panel
    objectName: "mpr_menu_panel"

    width: 80

    anchors.left: parent.left
    anchors.top: parent.top
    anchors.bottom: bottombar_panel.top
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

  // View Layout
  MPR_4x4_layout {
    id: mpr_4x4_layout
    objectName: "mpr_4x4_layout"

    anchors.left: mpr_menu_panel.right
    anchors.top: mpr_topbar_panel.bottom
    anchors.right: parent.right
    anchors.bottom: bottombar_panel.top
  }

}