import QtQuick 2.0
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

    Text {
      id: txt_thumbnail
      anchors.fill: inner_rect_thumbnail
      text: ""
      clip: true
      color: "white"
      font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize
      verticalAlignment: Text.AlignVCenter
    }

    MouseArea {
      id: mouse_thumbnail
      anchors.fill: parent
      acceptedButtons: Qt.AllButtons
      hoverEnabled: true

      drag.target: thumbnail_item
      drag.axis: Drag.XAxis | Drag.YAxis
      drag.threshold: 0

      property var prev_x: 0
      property var prev_y: 0

      onContainsMouseChanged: {
        thumbnail_item.highlight = containsMouse;
        sliceview_topbar_thumbnail.sigHighlight(model.study_uid, model.series_uid, containsMouse);
      }

      /*onClicked: {
        selected = !selected;
      }*/

      onPressed: {
        prev_x = thumbnail_item.x;
        prev_y = thumbnail_item.y;
        close_thumbnail.visible = false;
        sliceview_topbar_thumbnail.sigHighlight(model.study_uid, model.series_uid, true);
        thumbnail_item.z = 10;
      }

      onReleased: {
        var _x = thumbnail_item.x + (thumbnail_item.width / 2);
        var _y = thumbnail_item.y - sliceview_topbar_thumbnail.height + (thumbnail_item.height / 2);
        var src_obj = sliceview_mxn_layout.getGridLayoutItem();
        var _obj = src_obj.childAt(_x, _y);

        // should be called after search obj
        thumbnail_item.x = prev_x;
        thumbnail_item.y = prev_y;
        prev_x = 0;
        prev_y = 0;

        close_thumbnail.visible = true;
        sliceview_topbar_thumbnail.sigHighlight(model.study_uid, model.series_uid, false);
        thumbnail_item.highlight = false;
        thumbnail_item.z = 1;

        if ((_obj == null) || (_obj.objectName != 'img_holder_root')) {
          return;
        }

        var picked_layout_id = _obj.children[1].getIndex();
        sliceview_topbar_thumbnail.sigDrop(picked_layout_id, model.study_uid, model.series_uid);
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
    color: '#406084'

    MouseArea {
      id: mouse_close_thumbnail
      anchors.fill: parent
      acceptedButtons: Qt.LeftButton

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

    txt_thumbnail.text = ('ID : %1\nName : %2\nSeries : %3\nDate : %4\nModality : %5')
                          .arg(_patient_id).arg(_patient_name).arg(_series_id).arg(_date).arg(_modality);

    model = _model;
  }

  function isExist(_study_uid, _series_uid)
  {
    if ((model.study_uid == _study_uid) && (model.series_uid == _series_uid))
      return true;
    return false;
  }
}