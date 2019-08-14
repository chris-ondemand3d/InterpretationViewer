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
    height: 60

    anchors.left: parent.left
    anchors.top: parent.top
    anchors.right: parent.right
  }

  // Topbar Thumbnail
  SliceView_topbar_thumbnail {
    id: sliceview_topbar_thumbnail
    objectName: "sliceview_topbar_thumbnail"
    height: 120

    anchors.left: parent.left
    anchors.top: sliceview_topbar_panel.bottom
    anchors.right: parent.right
    z:10
  }

  // Menu Panel
  SliceView_menu_panel {
    id: sliceview_menu_panel
    objectName: "sliceview_menu_panel"

    width: 66

    anchors.left: parent.left
    anchors.top: sliceview_topbar_thumbnail.bottom
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

  // dummy image
  Image {
    id: img_sc_dummythumbnail
    objectName: "img_sc_dummythumbnail"

    width: default_width
    height: default_height
    x: 200
    y: 200
    z: 10
    opacity: 0.7
    visible: false

    fillMode: Image.PreserveAspectCrop
    smooth: true
    source: ""

    property var default_width: 120
    property var default_height: 100
    property var scaled_width: 240
    property var scaled_height: 190
    property var study_preview_width: 130
    property var study_preview_height: 60

    property bool rounded: true
    property bool adapt: true

    layer.enabled: rounded
    layer.effect: OpacityMask {
      maskSource: Item {
        width: img_sc_dummythumbnail.width
        height: img_sc_dummythumbnail.height
        Rectangle {
          anchors.centerIn: parent
          width: img_sc_dummythumbnail.adapt ? img_sc_dummythumbnail.width : Math.min(img_sc_dummythumbnail.width, img_sc_dummythumbnail.height)
          height: img_sc_dummythumbnail.adapt ? img_sc_dummythumbnail.height : width
          radius: 7
        }
      }
    }

    function set_default_mode()
    {
      img_sc_dummythumbnail.width = default_width;
      img_sc_dummythumbnail.height = default_height;
      img_sc_dummythumbnail.opacity = 0.7;
    }

    function set_series_preview_mode()
    {
      img_sc_dummythumbnail.width = scaled_width;
      img_sc_dummythumbnail.height = scaled_height;
      img_sc_dummythumbnail.opacity = 1.0;
    }

    function set_study_preview_mode()
    {
      img_sc_dummythumbnail.width = study_preview_width;
      img_sc_dummythumbnail.height = study_preview_height;
      img_sc_dummythumbnail.opacity = 0.7;
    }
  }

}