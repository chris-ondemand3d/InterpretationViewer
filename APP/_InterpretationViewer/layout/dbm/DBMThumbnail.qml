import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0
import cyhub 1.0

import "../style"


Item {
  id: dbm_thumbnail_item
  objectName: "dbm_thumbnail_item"

  width: 250
  height: 300

  /*
  signal sigDrop(real picked_layout_id, string study_uid, string series_uid)
  signal sigHighlight(string study_uid, string series_uid, bool on)
  signal sigReleaseDummyThumbnail()
  signal sigClose(string study_uid, string series_uid)

  signal sigPositionChanged_Global(var global_mosue, var img_url, var mode)
  signal sigDropToOtherApp(var global_mouse, string study_uid, string series_uid)
  */

  ListModel {
    id: items_dbm_thumbnail
    objectName: "items_dbm_thumbnail"
  }

  // for model copy
  ListModel {
    id: items_dbm_thumbnail_dummy
  }

  // bg
  Rectangle{
    anchors.fill: parent
    //color: CyStyle.dbmwindow.treeview_bg_color
    color: "#262626"
  }

  // title
  Rectangle {
    id: title_dbm_thumbnail
    //color: CyStyle.dbmwindow.treeview_bg_color
    color: "#262626"
    anchors.left: parent.left
    anchors.top: parent.top
    anchors.right: parent.right

    width: parent.width
    height: 40

    Text {
      anchors.fill: parent
      text: 'Thumbnail'
      horizontalAlignment: Text.AlignHCenter
      verticalAlignment: Text.AlignVCenter
      color: CyStyle.dbmwindow.common_font_color
      font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize
      font.bold: true
    }
  }

  // contents
  ScrollView {
    id: scroll_dbm_thumbnail
    implicitWidth: parent.width
    implicitHeight: parent.height
    horizontalScrollBarPolicy: Qt.ScrollBarAlwaysOff
    verticalScrollBarPolicy: Qt.ScrollBarAlwaysOn
    anchors {
      left: parent.left
      right: parent.right
      top: title_dbm_thumbnail.bottom
      bottom: parent.bottom
    }
    anchors.margins: 0

    // style
    style: ScrollViewStyle{
      handle: Rectangle {
        implicitWidth: 10
        implicitHeight: 10
        radius: 7
        color: "#474747"
      }
      scrollBarBackground: Rectangle {
        implicitWidth: 9
        implicitHeight: 9
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
      ColumnLayout {
        id: layout_dbm_thumbnail
        objectName: "layout_dbm_thumbnail"
        width: dbm_thumbnail_item.width - 20
        spacing: 20

        Repeater {
          id: repeater_dbm_thumbnail
          objectName: 'repeater_dbm_thumbnail'
          model: 0

          ThumbnailItem {
            id: dbm_thumbnail_item
            objectName: "dbm_thumbnail_item"
            Layout.alignment: Qt.AlignHCenter | Qt.AlignTop
          }
        }

        // dummy
        Item {
          id: dbm_dummy_thumbnail
          objectName: "dbm_dummy_thumbnail"
          Layout.fillHeight: true
        }

      }
  }


  // function
  function appendThumbnail(_id, _name, _study_uid, _series_uid, _series_id, _date, _modality, _num)
  {
    // check exist
    for (var i=0; i<items_dbm_thumbnail.count; i++)
    {
      var _item = items_dbm_thumbnail.get(i);
      if ((_item.study_uid == _study_uid) && (_item.series_uid == _series_uid))
        return false;
    }

    items_dbm_thumbnail.append({patient_id: _id, patient_name: _name, study_uid: _study_uid,
                               series_uid: _series_uid, series_id: _series_id,
                               date: _date, modality: _modality, num: _num});

    // should call generateThumbnails()!
    generateThumbnails();

    return true;
  }

  function clearThumbnail()
  {
    items_dbm_thumbnail.clear();
    // should be called after remove model!
    generateThumbnails();
  }

  function generateThumbnails()
  {
    repeater_dbm_thumbnail.model = items_dbm_thumbnail.count;
    for (var i=0; i < repeater_dbm_thumbnail.count; i++)
    {
      var _item = repeater_dbm_thumbnail.itemAt(i)
      _item.setModel(items_dbm_thumbnail.get(i));
    }
  }

  function getRepeaterItem()
  {
    return repeater_dbm_thumbnail;
  }

}