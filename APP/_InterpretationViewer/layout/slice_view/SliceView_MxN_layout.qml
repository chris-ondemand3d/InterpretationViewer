import QtQuick 2.5
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
    id: grid_layout
    objectName: 'grid_layout'
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

    property double colMulti : grid_layout.width / grid_layout.columns
    property double rowMulti : grid_layout.height / grid_layout.rows

    Repeater {
      id: repeater_imgholder_sliceview
      objectName: 'repeater_imgholder_sliceview'
      model: grid_layout.rows * grid_layout.columns

      ColumnLayout {

        id: img_holder_root
        objectName: 'img_holder_root'
        spacing: 0
        width: prefWidth(this)
        height: prefHeight(this)

        property var column: 0
        property var columnSpan: 1
        property var row: 0
        property var rowSpan: 1

        Rectangle {
          id: vtk_img_topbar
          objectName: "vtk_img_topbar"
          width : vtk_img_holder.width
          height : 25
          implicitWidth: prefWidth(parent)
          implicitHeight: 25
          color: (highlight === true) ? '#696975' : '#232323'

          property var highlight: false
        }

        ImageHolder {
          id: vtk_img_holder
          property var name: "vtk_img_holder"

          Layout.alignment: Qt.AlignTop
          Layout.column: parent.column
          Layout.columnSpan: parent.columnSpan
          Layout.row: parent.row
          Layout.rowSpan: parent.rowSpan
          Layout.preferredWidth: prefWidth(parent)
          Layout.preferredHeight: prefHeight(parent) - vtk_img_topbar.height;
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
            anchors{
              top: col_sv_slice_number.bottom
              topMargin: 0
              right: col_sv_slice_number.right
              rightMargin: 0
            }

            signal sigChanged(real val, real idx)

            function reset(){
              cb_sv_thickness.currentIndex = 0;
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
                verticalAlignment: Text.AlignVCenter
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

              function insert_value(value)
              {
                for(var i=0; i<count; i++)
                {
                  var _item_val = parseFloat(get(i).val).toFixed(1)

                  if (parseFloat(_item_val) == parseFloat(value)){
                    break;
                  }

                  if (parseFloat(_item_val) > parseFloat(value)){
                    insert(i, {"val": String(value)});
                    break;
                  }
                }

                append({"val": String(value)});
              }
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
          Column{
            id: col_sv_image_filter
            objectName: "col_sv_image_filter"
            visible: false
            anchors{
              top: (col_sv_thickness.visible === true) ? col_sv_thickness.bottom : col_sv_slice_number.bottom
              topMargin: 0
              right: col_sv_thickness.right
              rightMargin: -5 // optical illusion
            }

            signal sigChanged(string val, real idx)

            function reset(){
              cb_sv_image_filter.currentIndex = 0;
            }

            ListModel {
              id: items_sv_image_filter
              ListElement { val: "Filter Off" }
              ListElement { val: "Gaussian" }
              ListElement { val: "Sharpen" }
              ListElement { val: "Unsharpen" }
              ListElement { val: "Anisotropic" }
              ListElement { val: "Highboost" }
              ListElement { val: "Bilateral" }
            }

            ComboBox {
              id: cb_sv_image_filter
              objectName: "cb_sv_image_filter"
              width: 80
              height: 18  // optical illusion
              editable: false
              visible: true
              focus: visible

              model: items_sv_image_filter

              style: ComboBoxStyle{
                  background: Rectangle {
                      anchors.fill: parent
                      color : "transparent"
                  }
                  label: Text {
                      anchors.fill: parent
                      verticalAlignment: Text.AlignVCenter
                      horizontalAlignment: Text.AlignRight
                      text: control.currentText
                      color: "white"
                  }
              }
              onCurrentIndexChanged: {
                if(currentText != ""){
                  col_sv_image_filter.sigChanged(currentText, index);
                }
              }
              onAccepted: {
                col_sv_image_filter.sigChanged(currentText, index);
              }
            }
          }

          // WWL (RB)
          Column{
            id: col_sv_wwl
            objectName: "col_sv_wwl"
            visible: true

            anchors{
              bottom: parent.bottom
              bottomMargin: 10
              right: parent.right
              rightMargin: 10
            }

            // WWL
            Text{
              id: text_sv_wwl
              width: 50
              height: 30
              text: ""
              color: "white"
              font.pointSize: CyStyle.mainwindow._module_menu_title_font_pointSize
              horizontalAlignment: Text.AlignRight
            }
          }

          // Busy Indicator
          BusyIndicator {
            id: busy_indicator
            objectName: "busy_indicator"
            width: 25;
            height: 25;
            anchors {
              left: parent.left
              bottom: parent.bottom
              leftMargin: 15
              bottomMargin: 15
            }
            running: false
          }

          function getIndex() {
            return index;
          }

          onMouseReleased: {
            // TODO
          }

          // fullscreen event
          onMouseDoubleClicked: {
            fullscreenTrigger = !fullscreenTrigger;
          }

          onFullscreenTriggerChanged: {
            onFullscreen(fullscreenTrigger, img_holder_root)
          }

          function clear(){
            // patient info
            text_sv_patient_id.text = "";
            text_sv_patient_name_age_sex.text = "";
            text_sv_patient_date.text = "";
            text_sv_patient_series_id.text = "";
            // slice number (RT_U)
            text_sv_slice_number.text = "";
            // thickness (RT_M)
            col_sv_thickness.reset();
            col_sv_thickness.visible = false;
            // filter (RT_L)
            col_sv_image_filter.reset();
            col_sv_image_filter.visible = false;
            // WWL (RB)
            text_sv_wwl.text = "";

            vtk_img_topbar.highlight = false;

            busy_indicator.running = false;
          }

          function setBusy(busy)
          {
            busy_indicator.running = busy;
          }

          function setSliceNumber(number){
            text_sv_slice_number.text = ('# %1').arg(number);
          }

          function setThickness(thickness){
            thickness = parseFloat(thickness).toFixed(1);

            if (thickness == -1.0){
              col_sv_thickness.visible = false;
              return;
            }

            col_sv_thickness.visible = true;
            if (cb_sv_thickness.find(String(thickness)) === -1){
              items_sv_thickness.insert_value(thickness);
              cb_sv_thickness.currentIndex = cb_sv_thickness.find(String(thickness));
            }
            else{
              cb_sv_thickness.currentIndex = cb_sv_thickness.find(String(thickness));
            }
            col_sv_thickness.sigChanged(thickness, parseInt(index));
          }

          function setFilter(filter){
            col_sv_image_filter.visible = true;
            var idx = cb_sv_image_filter.find(filter);

            if (idx != -1){
              cb_sv_image_filter.currentIndex = idx;
              col_sv_image_filter.sigChanged(filter, parseInt(index));
            }
          }

          function setWWL(ww, wl){
            text_sv_wwl.text = ('WW : %1\nWL : %2').arg(parseInt(ww)).arg(parseInt(wl));
          }
        }
      }
    }

  }

  Component.onCompleted: {
    for (var i=0; i < repeater_imgholder_sliceview.count; i++)
    {
        var y = parseInt((i / grid_layout.columns))
        var x = i % grid_layout.columns
        var item = repeater_imgholder_sliceview.itemAt(i)

        item.column = x
        item.row = y
    }
  }

  function setBusy(target_item, busy)
  {
    busy_indicator.setBusy(busy);
  }

  function prefWidth(item)
  {
    return (grid_layout.colMulti * item.columnSpan) - 0.5;
  }

  function prefHeight(item)
  {
    return (grid_layout.rowMulti * item.rowSpan) - 0.5;
  }

  function onFullscreen(bFullscreen, target_item)
  {
    for (var i=0; i < repeater_imgholder_sliceview.count; i++)
    {
      var _item = repeater_imgholder_sliceview.itemAt(i);
      var _topbar_item = _item.children[0];
      var _vtkimg_item = _item.children[1];

      if (bFullscreen){
        _item.visible = false;
      }
      else {
        _item.visible = true;
        var y = parseInt((i / grid_layout.columns));
        var x = i % grid_layout.columns;
        _item.column = x;
        _item.row = y;
        _item.columnSpan = 1;
        _item.rowSpan = 1;
      }
    }

    // should be called at last
    if (bFullscreen){
      var _item = target_item;
      var _topbar_item = _item.children[0];
      var _vtkimg_item = _item.children[1];
      _item.visible = true;
      _item.column = 0;
      _item.row = 0;
      _item.columnSpan = grid_layout.columns;
      _item.rowSpan = grid_layout.rows;
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

  function setFilter(target_item, filter)
  {
    target_item.setFilter(filter);
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

  function setWWL(target_item, ww, wl)
  {
    target_item.setWWL(ww, wl);
  }

  function getGridLayoutItem()
  {
    return grid_layout;
  }

}
