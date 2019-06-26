import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0
import cyhub 1.0

import './style'


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

    rows    : 12
    columns : 12

    rowSpacing: 1
    columnSpacing: 1

    property double colMulti : grid.width / grid.columns
    property double rowMulti : grid.height / grid.rows
    function prefWidth(item){
        return (colMulti * item.Layout.columnSpan) - 0.5
    }
    function prefHeight(item){
        return (rowMulti * item.Layout.rowSpan) - 0.5
    }


    ImageHolder {
    //Rectangle {
      //color: 'purple'
      id: vtk_coronal
      objectName: name
      property var name: "vtk_coronal"
      property var prev_width: 0
      property var prev_height: 0

      property var column: 0
      property var columnSpan: 6
      property var row: 0
      property var rowSpan: 6

      onColumnChanged: {
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
      }

      Layout.alignment: Qt.AlignTop
      Layout.column: column
      Layout.columnSpan: columnSpan
      Layout.row: row
      Layout.rowSpan: rowSpan
      Layout.preferredWidth  : grid.prefWidth(this)
      Layout.preferredHeight : grid.prefHeight(this)

      Rectangle {
        id: rect_coronal_label
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.leftMargin: 10
        anchors.topMargin: 10
        width: 85
        height: 20
        color: '#1A1B1B'
        opacity: 0.8
        radius: 15

        Text{
          color: "white"
          text: "Coronal"
          anchors.fill: parent
          horizontalAlignment: Text.AlignHCenter
          verticalAlignment: Text.AlignVCenter
          font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize
        }
      }

      Item{
        anchors{
          left: rect_coronal_label.left
          verticalCenter: rect_coronal_label.verticalCenter
        }
        z: 2
        width: 10
        height: 20
        clip: true

        Rectangle{
          width: 20
          height: 20
          radius: 10
          color: "#2E8DC8"
        }
      }

    }

    ImageHolder {
    //Rectangle {
      //color: 'purple'
      id: vtk_sagittal
      objectName: name
      property var name: "vtk_sagittal"
      property var prev_width: 0
      property var prev_height: 0

      property var column: 6
      property var columnSpan: 6
      property var row: 0
      property var rowSpan: 6

      onColumnChanged: {
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
      }

      Layout.alignment: Qt.AlignTop
      Layout.column: column
      Layout.columnSpan: columnSpan
      Layout.row: row
      Layout.rowSpan: rowSpan
      Layout.preferredWidth  : grid.prefWidth(this)
      Layout.preferredHeight : grid.prefHeight(this)

      Rectangle {
        id: rect_sagittal_label
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.leftMargin: 10
        anchors.topMargin: 10
        width: 85
        height: 20
        color: '#1A1B1B'
        opacity: 0.8
        radius: 15

        Text{
          color: "white"
          text: "Sagittal"
          anchors.fill: parent
          horizontalAlignment: Text.AlignHCenter
          verticalAlignment: Text.AlignVCenter
          font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize
        }
      }

      Item{
        anchors{
          left: rect_sagittal_label.left
          verticalCenter: rect_sagittal_label.verticalCenter
        }
        z: 2
        width: 10
        height: 20
        clip: true

        Rectangle{
          width: 20
          height: 20
          radius: 10
          color: "#BCEC00"
        }
      }

    }

    ImageHolder {
    //Rectangle {
      //color: 'purple'
      id: vtk_axial
      objectName: name
      property var name: "vtk_axial"
      property var prev_width: 0
      property var prev_height: 0

      property var column: 0
      property var columnSpan: 6
      property var row: 6
      property var rowSpan: 6

      onColumnChanged: {
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
      }

      Layout.alignment: Qt.AlignTop
      Layout.column: column
      Layout.columnSpan: columnSpan
      Layout.row: row
      Layout.rowSpan: rowSpan
      Layout.preferredWidth  : grid.prefWidth(this)
      Layout.preferredHeight : grid.prefHeight(this)

      Rectangle {
        id: rect_axial_label
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.leftMargin: 10
        anchors.topMargin: 10
        width: 85
        height: 20
        color: '#1A1B1B'
        opacity: 0.8
        radius: 15

        Text{
          color: "white"
          text: "Axial"
          anchors.fill: parent
          horizontalAlignment: Text.AlignHCenter
          verticalAlignment: Text.AlignVCenter
          font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize
        }
      }

      Item{
        anchors{
          left: rect_axial_label.left
          verticalCenter: rect_axial_label.verticalCenter
        }
        z: 2
        width: 10
        height: 20
        clip: true

        Rectangle{
          width: 20
          height: 20
          radius: 10
          color: "#cd3e00"
        }
      }

    }

    //ImageHolder
    Rectangle {
      color: 'black'
      id: vtk_none
      objectName: name
      property var name: "vtk_none"
      property var prev_width: 0
      property var prev_height: 0

      property var column: 6
      property var columnSpan: 6
      property var row: 6
      property var rowSpan: 6

      onColumnChanged: {
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
      }

      Layout.alignment: Qt.AlignTop
      Layout.column: column
      Layout.columnSpan: columnSpan
      Layout.row: row
      Layout.rowSpan: rowSpan
      Layout.preferredWidth  : grid.prefWidth(this)
      Layout.preferredHeight : grid.prefHeight(this)
    }

  }
}