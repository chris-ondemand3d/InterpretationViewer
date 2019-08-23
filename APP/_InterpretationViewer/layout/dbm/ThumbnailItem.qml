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

  width: 180
  height: 150

  property var model: ""
  property var img: ""

  Rectangle{
    id: outer_rect_thumbnail
    anchors.fill: parent
    color: '#474747'
    radius: 7

    Rectangle{
      id: inner_rect_thumbnail
      anchors.fill: parent
      anchors.margins: 2
      color: '#636363'
      radius: 7
    }

    Image {
      id: img_thumbnail
      objectName: "img_thumbnail"
      anchors.fill: parent
      anchors.margins: 2
      fillMode: Image.PreserveAspectCrop
      smooth: true
      source: thumbnail_item.img

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

    Text {
      id: txt_dbm_thumbnail_modality
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
      id: txt_dbm_thumbnail_patient_name
      anchors{
        left: inner_rect_thumbnail.left
        right: inner_rect_thumbnail.right
        bottom: txt_dbm_thumbnail_date.top
        leftMargin: 5
        rightMargin: 5
        topMargin: 0
        bottomMargin: 0
      }
      text: ""
      clip: true
      color: "white"
      font.bold: true
      font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize - 1
      verticalAlignment: Text.AlignVCenter
      horizontalAlignment: Text.AlignHCenter
    }

    Text {
      id: txt_dbm_thumbnail_date
      anchors{
        left: inner_rect_thumbnail.left
        right: inner_rect_thumbnail.right
        bottom: txt_dbm_thumbnail_series_id.top
        leftMargin: 5
        rightMargin: 5
        topMargin: 0
        bottomMargin: 0
      }
      text: ""
      clip: true
      color: "white"
      font.bold: true
      font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize - 1
      verticalAlignment: Text.AlignVCenter
      horizontalAlignment: Text.AlignHCenter
    }

    Text {
      id: txt_dbm_thumbnail_series_id
      anchors{
        left: inner_rect_thumbnail.left
        right: inner_rect_thumbnail.right
        bottom: inner_rect_thumbnail.bottom
        leftMargin: 5
        rightMargin: 5
        topMargin: 0
        bottomMargin: 2
      }
      text: ""
      clip: true
      color: "white"
      font.bold: true
      font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize - 1
      verticalAlignment: Text.AlignVCenter
      horizontalAlignment: Text.AlignHCenter
    }

  }

  // function
  function setModel(_model)
  {
    var _patient_id = _model.patient_id;
    var _patient_name = _model.patient_name;
    var _study_uid = _model.study_uid;
    var _series_uid = _model.series_uid;
    var _series_id = _model.series_id;
    var _date = _model.date;
    var _modality = _model.modality;

    txt_dbm_thumbnail_modality.text = _modality;
    txt_dbm_thumbnail_patient_name.text = _patient_name;
    txt_dbm_thumbnail_date.text = _date;
    txt_dbm_thumbnail_series_id.text = _series_id;

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

}