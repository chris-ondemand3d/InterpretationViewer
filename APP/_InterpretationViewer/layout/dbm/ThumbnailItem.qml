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
    color: '#232323'
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

    /*txt_thumbnail.text = ('ID : %1\nName : %2\nSeries : %3\nDate : %4\nModality : %5')
                          .arg(_patient_id).arg(_patient_name).arg(_series_id).arg(_date).arg(_modality);*/
    /*txt_thumbnail_modality.text = _modality;
    txt_thumbnail_patient_name.text = _patient_name;
    txt_thumbnail_date.text = _date;*/

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