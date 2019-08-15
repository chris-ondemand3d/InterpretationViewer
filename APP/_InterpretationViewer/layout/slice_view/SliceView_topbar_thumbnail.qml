import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0
import cyhub 1.0

import "../style"


Item {
  id: sliceview_topbar_thumbnail_item
  objectName: "sliceview_topbar_thumbnail_item"

  width: 800
  height: 30

  signal sigDrop(real picked_layout_id, string study_uid, string series_uid)
  signal sigHighlight(string study_uid, string series_uid, bool on)
  signal sigReleaseDummyThumbnail()
  signal sigClose(string study_uid, string series_uid)

  signal sigPositionChanged_Global(var global_mosue, var img_url, var mode)
  signal sigDropToOtherApp(var global_mouse, string study_uid, string series_uid)

  ListModel {
    id: items_sv_thumbnail
    objectName: "items_sv_thumbnail"
  }

  // for model copy
  ListModel {
    id: items_sv_thumbnail_dummy
  }

  Rectangle{
    anchors.fill: parent
    color: '#303030'

    Text {
      width: parent.width
      height: parent.height
      verticalAlignment: Text.AlignVCenter
      horizontalAlignment: Text.AlignHCenter
      text: "S    E    R    I    E    S"
      color: 'lightgray'
      font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize + 10
      font.bold: true
      opacity: 0.1
    }

  }

  Rectangle {
    id: title_sc_topbar_thumbnail
    color: CyStyle.dbmwindow.data_infomation_bg_color
    anchors.left: parent.left
    anchors.top: parent.top

    width: 35
    height: parent.height

    visible: false

    Text {
      anchors.fill: parent
      text: 'S\nR'
      horizontalAlignment: Text.AlignHCenter
      verticalAlignment: Text.AlignVCenter
      color: CyStyle.dbmwindow.common_font_color
      font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize
      font.bold: true
    }
  }

  ScrollView {
    id: scroll_sv_thumbnail
    implicitWidth: parent.width
    implicitHeight: parent.height
    horizontalScrollBarPolicy: Qt.ScrollBarAsNeeded
    anchors {
      left: title_sc_topbar_thumbnail.right
      right: sliceview_topbar_thumbnail_item.right
      top: sliceview_topbar_thumbnail_item.top
      bottom: sliceview_topbar_thumbnail_item.bottom
    }

    anchors {
      leftMargin: 5
      rightMargin: 5
      topMargin: 5
      bottomMargin: 2
    }

    // style
    style: ScrollViewStyle{
      handle: Rectangle {
        implicitWidth: 8
        implicitHeight: 8
        radius: 7
        color: "#474747"
      }
      scrollBarBackground: Rectangle {
        implicitWidth: 8
        implicitHeight: 8
        color: "transparent"
      }
      decrementControl: Rectangle {
        color: "transparent"
      }
      incrementControl: Rectangle {
        color: "transparent"
      }
      corner: Rectangle {
        color: "transparent"
      }
    }

    contentItem:
      RowLayout {
        id: layout_thumbnail
        objectName: "layout_thumbnail"

        Repeater {
          id: repeater_sv_thumbnail
          objectName: 'repeater_sv_thumbnail'
          model: 0

          ThumbnailItem{
            id: thumbnail_item
            objectName: "thumbnail_item"
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
          }
        }

        // dummy
        Item {
          id: dummy_thumbnail
          objectName: "dummy_thumbnail"
          Layout.fillWidth: true
        }

      }
  }

  function appendThumbnail(_id, _name, _study_uid, _series_uid, _series_id, _date, _modality)
  {
    items_sv_thumbnail.append({patient_id: _id, patient_name: _name, study_uid: _study_uid,
                               series_uid: _series_uid, series_id: _series_id,
                               date: _date, modality: _modality});

    // should call generateThumbnails()!
    generateThumbnails();
  }

  function removeThumbnail(_study_uid, _series_uid)
  {
    items_sv_thumbnail_dummy.clear();

    for (var i=0; i < items_sv_thumbnail.count; i++)
    {
      var _model = items_sv_thumbnail.get(i);

      if (_series_uid == null)
      {
        // for all series with study uid
        if (_model.study_uid != _study_uid)
        {
          items_sv_thumbnail_dummy.append(_model);
        }
      }
      else
      {
        // for series with specified _study_uid & _series_uid
        if (!((_model.study_uid == _study_uid) && (_model.series_uid == _series_uid)))
        {
          items_sv_thumbnail_dummy.append(_model);
        }
      }
    }
    items_sv_thumbnail.clear();

    // switch list model
    if (items_sv_thumbnail_dummy.count > 0)
    {
      for (var i=0; i < items_sv_thumbnail_dummy.count; i++)
      {
        var _model = items_sv_thumbnail_dummy.get(i);
        items_sv_thumbnail.append(_model);
      }

      items_sv_thumbnail_dummy.clear();
    }

    // should be called after remove model!
    generateThumbnails();
  }

  function clearThumbnail()
  {
    items_sv_thumbnail.clear();
    // should be called after remove model!
    generateThumbnails();
  }

  function generateThumbnails()
  {
    repeater_sv_thumbnail.model = items_sv_thumbnail.count;
    for (var i=0; i < repeater_sv_thumbnail.count; i++)
    {
      var _item = repeater_sv_thumbnail.itemAt(i)
      _item.setModel(items_sv_thumbnail.get(i));
    }
  }

  function isExist(_study_uid)
  {
    for (var i=0; i < items_sv_thumbnail.count; i++)
    {
      var _model = items_sv_thumbnail.get(i);
      if (_model.study_uid == _study_uid)
      {
        return true;
      }
    }
    return false;
  }

}
