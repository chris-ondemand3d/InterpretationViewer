import QtQuick 2.0
import QtQuick.Controls 1.4
import QtQml.Models 2.2
import "../style"

Component {
  Rectangle{
    //color: CyStyle.dbmwindow.treeview_header_bg_color
    color: CyStyle.dbmwindow.treeview_bg_color
    width: parent.width
    height: 40

    Text {
      width: parent.width
      height: parent.height
      horizontalAlignment: Text.AlignHCenter
      verticalAlignment: Text.AlignVCenter
      text: String(styleData.value) === "undefined" ? "": styleData.value
      color: CyStyle.dbmwindow.common_font_color
      font.bold: true
    }

    Connections {
      id: header_click_connections
      target: styleData
      property var prev_column: -1
      property bool trigger: true
      onPressedChanged: {
//        if(prev_column !== styleData.column){
//          project_list_treeview.sig_header_clicked_for_sort(prev_column, Qt.AscendingOrder)
//          prev_column = styleData.column
//          console.log(prev_column)
//          console.log(styleData.column)
//        }else{
//          project_list_treeview.sig_header_clicked_for_sort(prev_column, Qt.DescendingOrder)
//          console.log(prev_column)
//          console.log(styleData.column)
//        }
        if(styleData.pressed){

        }else{
          if(prev_column === styleData.column){
            if(header_click_connections.trigger === true){
              study_treeview.sig_header_clicked_for_sort(styleData.column, Qt.AscendingOrder)
              header_click_connections.trigger = false
            }else{
              study_treeview.sig_header_clicked_for_sort(styleData.column, Qt.DescendingOrder)
              header_click_connections.trigger = true
            }
          }else{
            study_treeview.sig_header_clicked_for_sort(styleData.column, Qt.DescendingOrder)
            prev_column = styleData.column
          }
        }
      }
    }
  }
}
