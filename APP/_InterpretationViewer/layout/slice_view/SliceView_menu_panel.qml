import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0
import cyhub 1.0

import "../style"


Item {
  id: sliceview_menu_panel_item
  objectName: "sliceview_menu_panel_item"

  width: 150
  height: 600

  Rectangle{
    anchors.fill: parent
    color: '#252528'
  }

  Rectangle {
    id: tools_title
    width: parent.width
    height: 25
    //Layout.preferredWidth: parent.width
    //Layout.preferredHeight: height
    color: "#131313"

    Text {
      width: parent.width
      height: parent.height
      verticalAlignment: Text.AlignVCenter
      horizontalAlignment: Text.AlignHCenter
      text: "Tools"
      color: 'lightgray'
      font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize
      font.bold: true
    }
  }

  ColumnLayout {
    //anchors.fill: parent
    anchors {
      top: tools_title.bottom
      left: parent.left
      right: parent.right
      bottom: parent.bottom
    }
    anchors.topMargin: 5
    anchors.bottomMargin: 5
    spacing: 20

    ToolBox {
      id: sliceview_menu_common
      objectName: "sliceview_menu_common"

      Layout.preferredWidth: width
      Layout.preferredHeight: height

      title: "Common"
      itemModel: toolbox_models.getCommonModel()

      onSigToggleOn: {
        // NOTE be sure to add other toolbox's releaseAll() when adding a new toolbox.
        sliceview_menu_measure.releaseAll();
      }
    }

    ToolBox {
      id: sliceview_menu_measure
      objectName: "sliceview_menu_measure"

      Layout.preferredWidth: width
      Layout.preferredHeight: height

      title: "Measure"
      itemModel: toolbox_models.getMeasureModel()

      onSigToggleOn: {
        // NOTE be sure to add other toolbox's releaseAll() when adding a new toolbox.
        sliceview_menu_common.releaseAll();
      }
    }

    ToolBoxModels{
      id: toolbox_models
    }

    // dummy
    Item {
      //Layout.fillWidth: true
      Layout.fillHeight: true
    }
  }

}