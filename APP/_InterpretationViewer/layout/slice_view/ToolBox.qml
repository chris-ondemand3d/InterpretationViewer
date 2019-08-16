import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtGraphicalEffects 1.0
import cyhub 1.0

import "../style"


Item {
  id: toolbox_menu_item
  objectName: "toolbox_menu_item"

  width: parent.width
  height: layout_toolbox.height

  signal sigSelect(string btnName, bool bSelected)
  signal sigSelected(string btnName, bool bSelected)
  signal sigToggleOn()

  property var title: null
  property var itemModel: null

  Rectangle{
    anchors.fill: parent
    //color: '#252528'
    color: 'transparent'
  }

  ColumnLayout {
    id: layout_toolbox
    anchors.fill: parent
    spacing: 5
    height: title_toolbox.height + grid_toolbox.height + ((layout_toolbox.children.length-1) * spacing)

    Rectangle {
      id: title_toolbox
      width: parent.width
      height: 20
      Layout.preferredWidth: parent.width
      Layout.preferredHeight: height
      color: CyStyle.dbmwindow.data_infomation_bg_color

      Text {
        width: parent.width
        height: parent.height
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        text: title
        color: 'lightgray'
        font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize - 2
      }
    }

    GridLayout {
      id: grid_toolbox
      Layout.alignment: Qt.AlignCenter | Qt.AlignTop
      Layout.fillWidth: true
      //Layout.fillHeight: true
      Layout.preferredHeight: (30+columnSpacing) * rows

      rows    : 4
      columns : 2

      rowSpacing: 2
      columnSpacing: 2

      property var default_color: "slategray"
      property var selected_color: "lightgray"
      property var pressed_color: "dimgray"

      Repeater {
        id: repeater_toolbox
        objectName: 'repeater_toolbox'
        model: itemModel.count

        Rectangle {
          id: btn_toolbox
          color: 'black'
          width: 30
          height: 30

          signal sigSelected(string btnName, bool bSelected)

          Rectangle {
            id: inner_rect_toolbox
            anchors.fill: parent
            anchors.margins: 1
            color: (isSelected() === true) ? grid_toolbox.selected_color : grid_toolbox.default_color

            // debug
            Text {
              anchors.fill: inner_rect_toolbox
              text: itemModel.get(index).name
              clip: true
              wrapMode: Text.WrapAnywhere
              verticalAlignment: Text.AlignVCenter
              horizontalAlignment: Text.AlignHCenter
              font.pointSize: CyStyle.i2gwindow._i2g_title_font_pointSize - 3
            }
          }

          MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.LeftButton
            onClicked: {
              var _model = itemModel.get(index);
              if (_model.toggle)
              {
                _model.selected = !_model.selected;

                if (_model.selected)
                  toolbox_menu_item.sigToggleOn();

                btn_toolbox.sigSelected(_model.name, _model.selected);
              }
              else
              {
                _model.selected = false;
                btn_toolbox.sigSelected(_model.name, true);
              }
            }

            onPressed: {
              inner_rect_toolbox.color = grid_toolbox.pressed_color
            }
            onReleased: {
              inner_rect_toolbox.color = (isSelected() === true) ? grid_toolbox.selected_color : grid_toolbox.default_color
            }
          }

          onSigSelected: {
            btn_toolbox.syncWithModel();
            toolbox_menu_item.sigSelected(btnName, bSelected);
          }

          function isSelected()
          {
            return itemModel.get(index).selected;
          }

          function syncWithModel()
          {
            if (itemModel.get(index).toggle == true)
            {
              for (var i=0; i<itemModel.count; i++)
              {
                var _model = itemModel.get(i);
                if (i != index)
                {
                  if (_model.selected)
                    toolbox_menu_item.sigSelected(_model.name, false);
                  _model.selected = false;
                }
                var _item = repeater_toolbox.itemAt(i);
                _item.children[0].color = _model.selected ? grid_toolbox.selected_color : grid_toolbox.default_color
              }
            }
          }
        }
      }
    }
  }

  // before
  onSigSelect: {
  }

  // after
  onSigSelected: {
  }

  function releaseAll()
  {
    for (var i=0; i<itemModel.count; i++)
    {
      var _model = itemModel.get(i);
      if (_model.selected)
        toolbox_menu_item.sigSelected(_model.name, false);
      _model.selected = false;
      var _item = repeater_toolbox.itemAt(i);
      _item.children[0].color = _model.selected ? grid_toolbox.selected_color : grid_toolbox.default_color
    }
  }

  function retrySelect()
  {
    for (var i=0; i<itemModel.count; i++)
    {
      var _model = itemModel.get(i);
      if (_model.selected)
      {
        toolbox_menu_item.sigSelected(_model.name, _model.selected);
      }
    }
  }

}