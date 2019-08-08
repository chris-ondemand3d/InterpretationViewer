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

  Rectangle{
    anchors.fill: parent
    color: (selected == true) ? '#999999' : '#636363'

    Text {
      id: txt_thumbnail
      anchors.fill: parent
      text: ""
      clip: true
      font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize
    }

    MouseArea {
      id: mouse_thumbnail
      anchors.fill: parent
      acceptedButtons: Qt.AllButtons

      drag.target: thumbnail_item
      drag.axis: Drag.XAxis | Drag.YAxis
      drag.threshold: 0

      property var prev_x: 0
      property var prev_y: 0

      /*onClicked: {
        selected = !selected;
      }*/

      onPressed: {
        prev_x = thumbnail_item.x;
        prev_y = thumbnail_item.y;
        close_thumbnail.visible = false;
        sliceview_topbar_thumbnail.sigHighlight(model.study_uid, model.series_uid, true);
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
      topMargin: 3
      right: parent.right
      rightMargin: 3
    }
    width: 15
    height: 15
    color: '#406084'

    MouseArea {
      id: mouse_close_thumbnail
      anchors.fill: parent
      acceptedButtons: Qt.LeftButton

      onClicked: {
        sliceview_topbar_thumbnail.sigClose(model.study_uid, model.series_uid, false);
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
}