import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0
import cyhub 1.0

import '../style'


Item {
  id: mpr_4x4_layout_item
  objectName: "mpr_4x4_layout_item"

  width: 400
  height: 400

  Rectangle{
    width: parent.width
    height: parent.height
    color: '#303030'
  }

  GridLayout {
    id: grid
    width: parent.width
    height: parent.height
    Layout.preferredWidth: width
    Layout.preferredHeight: height
    Layout.maximumHeight: height
    Layout.maximumWidth: width
    Layout.minimumHeight: height
    Layout.minimumWidth: width

    rows    : 2
    columns : 2

    rowSpacing: 1
    columnSpacing: 1

    property double colMulti : grid.width / grid.columns
    property double rowMulti : grid.height / grid.rows

    Repeater {
      id: repeater_imgholder_sliceview
      objectName: 'repeater_imgholder_sliceview'
      model: grid.rows * grid.columns

      /*
      Rectangle{
        property var column: 0
        property var columnSpan: 1
        property var row: 0
        property var rowSpan: 1
        id: rect_in_repeater
        Layout.alignment: Qt.AlignTop
        Layout.column: column
        Layout.columnSpan: columnSpan
        Layout.row: row
        Layout.rowSpan: rowSpan
        Layout.preferredWidth  : grid.colMulti * columnSpan - grid.columnSpacing
        Layout.preferredHeight : grid.rowMulti * rowSpan - grid.rowSpacing
        color: "green"
      }
      */

      ImageHolder {
        id: vtk_img_holder
        property var name: "vtk_img_holder"

        property var column: 0
        property var columnSpan: 1
        property var row: 0
        property var rowSpan: 1
        Layout.alignment: Qt.AlignTop
        Layout.column: column
        Layout.columnSpan: columnSpan
        Layout.row: row
        Layout.rowSpan: rowSpan
        Layout.preferredWidth  : grid.colMulti * columnSpan - 0.5
        Layout.preferredHeight : grid.rowMulti * rowSpan - 0.5

        /*onColumnChanged: {
          Layout.column = column
        }
        onColumnSpanChanged: {
          Layout.columnSpan = columnSpan
        }
        onRowChanged: {
          Layout.row = row
        }
        onRowSpanChanged: {
          Layout.rowSpan = rowSpan
        }*/

      }
    }
  }

  Component.onCompleted: {
    for (var i=0; i < repeater_imgholder_sliceview.count; i++)
    {
        var column = 0
        var columnSpan = 1
        var row = 0
        var rowSpan = 1

        var y = parseInt((i / grid.columns))
        var x = i % grid.columns
        var item = repeater_imgholder_sliceview.itemAt(i)

        item.column = x
        item.row = y
    }
  }
}