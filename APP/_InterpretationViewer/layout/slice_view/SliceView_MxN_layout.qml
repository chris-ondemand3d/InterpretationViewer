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

      ColumnLayout {

        id: img_holder_root
        spacing: 0
        width: grid.colMulti * columnSpan - 0.5
        height: grid.rowMulti * rowSpan - 0.5

        property var column: 0
        property var columnSpan: 1
        property var row: 0
        property var rowSpan: 1

        Rectangle {
          width : vtk_img_holder.width
          height : 30
          implicitWidth: vtk_img_holder.width
          implicitHeight: 30
          color: '#232323'
        }

        ImageHolder {
          id: vtk_img_holder
          property var name: "vtk_img_holder"

          Layout.alignment: Qt.AlignTop
          Layout.column: parent.column
          Layout.columnSpan: parent.columnSpan
          Layout.row: parent.row
          Layout.rowSpan: parent.rowSpan
          Layout.preferredWidth  : grid.colMulti * parent.columnSpan - 0.5
          Layout.preferredHeight : grid.rowMulti * parent.rowSpan - 0.5
          fullscreenTrigger: false

          onMouseDoubleClicked: {
            fullscreenTrigger = !fullscreenTrigger;
          }

          onFullscreenTriggerChanged: {
            onFullscreen(fullscreenTrigger, img_holder_root)
          }

        }
      }
    }
  }

  Component.onCompleted: {
    for (var i=0; i < repeater_imgholder_sliceview.count; i++)
    {
        var y = parseInt((i / grid.columns))
        var x = i % grid.columns
        var item = repeater_imgholder_sliceview.itemAt(i)

        item.column = x
        item.row = y
    }
  }

  function onFullscreen(bFullscreen, target_item)
  {
    for (var i=0; i < repeater_imgholder_sliceview.count; i++)
    {
      var _item = repeater_imgholder_sliceview.itemAt(i)
      var _topbar_item = _item.children[0]
      var _vtkimg_item = _item.children[1]

      if (bFullscreen){
        _item.visible = false
      }
      else {
        _item.visible = true
        var y = parseInt((i / grid.columns))
        var x = i % grid.columns
        _vtkimg_item.Layout.column = _item.column
        _vtkimg_item.Layout.columnSpan = _item.columnSpan
        _vtkimg_item.Layout.row = _item.row
        _vtkimg_item.Layout.rowSpan = _item.rowSpan
        _vtkimg_item.Layout.preferredWidth  = grid.colMulti * _item.columnSpan - 0.5
        _vtkimg_item.Layout.preferredHeight = grid.rowMulti * _item.rowSpan - 0.5
      }
    }

    // should be called at last
    if (bFullscreen){
      var _item = target_item
      var _topbar_item = _item.children[0]
      var _vtkimg_item = _item.children[1]
      _item.visible = true
      _vtkimg_item.Layout.column = 0
      _vtkimg_item.Layout.columnSpan = grid.columns
      _vtkimg_item.Layout.row = 0
      _vtkimg_item.Layout.rowSpan = grid.rows
      _vtkimg_item.Layout.preferredWidth  = grid.width
      _vtkimg_item.Layout.preferredHeight = grid.height
    }

  }
}