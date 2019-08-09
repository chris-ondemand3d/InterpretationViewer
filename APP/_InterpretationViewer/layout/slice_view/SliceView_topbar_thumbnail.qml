import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0
import cyhub 1.0


Item {
  id: sliceview_topbar_thumbnail_item
  objectName: "sliceview_topbar_thumbnail_item"

  width: 800
  height: 30

  signal sigDrop(real picked_layout_id, string study_uid, string series_uid)
  signal sigHighlight(string study_uid, string series_uid, bool on)
  signal sigClose(string study_uid, string series_uid)

  ListModel {
    id: items_sv_thumbnail
  }

  Rectangle{
    anchors.fill: parent
    color: '#303030'
  }

  RowLayout {
    id: layout_thumbnail
    anchors.fill: parent
    anchors.margins: 5
    width: parent.width
    height: parent.height
    Layout.preferredWidth: width
    Layout.preferredHeight: height
    Layout.maximumHeight: height
    Layout.maximumWidth: width
    Layout.minimumHeight: height
    Layout.minimumWidth: width

    Repeater {
      id: repeater_sv_thumbnail
      objectName: 'repeater_sv_thumbnail'
      model: 0

      ThumbnailItem{
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
    for (var i=0; i < items_sv_thumbnail.count; i++)
    {
      var _model = items_sv_thumbnail.get(i);

      if ((_model.study_uid == _study_uid) && (_model.series_uid == _series_uid))
      {
        // remove model(ListModel)
        items_sv_thumbnail.remove(i);

        // should be called after remove model!
        generateThumbnails();

        break;
      }
    }
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

}