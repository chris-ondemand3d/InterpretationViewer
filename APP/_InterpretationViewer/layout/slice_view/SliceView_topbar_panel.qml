import QtQuick 2.10
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0
import cyhub 1.0

import "../style"


Item {
  id: sliceview_topbar_panel_item
  objectName: "sliceview_topbar_panel_item"

  width: 800
  height: 30

  signal sigSelected(int selected_index)
  signal sigClose(string study_uid)

  ListModel {
    id: items_sv_study
    objectName: "items_sv_study"
  }

  Rectangle{
    anchors.fill: parent
    color: '#404040'
    //color: '#252528'
  }

  Rectangle {
    id: title_sc_topbar_panel
    color: CyStyle.dbmwindow.data_infomation_bg_color
    anchors.left: parent.left
    anchors.top: parent.top

    width: 30
    height: parent.height

    Text {
      anchors.fill: parent
      text: 'S\nT'
      horizontalAlignment: Text.AlignHCenter
      verticalAlignment: Text.AlignVCenter
      color: CyStyle.dbmwindow.common_font_color
      font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize
      font.bold: true
    }
  }

  // Contents

  ScrollView {
    id: scroll_sv_study
    implicitWidth: parent.width
    implicitHeight: parent.height
    horizontalScrollBarPolicy: Qt.ScrollBarAsNeeded
    anchors {
      left: title_sc_topbar_panel.right
      right: sliceview_topbar_panel_item.right
      top: sliceview_topbar_panel_item.top
      bottom: sliceview_topbar_panel_item.bottom
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
        id: layout_study
        objectName: "layout_study"
        spacing: 1

        Repeater {
          id: repeater_sv_study
          objectName: 'repeater_sv_study'
          model: 0

          StudyItem{
            id: study_item
            objectName: "study_item"
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
          }
        }

        // dummy
        Item {
          id: dummy_study
          objectName: "dummy_study"
          Layout.fillWidth: true
        }

      }
  }

  // slots
  onSigSelected: {
    repeater_sv_study.model = items_sv_study.count;
    for (var i=0; i < repeater_sv_study.count; i++)
    {
      var _item = repeater_sv_study.itemAt(i)
      if (i != selected_index)
        _item.select(false);
    }
  }

  // functions

  function appendStudy(_id, _name, _study_uid, _date)
  {

    // check exist
    for (var i=0; i < items_sv_study.count; i++)
    {
      var _model = items_sv_study.get(i);

      // if exist
      if (_model.study_uid == _study_uid)
      {
        return;
      }
    }

    items_sv_study.append({patient_id: _id, patient_name: _name, study_uid: _study_uid, date: _date});

    // should call generateStudies()!
    generateStudies();
  }

  function removeStudy(_study_uid)
  {
    for (var i=0; i < items_sv_study.count; i++)
    {
      var _model = items_sv_study.get(i);

      if (_model.study_uid == _study_uid)
      {
        // remove model(ListModel)
        items_sv_study.remove(i);

        // should be called after remove model!
        generateStudies();

        break;
      }
    }
  }

  function generateStudies()
  {
    repeater_sv_study.model = items_sv_study.count;
    for (var i=0; i < repeater_sv_study.count; i++)
    {
      var _item = repeater_sv_study.itemAt(i)
      _item.setModel(items_sv_study.get(i));
    }
  }

}