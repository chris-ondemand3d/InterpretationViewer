import QtQuick 2.10
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0
import cyhub 1.0

import '../style'


Item {
  id: thumbnail_item
  objectName: "thumbnail_item"

  width: 120
  height: 100

  property var selected: false
  property var model: ""
  property var highlight: false

  property var grabbedImageUrl: null

  Rectangle{
    id: outer_rect_thumbnail
    anchors.fill: parent
    //color: (selected == true) ? '#999999' : '#636363'
    color: (highlight === true) ? '#696975' : '#232323'
    radius: 7

    Rectangle{
      id: inner_rect_thumbnail
      anchors.fill: parent
      anchors.margins: 4
      color: '#636363'
      radius: 7
    }

    Image {
      id: img_thumbnail
      objectName: "img_thumbnail"
      anchors.fill: parent
      anchors.margins: 4
      fillMode: Image.PreserveAspectCrop
      smooth: true
      source: ""

      property bool rounded: true
      property bool adapt: true

      layer.enabled: rounded
      layer.effect: OpacityMask {
        maskSource: Item {
          width: img_thumbnail.width
          height: img_thumbnail.height
          Rectangle {
            anchors.centerIn: parent
            width: img_thumbnail.adapt ? img_thumbnail.width : Math.min(img_thumbnail.width, img_thumbnail.height)
            height: img_thumbnail.adapt ? img_thumbnail.height : width
            radius: img_thumbnail.parent.radius
          }
        }
      }

    }

    // debug
    /*Text {
      id: txt_thumbnail
      anchors.fill: inner_rect_thumbnail
      text: ""
      clip: true
      color: "white"
      font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize
      verticalAlignment: Text.AlignVCenter
    }*/

    Text {
      id: txt_thumbnail_modality
      anchors{
        left: inner_rect_thumbnail.left
        top: inner_rect_thumbnail.top
        leftMargin: 5
        topMargin: 5
      }
      text: ""
      clip: true
      color: "white"
      font.bold: true
      font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize
      verticalAlignment: Text.AlignVCenter
    }

    Text {
      id: txt_thumbnail_patient_name
      anchors{
        left: inner_rect_thumbnail.left
        right: inner_rect_thumbnail.right
        bottom: txt_thumbnail_date.top
        leftMargin: 5
        rightMargin: 5
        topMargin: 0
        bottomMargin: 0
      }
      text: ""
      clip: true
      color: "white"
      font.bold: true
      font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize
      verticalAlignment: Text.AlignVCenter
      //horizontalAlignment: Text.AlignHCenter
    }

    Text {
      id: txt_thumbnail_date
      anchors{
        left: inner_rect_thumbnail.left
        right: inner_rect_thumbnail.right
        bottom: inner_rect_thumbnail.bottom
        leftMargin: 5
        rightMargin: 5
        topMargin: 0
        bottomMargin: 0
      }
      text: ""
      clip: true
      color: "white"
      font.bold: true
      font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize
      verticalAlignment: Text.AlignVCenter
      horizontalAlignment: Text.AlignHCenter
    }

    MouseArea {
      id: mouse_thumbnail
      anchors.fill: parent
      acceptedButtons: Qt.LeftButton | Qt.RightButton
      hoverEnabled: true
      pressAndHoldInterval: 500

      property var pressed_button: 0
      property var previousGlobalPosition: null

      onPositionChanged: {
        if (pressed && (pressed_button == Qt.LeftButton))
        {
          mouse_thumbnail.previousGlobalPosition = thumbnail_item.mapToGlobal(mouse.x, mouse.y);
          sliceview_topbar_thumbnail.sigPositionChanged_Global(mouse_thumbnail.previousGlobalPosition, thumbnail_item.grabbedImageUrl, 'series_thumbnail');

          var mouse_root = win_root.mapFromGlobal(mouse_thumbnail.previousGlobalPosition.x,
                                                  mouse_thumbnail.previousGlobalPosition.y);
          img_sc_dummythumbnail.set_default_mode();
          img_sc_dummythumbnail.visible = true;
          img_sc_dummythumbnail.x = mouse_root.x - (thumbnail_item.width / 2);
          img_sc_dummythumbnail.y = mouse_root.y - (thumbnail_item.height / 2);
          if (grabbedImageUrl != null)
            img_sc_dummythumbnail.source = grabbedImageUrl;
        }
      }

      onContainsMouseChanged: {
        thumbnail_item.highlight = containsMouse;
        sliceview_topbar_thumbnail.sigHighlight(model.study_uid, model.series_uid, containsMouse);
      }

      onPressed: {
        pressed_button = mouse.button;
        if (mouse.button == Qt.LeftButton)
        {
          close_thumbnail.visible = false;
          thumbnail_item.highlight = true;
          thumbnail_item.grabImage();
          sliceview_topbar_thumbnail.sigHighlight(model.study_uid, model.series_uid, true);
        }
      }

      onReleased: {
        if ((mouse_thumbnail.previousGlobalPosition != null) && (mouse.button == Qt.LeftButton))
        {
          var mouse_grid = sliceview_mxn_layout.mapFromGlobal(mouse_thumbnail.previousGlobalPosition.x,
                                                              mouse_thumbnail.previousGlobalPosition.y);
          var _x = mouse_grid.x;
          var _y = mouse_grid.y;
          var src_obj = sliceview_mxn_layout.getGridLayoutItem();
          var _obj = src_obj.childAt(_x, _y);

          // should be called after search obj
          close_thumbnail.visible = true;
          sliceview_topbar_thumbnail.sigHighlight(model.study_uid, model.series_uid, false);
          sliceview_topbar_thumbnail.sigReleaseDummyThumbnail();
          thumbnail_item.highlight = false;
          img_sc_dummythumbnail.set_default_mode();

          if ((_obj == null) || (_obj.objectName != 'img_holder_root')) {
            sliceview_topbar_thumbnail.sigDropToOtherApp(mouse_thumbnail.previousGlobalPosition, model.study_uid, model.series_uid);
            pressed_button = 0;
            return;
          }

          var picked_layout_id = _obj.children[1].getIndex();
          sliceview_topbar_thumbnail.sigDrop(picked_layout_id, model.study_uid, model.series_uid);
        }
        else
        {
          // should be called after search obj
          close_thumbnail.visible = true;
          sliceview_topbar_thumbnail.sigHighlight(model.study_uid, model.series_uid, false);
          sliceview_topbar_thumbnail.sigReleaseDummyThumbnail();
          thumbnail_item.highlight = false;
        }

        pressed_button = 0;

      }

      onPressAndHold: {
        if (pressed_button == 1)
        {
          var _mouse_global = thumbnail_item.mapToGlobal(mouse.x, mouse.y);
          var mouse_root = win_root.mapFromGlobal(_mouse_global.x, _mouse_global.y);
          img_sc_dummythumbnail.set_series_preview_mode();
          img_sc_dummythumbnail.visible = true;
          img_sc_dummythumbnail.x = mouse_root.x;
          img_sc_dummythumbnail.y = mouse_root.y;
          if (grabbedImageUrl != null)
            img_sc_dummythumbnail.source = img_thumbnail.source;
        }
      }
    }
  }

  Rectangle {
    id: close_thumbnail
    anchors{
      top: parent.top
      topMargin: 5
      right: parent.right
      rightMargin: 5
    }
    width: 15
    height: 15
    color: '#FF4343'
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

      visible: mouse_close_thumbnail.containsMouse
    }

    MouseArea {
      id: mouse_close_thumbnail
      anchors.fill: parent
      acceptedButtons: Qt.LeftButton
      hoverEnabled: true

      onClicked: {
        sliceview_topbar_thumbnail.sigClose(model.study_uid, model.series_uid);
      }
    }
  }

  function setModel(_model)
  {
    var _patient_id = _model.patient_id;
    var _patient_name = _model.patient_name;
    var _study_uid = _model.study_uid;
    var _series_uid = _model.series_uid;
    var _series_id = _model.series_id;
    var _date = _model.date;
    var _modality = _model.modality;

    /*txt_thumbnail.text = ('ID : %1\nName : %2\nSeries : %3\nDate : %4\nModality : %5')
                          .arg(_patient_id).arg(_patient_name).arg(_series_id).arg(_date).arg(_modality);*/
    txt_thumbnail_modality.text = _modality;
    txt_thumbnail_patient_name.text = _patient_name;
    txt_thumbnail_date.text = _date;

    model = _model;
  }

  function isExist(_study_uid, _series_uid)
  {
    if ((model.study_uid == _study_uid) && (model.series_uid == _series_uid))
      return true;
    return false;
  }

  function getStudyUID()
  {
    return model.study_uid;
  }

  function getSeriesUID()
  {
    return model.series_uid;
  }

  function grabImage()
  {
    thumbnail_item.grabToImage(function(result) {
       //result.saveToFile("../_tmp/grabbedimg.png");
       thumbnail_item.grabbedImageUrl = result.url;
    });

  }

}