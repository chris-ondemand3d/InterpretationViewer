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
  id : related_study_treeview_item

  // Custom ItemDelegate
  DBMTreeViewItemDelegate2{
    id: my_treeview_itemdelegate
  }
  // Custom HeaderDelegate
  DBMTreeViewHeaderDelegate{
    id: my_treeview_headerdelegate
  }

  TreeView{
    id: related_study_treeview
    objectName: "related_study_treeview"
    width: parent.width
    height: parent.height
    anchors.centerIn: parent
    model: (typeof(related_study_treeview_model) === "undefined") ? null : related_study_treeview_model
    headerVisible: true
    sortIndicatorVisible: true
    frameVisible: false
    focus: true

    //horizontalScrollBarPolicy: Qt.ScrollBarAlwaysOn
    verticalScrollBarPolicy: Qt.ScrollBarAlwaysOn

    selectionMode: SelectionMode.ExtendedSelection

    selection: ItemSelectionModel{
      id: related_study_treeview_itemselectionmodel
      objectName: "related_study_treeview_itemselectionmodel"
      model: (typeof(related_study_treeview_model) === "undefined") ? null : related_study_treeview_model

      onCurrentIndexChanged: {
        if(related_study_treeview_itemselectionmodel.currentIndex.parent.row != -1){
          related_study_treeview.prev_parent_index = currentIndex.parent
          related_study_treeview.sig_changed_index(currentIndex, false)
        }else{
          related_study_treeview.sig_changed_index(currentIndex, true)
        }
      }

      onSelectionChanged: {
        var indices = []
        selection.forEach(function(rowIndex){
          indices.push(rowIndex);
        })
        related_study_treeview.sig_selection_changed(indices);
      }
    }

    property var prev_child_index
    property var prev_parent_index
    property bool trigger: false

    signal sig_menu_trigger(string type, var index)
    signal sig_header_clicked_for_sort(var sortIndicatorColumn, var sortIndicatorOrder)
    signal sig_childitem_dclick(var index)
    signal sig_changed_index(var index, bool trigger)
    signal sig_selection_changed(var indices)

    function set_prev_index(parent_index, child_index){
      var _p_index = parent_index
      var _c_index = child_index

      related_study_treeview.expand(_p_index)
      related_study_treeview_itemselectionmodel.setCurrentIndex(_c_index, ItemSelectionModel.ClearAndSelect)

      __currentRow = _p_index.row + 1

    }

    style: TreeViewStyle{
      //backgroundColor: CyStyle.dbmwindow.treeview_bg_color
      backgroundColor: "#262626"

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

    rowDelegate: Component{
      Rectangle {
        id : related_study_treeview_row_delegate
        width: related_study_treeview.width
        height: 40
        //color: styleData.selected ? CyStyle.dbmwindow.treeview_select_bg_color : "transparent"
        color: styleData.selected ? "#161616" : "transparent"
        Rectangle {
          width: related_study_treeview.width * 0.95
          height: 1
          color: '#2e2e2e'
        }
      }
    }

    // Custom ItemDelegate
    itemDelegate: my_treeview_itemdelegate
    // Custom HeaderDelegate
    headerDelegate: my_treeview_headerdelegate

    TableViewColumn{
      width : 170
      role: "AccessionNumber"
      title: "AccessionNumber"
      movable: false
      visible: true
    }
    TableViewColumn{
      width : 170
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
      related_study_treeview.sig_childitem_dclick(related_study_treeview_itemselectionmodel.selectedIndexes[0])
    }

  }
}
