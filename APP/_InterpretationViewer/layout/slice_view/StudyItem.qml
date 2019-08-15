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
          close_study.visible = false;
          study_item.grabImage();
        }
      }

      onReleased: {
        if ((mouse_study.previousGlobalPosition != null) && (mouse.button == Qt.LeftButton))
        {
          var mouse_grid = sliceview_mxn_layout.mapFromGlobal(mouse_study.previousGlobalPosition.x,
                                                              mouse_study.previousGlobalPosition.y);
          var _x = mouse_grid.x;
          var _y = mouse_grid.y;

          // should be called after search obj
          close_study.visible = true;
          sliceview_topbar_panel.sigReleaseDummyThumbnail();
          img_sc_dummythumbnail.set_default_mode();

          var _obj = win_root.childAt(_x, _y);

          if ((_obj == null)) {
            sliceview_topbar_panel.sigDropToOtherApp(mouse_study.previousGlobalPosition, model.study_uid);
            pressed_button = 0;
            return;
          }
        }
        else
        {
          // should be called after search obj
          close_study.visible = true;
          sliceview_topbar_panel.sigReleaseDummyThumbnail();
        }

        pressed_button = 0;

      }

      onPositionChanged: {
        if (pressed && (pressed_button == Qt.LeftButton))
        {
          mouse_study.previousGlobalPosition = study_item.mapToGlobal(mouse.x, mouse.y);
          sliceview_topbar_panel.sigPositionChanged_Global(mouse_study.previousGlobalPosition, study_item.grabbedImageUrl, 'study_thumbnail');

          var mouse_root = win_root.mapFromGlobal(mouse_study.previousGlobalPosition.x,
                                                  mouse_study.previousGlobalPosition.y);
          img_sc_dummythumbnail.set_study_preview_mode();
          img_sc_dummythumbnail.visible = true;
          img_sc_dummythumbnail.x = mouse_root.x - (study_item.width / 2);
          img_sc_dummythumbnail.y = mouse_root.y - (study_item.height / 2);
          if (grabbedImageUrl != null)
            img_sc_dummythumbnail.source = grabbedImageUrl;
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

    txt_study.text = ('%1\n%2').arg(_patient_name).arg(_date);
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

  function grabImage()
  {
    study_item.grabToImage(function(result) {
       //result.saveToFile("../_tmp/grabbedimg.png");
       study_item.grabbedImageUrl = result.url;
    });

  }

}
