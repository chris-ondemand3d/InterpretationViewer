import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0
import cyhub 1.0

import "../style"


Item {
  id: sliceview_topbar_panel_item
  objectName: "sliceview_topbar_panel_item"

  width: 800
  height: 30

  Rectangle{
    anchors.fill: parent
    color: '#404040'
    //color: '#252528'
  }

  Rectangle {
    id: title_sc_topbar_panel
    color: CyStyle.dbmwindow.data_infomation_bg_color
    anchors.left: parent.left
    anchors.top: parent.top

    width: 25
    height: parent.height

    Text {
      anchors.fill: parent
      text: 'S\nT\nD'
      horizontalAlignment: Text.AlignHCenter
      verticalAlignment: Text.AlignVCenter
      color: CyStyle.dbmwindow.common_font_color
      font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize
      font.bold: true
    }
  }

}