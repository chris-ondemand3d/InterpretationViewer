import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0
import cyhub 1.0

import "../"
import "../style"


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
  SliceView_topbar_panel {
    id: sliceview_topbar_panel
    objectName: "sliceview_topbar_panel"
    height: 70

    anchors.left: sliceview_menu_panel.right
    anchors.top: parent.top
    anchors.right: parent.right
  }

  // Topbar Thumbnail
  SliceView_topbar_thumbnail {
    id: sliceview_topbar_thumbnail
    objectName: "sliceview_topbar_thumbnail"
    height: 100

    anchors.left: sliceview_menu_panel.right
    anchors.top: sliceview_topbar_panel.bottom
    anchors.right: parent.right
  }

  // Menu Panel
  SliceView_menu_panel {
    id: sliceview_menu_panel
    objectName: "sliceview_menu_panel"

    width: 0

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
  SliceView_MxN_layout {
    id: sliceview_mxn_layout
    objectName: "sliceview_mxn_layout"

    anchors.left: sliceview_menu_panel.right
    anchors.top: sliceview_topbar_thumbnail.bottom
    anchors.right: parent.right
    anchors.bottom: bottombar_panel.top
  }

}