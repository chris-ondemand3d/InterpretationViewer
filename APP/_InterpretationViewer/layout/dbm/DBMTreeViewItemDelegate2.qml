import QtQuick 2.0
import QtQuick.Controls 1.4
import QtQml.Models 2.2
import QtQml 2.2
import "../style"

Component {
  Rectangle{
    id:baseRec
    color: "transparent"

    Text {
      id: data
      width: parent.width
      height: parent.height
      horizontalAlignment: Text.AlignHCenter
      verticalAlignment: Text.AlignVCenter
      elide: Text.ElideRight
      text: String(styleData.value) === "undefined" ? "": styleData.value
      color: styleData.selected ? "white" : CyStyle.dbmwindow.common_font_color
    }

    MouseArea {
      anchors.fill: parent
      acceptedButtons: Qt.RightButton
      onClicked: {
        if (mouse.button == Qt.RightButton && related_study_treeview_itemselectionmodel.hasSelection){
          if (related_study_treeview_itemselectionmodel.selectedIndexes.length === 1){
            related_study_treeview_itemselectionmodel.setCurrentIndex(styleData.index, ItemSelectionModel.ClearAndSelect)
          }
          contextMenu.popup()
        }
      }
    }

    ListModel {
      id: menuModel

      ListElement {
        menuType: "view(1)"
      }
      ListElement {
        menuType: "view(2)"
      }
      ListElement {
        menuType: "..."
      }
      ListElement {
        menuType: "..."
      }
    }

    Menu {
      id: contextMenu

      Instantiator {
        model: menuModel
        MenuItem {
          property var indexes: []
          text: model.menuType
          onTriggered:{
            if(related_study_treeview_itemselectionmodel.selectedIndexes.length > 1){
              for(var i = 0; i < related_study_treeview_itemselectionmodel.selectedIndexes.length; i++){
                indexes.push(related_study_treeview_itemselectionmodel.selectedIndexes[i])
              }
              related_study_treeview.sig_menu_trigger(text, indexes)
              //project_list_treeview_itemselectionmodel.clearSelection()
              //project_list_treeview.__currentRow = -1

              indexes = []
            }else{
              indexes.push(related_study_treeview_itemselectionmodel.selectedIndexes[0])
              related_study_treeview.sig_menu_trigger(text, indexes)

              //project_list_treeview_itemselectionmodel.clearSelection()
              //project_list_treeview.__currentRow = -1

              indexes = []
            }
          }
        }
        onObjectAdded: contextMenu.insertItem(index, object)
        onObjectRemoved: contextMenu.removeItem(object)
      }

      MenuSeparator {
        visible: menuModel.count > 0
      }

      MenuItem {
        text: "Clear menu"
        enabled: menuModel.count > 0
        onTriggered: recentFilesModel.clear()
      }
    }
  }
}
