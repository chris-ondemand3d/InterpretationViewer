import QtQuick 2.10
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0
import cyhub 1.0

import '../style'


Item {
  id: study_item
  objectName: "study_item"

  width: 130
  height: 60

  property var selected: false
  property var model: ""
  property var highlight: false

  property var grabbedImageUrl: null

  Rectangle{
    id: outer_rect_study
    anchors.fill: parent
    color: (selected === true) ? '#303030' : '#636363'
    radius: 0

    Rectangle{
      id: inner_rect_study
      anchors.fill: parent
      anchors.margins: 5
      color: parent.color
      radius: 0
    }

    // debug
    Text {
      id: txt_study
      anchors.fill: inner_rect_study
      text: ""
      clip: true
      color: "white"
      font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize
      verticalAlignment: Text.AlignBottom
    }

    MouseArea {
      id: mouse_study
      anchors.fill: parent
      acceptedButtons: Qt.LeftButton | Qt.RightButton

      property var pressed_button: 0
      property var previousGlobalPosition: null

      onClicked: {
        if (selected === true)
          return;
        select();
      }

      onPressed: {
        pressed_button = mouse.button;
        if (mouse.button == Qt.LeftButton)
        {
        }
      }

      onReleased: {
      }

      onPositionChanged: {
        if (pressed && (pressed_button == Qt.LeftButton))
        {
        }
      }

    }

  }

  Rectangle {
    id: close_study
    anchors{
      top: parent.top
      topMargin: 5
      right: parent.right
      rightMargin: 5
    }
    width: 15
    height: 15
    color: (selected === true) ? '#FF4343' : '#474747'
    radius: 10

    Text {
      anchors.fill: parent
      color: "black"
      font.pointSize: 10
      font.bold: true
      font.weight: Font.ExtraBold
      verticalAlignment: Text.AlignVCenter
      horizontalAlignment: Text.AlignHCenter
      text: "X"

      visible: mouse_close_study.containsMouse
    }

    MouseArea {
      id: mouse_close_study
      anchors.fill: parent
      acceptedButtons: Qt.LeftButton
      hoverEnabled: true

      onClicked: {
        sliceview_topbar_panel.sigClose(model.study_uid);
      }
    }
  }

  function setModel(_model)
  {
    var _patient_id = _model.patient_id;
    var _patient_name = _model.patient_name;
    var _study_uid = _model.study_uid;
    var _date = _model.date;

    txt_study.text = ('N : %1\nD : %2').arg(_patient_name).arg(_date);
    //txt_thumbnail_patient_name.text = _patient_name;
    //txt_thumbnail_date.text = _date;

    model = _model;
  }

  function select(bSelected)
  {
    if (bSelected === undefined)
      selected = !selected;
    else if (bSelected != selected)
      selected = bSelected;
    else
      return

    if (selected == true)
      sliceview_topbar_panel.sigSelected(index);
  }

  function getStudyUID()
  {
    return model.study_uid;
  }

}
