import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Dialogs 1.2
import QtGraphicalEffects 1.0
import QtQml 2.0
import QtQml.Models 2.2

import "../"
import "../style"


Item {
  id : study_treeview_item

  // Custom ItemDelegate
  DBMTreeViewItemDelegate{
    id: my_treeview_itemdelegate
  }
  // Custom HeaderDelegate
  DBMTreeViewHeaderDelegate{
    id: my_treeview_headerdelegate
  }

  TreeView{
    id: study_treeview
    objectName: "study_treeview"
    width: parent.width
    height: parent.height
    anchors.centerIn: parent
    model: (typeof(study_treeview_model) === "undefined") ? null : study_treeview_model
    headerVisible: true
    sortIndicatorVisible: true
    frameVisible: false
    focus: true

    //horizontalScrollBarPolicy: Qt.ScrollBarAlwaysOn
    //verticalScrollBarPolicy: Qt.ScrollBarAlwaysOn

    selectionMode: SelectionMode.ExtendedSelection

    selection: ItemSelectionModel{
      id: study_treeview_itemselectionmodel
      objectName: "study_treeview_itemselectionmodel"
      model: (typeof(study_treeview_model) === "undefined") ? null : study_treeview_model

      onCurrentIndexChanged: {
        if(study_treeview_itemselectionmodel.currentIndex.parent.row != -1){
          study_treeview.prev_parent_index = currentIndex.parent
          study_treeview.sig_changed_index(currentIndex, false)
        }else{
          study_treeview.sig_changed_index(currentIndex, true)
        }
      }
    }

    property var prev_child_index
    property var prev_parent_index
    property bool trigger: false

    signal sig_menu_trigger(string type, var index)
    signal sig_header_clicked_for_sort(var sortIndicatorColumn, var sortIndicatorOrder)
    signal sig_childitem_dclick(var index, var index_info)
    signal sig_changed_index(var index, bool trigger)

    function set_prev_index(parent_index, child_index){
      var _p_index = parent_index
      var _c_index = child_index

      study_treeview.expand(_p_index)
      study_treeview_itemselectionmodel.setCurrentIndex(_c_index, ItemSelectionModel.ClearAndSelect)

      __currentRow = _p_index.row + 1

    }

    style: TreeViewStyle{
      backgroundColor: CyStyle.dbmwindow.treeview_bg_color

      handle: Rectangle {
        implicitWidth: 13
        implicitHeight: 13
        radius: 7
        color: "#474747"
      }
      scrollBarBackground: Rectangle {
        implicitWidth: 13
        implicitHeight: 13
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

    rowDelegate: Component{
      Rectangle {
        id : study_treeview_row_delegate
        height: 40
        color: styleData.selected ? CyStyle.dbmwindow.treeview_select_bg_color : "transparent"
      }
    }

    // Custom ItemDelegate
    itemDelegate: my_treeview_itemdelegate
    // Custom HeaderDelegate
    headerDelegate: my_treeview_headerdelegate

    TableViewColumn{
      width : 180
      role: "PatientID"
      title: "PatientID"
      movable: false
      visible: true
    }
    TableViewColumn{
      width : 150
      role: "PatientName"
      title: "PatientName"
      movable: false
      visible: true
    }
    TableViewColumn{
      width : 50
      role: "PatientSex"
      title: "Sex"
      movable: false
      visible: true
    }
    TableViewColumn{
      width : 50
      role: "PatientAge"
      title: "Age"
      movable: false
      visible: true
    }
    TableViewColumn{
      width : 130
      role: "DateTime"
      title: "DateTime"
      movable: false
      visible: true
    }
    TableViewColumn{
      width : 60
      role: "Imgs"
      title: "Imgs"
      movable: false
      visible: true
    }
    TableViewColumn{
      width : 80
      role: "Modality"
      title: "Modality"
      movable: false
      visible: true
    }
    TableViewColumn{
      width : 100
      role: "BodyPartExamined"
      title: "BodyPart"
      movable: false
      visible: true
    }
    TableViewColumn{
      width : 400
      role: "Description"
      title: "Description"
      movable: false
      visible: true
    }
    TableViewColumn{
      width : 300
      role: "Comment"
      title: "Comment"
      movable: false
      visible: false
    }
    TableViewColumn{
      width : 1
      role: "Key"
      title: "Key"
      movable: false
      visible: false
    }

    onDoubleClicked: {
      if(isExpanded(study_treeview_itemselectionmodel.currentIndex) === true){
        collapse(study_treeview_itemselectionmodel.currentIndex)
        if(study_treeview_itemselectionmodel.currentIndex.parent.row != -1){
          if(study_treeview_itemselectionmodel.selectedIndexes.length === 1){
            study_treeview.sig_childitem_dclick(study_treeview_itemselectionmodel.selectedIndexes[0], study_treeview_itemselectionmodel.currentIndex)
          }
        }
      }else{
        expand(study_treeview_itemselectionmodel.currentIndex)
        if(study_treeview_itemselectionmodel.currentIndex.parent.row != -1){
          if(study_treeview_itemselectionmodel.selectedIndexes.length === 1){

            study_treeview.prev_child_index = study_treeview_itemselectionmodel.currentIndex

            var prev_index_info = [study_treeview.prev_parent_index, study_treeview.prev_child_index]

            study_treeview.sig_childitem_dclick(study_treeview_itemselectionmodel.selectedIndexes[0], prev_index_info)
          }
        }
      }
    }
  }

}