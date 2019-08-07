import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0
import cyhub 1.0

import '../style'


Item {
  id: slice_view_layout_item
  objectName: "slice_view_layout_item"

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
          height : 25
          implicitWidth: vtk_img_holder.width
          implicitHeight: 25
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

          // patient info (LT) - Patient ID, Name, Age, Sex, Date, Series ID
          Column{
            id: col_sv_patient_info
            objectName: "col_sv_patient_info"
            visible: true

            anchors{
              top: parent.top
              topMargin: 10
              left: parent.left
              leftMargin: 10
            }

            // Patient ID
            Text{
              id: text_sv_patient_id
              width: 100
              height: 15
              text: ""
              color: "white"
              font.pointSize: CyStyle.mainwindow._module_menu_title_font_pointSize
              verticalAlignment: Text.AlignVCenter
            }

            // Patient Name & Age & Sex
            Text{
              id: text_sv_patient_name_age_sex
              width: 100
              height: 15
              text: ""
              color: "white"
              font.pointSize: CyStyle.mainwindow._module_menu_title_font_pointSize
              verticalAlignment: Text.AlignVCenter
            }

            // Patient Created Date
            Text{
              id: text_sv_patient_date
              width: 100
              height: 15
              text: ""
              color: "white"
              font.pointSize: CyStyle.mainwindow._module_menu_title_font_pointSize
              verticalAlignment: Text.AlignVCenter
            }

            // Patient Series ID
            Text{
              id: text_sv_patient_series_id
              width: 100
              height: 15
              text: ""
              color: "white"
              font.pointSize: CyStyle.mainwindow._module_menu_title_font_pointSize
              verticalAlignment: Text.AlignVCenter
            }

          }

          // slice number (RT_U)
          Column{
            id: col_sv_slice_number
            objectName: "col_sv_slice_number"
            visible: true

            anchors{
              top: parent.top
              topMargin: 10
              right: parent.right
              rightMargin: 10
            }

            // Slice Number
            Text{
              id: text_sv_slice_number
              width: 50
              height: 15
              text: ""
              color: "yellow"
              font.pointSize: CyStyle.mainwindow._module_menu_title_font_pointSize
              horizontalAlignment: Text.AlignRight
            }
          }

          // thickness (RT_M)
          Column{
            id: col_sv_thickness
            objectName: "col_sv_thickness"
            visible: false

            signal sigChanged(real val, real idx)

            function reset(){
              cb_sv_thickness.currentIndex = 0;
            }

            anchors{
              top: col_sv_slice_number.bottom
              topMargin: 0
              right: col_sv_slice_number.right
              rightMargin: 0
            }

            Rectangle{
              id: rect_sv_thickness_title
              width: 80
              height: 15
              color: "transparent"

              Text{
                id: text_sv_thickness
                text: "Th: " + cb_sv_thickness.currentText + " [mm]"
                color: cb_sv_thickness.visible ? "orange" : "white"
                anchors.right: parent.right
                horizontalAlignment: Text.AlignRight
              }

              MouseArea{
                anchors.fill: parent
                hoverEnabled: true
                onClicked: {
                  if(!cb_sv_thickness.visible)
                    cb_sv_thickness.visible = true
                  else
                    cb_sv_thickness.visible = false
                }
                onContainsMouseChanged: {
                  if(containsMouse)
                    cursorShape = Qt.PointingHandCursor
                  else
                    return
                }
              }
            }

            ListModel {
              id: items_sv_thickness

              property double maximumValue: 30.0
              property double minimumValue: 0.0

              ListElement { val: "0.0" }
              ListElement { val: "0.5" }
              ListElement { val: "1.0" }
              ListElement { val: "2.0" }
              ListElement { val: "3.0" }
              ListElement { val: "4.0" }
              ListElement { val: "5.0" }
              ListElement { val: "10.0" }
              ListElement { val: "15.0" }
              ListElement { val: "20.0" }
            }

            ComboBox {
              id: cb_sv_thickness
              width: 80
              editable: true
              visible: false
              focus: visible

              //signal sigChanged(real val, real idx)

              inputMethodHints: Qt.ImhFormattedNumbersOnly
              validator: DoubleValidator {
                bottom: items_sv_thickness.minimumValue
                top: items_sv_thickness.maximumValue
                notation: DoubleValidator.StandardNotation
                decimals: 1
              }
              model: items_sv_thickness

              onCurrentIndexChanged: {
                if(currentText != ""){
                  col_sv_thickness.sigChanged(parseFloat(currentText), parseInt(index));
                  this.visible = false
                }
              }

              onAccepted: {
                col_sv_thickness.sigChanged(parseFloat(currentText), parseInt(index));
                this.visible = false
              }

              onEditTextChanged: {
                if(editText.length >= 2 && editText[0] == "0" && editText[1] != ".")
                  editText = "0"
                if(parseInt(editText) > items_sv_thickness.maximumValue)
                  editText = "30"
                if(editText[0] == "3" && editText[1] == "0" && editText[2] == ".")
                  editText = "30"
              }
              // Temp Source!!!!!!! - by jhjeong  // why?
              /*onVisibleChanged: {
                  if(visible){
                      cb_sv_2d_format.enabled = false
                      col_sv_thickness.z = 1
                  }
                  else{
                      cb_sv_2d_format.enabled = true
                      col_sv_thickness.z = 0
                  }
              }*/
            }
          }

          // filter (RT_L)


          // WWL (RB)


          // fullscreen event
          onMouseDoubleClicked: {
            fullscreenTrigger = !fullscreenTrigger;
          }

          onFullscreenTriggerChanged: {
            onFullscreen(fullscreenTrigger, img_holder_root)
          }

          function clear(){
            // patient info
            text_sv_patient_id.text = ""
            text_sv_patient_name_age_sex.text = ""
            text_sv_patient_date.text = ""
            text_sv_patient_series_id.text = ""
            // slice number (RT_U)
            text_sv_slice_number.text = ""
            // thickness (RT_M)
            col_sv_thickness.reset()
            col_sv_thickness.visible = false
            // filter (RT_L)
            // WWL (RB)
          }

          function setSliceNumber(number){
            text_sv_slice_number.text = ('# %1').arg(number);
          }

          function setThickness(thickness){
            col_sv_thickness.visible = true;
            cb_sv_thickness.currentIndex = thickness;
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

  function setPatientInfo(target_item, id, name, age, sex, date, series_id)
  {
    // id
    var txt_id = target_item.children[0];
    txt_id.text = ('ID : %1').arg(id);

    // name & age & sex
    var txt_name = target_item.children[1];
    txt_name.text = ('Name : %1 [%2%3]').arg(name).arg(String(age) === "undefined" ? "" : age).arg(sex);

    // date
    var txt_date = target_item.children[2];
    txt_date.text = ('Date : %1').arg(date);

    // series id
    var txt_series = target_item.children[3];
    txt_series.text = ('Series : %1').arg(series_id);
  }

  function setSliceNumber(target_item, number)
  {
    target_item.setSliceNumber(number);
  }

  function setThickness(target_item, thickness)
  {
    target_item.setThickness(thickness);
  }

  function clear()
  {
    for (var i=0; i < repeater_imgholder_sliceview.count; i++)
    {
      var _item = repeater_imgholder_sliceview.itemAt(i)
      var _topbar_item = _item.children[0]
      var _vtkimg_item = _item.children[1]
      _vtkimg_item.clear();
    }
  }

}
