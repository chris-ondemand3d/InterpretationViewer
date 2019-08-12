import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Dialogs 1.2
import QtGraphicalEffects 1.0
import QtQml 2.0
import QtQml.Models 2.2

import cyhub 1.0

import "../"
import "../style"


Item {
  id: dbm_win_root
  width: 1000
  height: 700

  Rectangle{
    id: bg
    anchors.fill: parent
    color: 'darkgray'
  }

  // Bottom Panel
  COMMON_bottombar {
    id: bottombar_panel
    objectName: "bottombar_panel"

    height: 20

    anchors.left: parent.left
    anchors.right: parent.right
    anchors.bottom: parent.bottom
  }

  SplitView {
    id: dbm_split_view
    anchors.left: parent.left
    anchors.top: parent.top
    anchors.right: parent.right
    anchors.bottom: bottombar_panel.top
    orientation: Qt.Vertical

    // Top
    Rectangle {
      color: CyStyle.dbmwindow.treeview_bg_color
      height: dbm_split_view.height * 4 / 10
      Layout.minimumHeight: 100
      Layout.maximumHeight: 1000

      RowLayout {

        width: parent.width
        height: parent.height
        spacing: 0
        anchors.centerIn: parent

        Rectangle{
          color: CyStyle.dbmwindow.data_infomation_bg_color
          width: 30
          Layout.fillHeight: parent.height

          Text {
            width: parent.width
            height: parent.height
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            text: 'S\nT\nU\nD\nI\nE\nS'
            color: CyStyle.dbmwindow.common_font_color
            font.bold: true
          }

        }

        DBMStudyTreeView {
          Layout.fillWidth: parent.width
          Layout.fillHeight: parent.height
        }
      }

    }

    // Middle
    Rectangle {
      color: CyStyle.dbmwindow.treeview_bg_color
      height: dbm_split_view.height * 2.5 / 10
      Layout.minimumHeight: 100
      Layout.maximumHeight: 700

      RowLayout {

        width: parent.width
        height: parent.height
        spacing: 0
        anchors.centerIn: parent

        Rectangle{
          color: CyStyle.dbmwindow.data_infomation_bg_color
          width: 30
          Layout.fillHeight: parent.height

          Text {
            width: parent.width
            height: parent.height
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            text: 'R\nE\nL\nA\nT\nE\nD\n'
            color: CyStyle.dbmwindow.common_font_color
            font.bold: true
          }
        }

        DBMRelatedStudyTreeView {
          Layout.fillWidth: parent.width
          Layout.fillHeight: parent.height
        }
      }

    }

    // Bottom
    Rectangle {
      color: CyStyle.dbmwindow.treeview_bg_color
      height: dbm_split_view.height * 3.5 / 10
      Layout.minimumHeight: 100
      Layout.maximumHeight: 700

      RowLayout {

        width: parent.width
        height: parent.height
        spacing: 0
        anchors.centerIn: parent

        Rectangle{
          color: CyStyle.dbmwindow.data_infomation_bg_color
          width: 30
          Layout.fillHeight: parent.height

          Text {
            width: parent.width
            height: parent.height
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            text: 'R\nE\nP\nO\nR\nT\nS\n'
            color: CyStyle.dbmwindow.common_font_color
            font.bold: true
          }
        }

        Rectangle {
          color: CyStyle.dbmwindow.treeview_bg_color
          Layout.fillWidth: parent.width
          Layout.fillHeight: parent.height
        }

      }

    }

  }

  Rectangle {
    id: dbm_message_box
    objectName: "dbm_message_box"
    anchors {
        right: parent.right
        bottom: bottombar_panel.top
        margins: 15
    }
    color: '#484848'
    width: 360
    height: 120
    radius: 0
    visible: false

    signal sigMsg(string title, string text)

    Timer {
        id: timer_dbm_message_box
        interval: 10000 // triggers every 5000 ms
        onTriggered: dbm_message_box.clear()
        running: false
    }

    Rectangle {
        id: icon_dbm_message

        anchors {
            right: layout_dbm_messagebox.left
            rightMargin: 15
            top: layout_dbm_messagebox.top
            topMargin: (txt_dbm_message1.height - height) / 2
        }
        width: 20
        height: 20
        //color: "skyblue"
        color: '#FF4343'
        radius: 100
    }

    ColumnLayout {

        id: layout_dbm_messagebox
        spacing: 10
        anchors.centerIn: parent

        Text
        {
          id: txt_dbm_message1
          text: ""
          color: "white"
          horizontalAlignment: Text.AlignLeft
          verticalAlignment: Text.AlignVCenter
          font.pointSize: CyStyle.dbmwindow._db_title_font_pointSize
          font.bold: true
          font.weight: Font.ExtraBold
          clip: true
          Layout.maximumWidth: dbm_message_box.width * 0.7
        }

        Text
        {
          id: txt_dbm_message2
          text: ""
          color: "white"
          horizontalAlignment: Text.AlignLeft
          verticalAlignment: Text.AlignVCenter
          font.pointSize: CyStyle.dbmwindow._db_title_font_pointSize - 3
          clip: true
          Layout.maximumWidth: dbm_message_box.width * 0.7
        }
    }

    onSigMsg: {
        setMsg(title, text);
    }

    function setMsg(title, text)
    {
        txt_dbm_message1.text = title;
        txt_dbm_message2.text = text;
        dbm_message_box.visible = true;
        timer_dbm_message_box.restart();
    }

    function clear()
    {
        txt_dbm_message1.text = "";
        txt_dbm_message2.text = "";
        dbm_message_box.visible = false;
    }

  }

}