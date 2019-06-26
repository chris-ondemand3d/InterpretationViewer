pragma Singleton  
import QtQuick 2.0  

// dept1 -> .qml file name(Property names cannot begin with an upper case letter)
// dept2 -> Item id
// dept3 -> _property name

// Sample!!!!
// property QtObject mainwindow: QtObject{
//   property QtObject bg: QtObject{
//     property color _color1: "red";
//   }
// }

// main - CyStyle
// sub - StyleMac, StyleWin, etc ...
//
// 만약 sub에 property를 추가 했다면,
// main과 다른 sub에도 추가한 property와 같은 이름으로 property를 만들어야 합니다.

Item{

  StyleMac{ id:style_mac }
  StyleWin{ id:style_win }

  function check_os(){
    if(Qt.platform.os === "osx"){
      return style_mac
    }else if(Qt.platform.os === "windows"){
      return style_win
    }else{
      // can be added.
    }
  }

  property var style_object: check_os()

  property QtObject mainwindow: QtObject{
    property int _module_menu_width: style_object.mainwindow._module_menu_width
    property int _module_menu_title_font_pointSize: style_object.mainwindow._module_menu_title_font_pointSize

    property string _tutorial_image: style_object.mainwindow._tutorial_image

    property color _normal_btn_bg_color : style_object.mainwindow._normal_btn_bg_color
    property color _hover_btn_bg_color : style_object.mainwindow._hover_btn_bg_color
    property color _active_btn_bg_color : style_object.mainwindow._active_btn_bg_color
  }

  property QtObject i2gwindow: QtObject{
    property int _i2g_title_font_pointSize: style_object.i2gwindow._i2g_title_font_pointSize
    property int _i2g_text_overlay_font_pointSize: style_object.i2gwindow._i2g_text_overlay_font_pointSize

    property string _i2g_mode_2_2_image: style_object.i2gwindow._i2g_mode_2_2_image
    property string _i2g_mode_2_3_image: style_object.i2gwindow._i2g_mode_2_3_image
  }

  property QtObject dbmwindow: QtObject{
    property int _db_title_font_pointSize: style_object.dbmwindow._db_title_font_pointSize

    property color db_connect_rect_bg_color: style_object.dbmwindow.db_connect_rect_bg_color
    property color db_connect_title_bg_color: style_object.dbmwindow.db_connect_title_bg_color
    property color data_infomation_bg_color: style_object.dbmwindow.data_infomation_bg_color
    property color treeview_bg_color: style_object.dbmwindow.treeview_bg_color
    property color treeview_select_bg_color: style_object.dbmwindow.treeview_select_bg_color

    property color common_font_color: style_object.dbmwindow.common_font_color
//    NOTE tooltip test
    property string btn_import_tooltip_text: style_object.dbmwindow.btn_import_tooltip_text

    property string _search_normal_image: style_object.dbmwindow._search_normal_image
    property string _treeview_PRJ_normal_image: style_object.dbmwindow._treeview_PRJ_normal_image
    property string _treeview_DICOM_normal_image: style_object.dbmwindow._treeview_DICOM_normal_image
    property string _treeview_STL_normal_image: style_object.dbmwindow._treeview_STL_normal_image
  }

  property QtObject dentaldummy: QtObject{
    property int _width : style_object.dentaldummy._width

    property color _main_bg_color: style_object.dentaldummy._main_bg_color
    property color _tools_main_bg_color: style_object.dentaldummy._tools_main_bg_color

    property string _tools_title_image: style_object.dentaldummy._tools_title_image
    property color _tools_title_bg_color: style_object.dentaldummy._tools_title_bg_color
    property color _tools_title_line_color: style_object.dentaldummy._tools_title_line_color
    property color _tools_title_label_color: style_object.dentaldummy._tools_title_label_color
    property int _tools_title_label_size: style_object.dentaldummy._tools_title_label_size
    property int _tools_title_label_height: style_object.dentaldummy._tools_title_label_height
    property int _tools_title_label_leftMargin: style_object.dentaldummy._tools_title_label_leftMargin

    property int _tools_icon_btn_width : style_object.dentaldummy._tools_icon_btn_width
    property int _tools_icon_btn_height : style_object.dentaldummy._tools_icon_btn_height
    property int _tools_icon_btn_radius : style_object.dentaldummy._tools_icon_btn_radius

    property int _tools_tasks_btn_height : style_object.dentaldummy._tools_tasks_btn_height

    property color _normal_btn_bg_color : style_object.dentaldummy._normal_btn_bg_color
    property color _hover_btn_bg_color : style_object.dentaldummy._hover_btn_bg_color
    property color _active_btn_bg_color : style_object.dentaldummy._active_btn_bg_color

    // View!!!!
    property string _pan_normal_image: style_object.dentaldummy._pan_normal_image
    property string _zoom_normal_image: style_object.dentaldummy._zoom_normal_image
    property string _vr_normal_image: style_object.dentaldummy._vr_normal_image
    property string _wwl_normal_image: style_object.dentaldummy._wwl_normal_image
    //      property string _text_overlay_normal_image: style_object.dentaldummy._text_overlay_normal_image
    property string _quickview_normal_image: style_object.dentaldummy._quickview_normal_image
    property int _quickview_title_font_pointSize: style_object.dentaldummy._quickview_title_font_pointSize

    // Measure!!!!
    property string _ruler_menu_normal_image: style_object.dentaldummy._ruler_menu_normal_image
    property string _ruler_normal_image: style_object.dentaldummy._ruler_normal_image
    property string _tapeline_normal_image: style_object.dentaldummy._tapeline_normal_image
    property string _curveline_normal_image: style_object.dentaldummy._curveline_normal_image
    property string _analysis_normal_image: style_object.dentaldummy._analysis_normal_image

    property string _angle_menu_normal_image: style_object.dentaldummy._angle_menu_normal_image
    property string _angle_normal_image: style_object.dentaldummy._angle_normal_image
    property string _point3_normal_image: style_object.dentaldummy._point3_normal_image
    property string _point4_normal_image: style_object.dentaldummy._point4_normal_image

    property string _area_menu_normal_image: style_object.dentaldummy._area_menu_normal_image
    property string _area_normal_image: style_object.dentaldummy._area_normal_image
    property string _linepen_normal_image: style_object.dentaldummy._linepen_normal_image
    property string _curvepen_normal_image: style_object.dentaldummy._curvepen_normal_image
    property string _smartpen_normal_image: style_object.dentaldummy._smartpen_normal_image

    property string _note_menu_normal_image: style_object.dentaldummy._note_menu_normal_image
    property string _note_normal_image: style_object.dentaldummy._note_normal_image
    property string _rectangle_normal_image: style_object.dentaldummy._rectangle_normal_image
    property string _circle_normal_image: style_object.dentaldummy._circle_normal_image
    property string _arrow_normal_image: style_object.dentaldummy._arrow_normal_image

    property string _profile_normal_image: style_object.dentaldummy._profile_normal_image
    property string _reset_normal_image: style_object.dentaldummy._reset_normal_image

    //Output!!!!
    property string _capture_normal_image: style_object.dentaldummy._capture_normal_image
    property string _export_normal_image: style_object.dentaldummy._export_normal_image
    property string _save_project_normal_image: style_object.dentaldummy._save_project_normal_image

    //Tasks!!!!
    property int _tools_tasks_label_size: style_object.dentaldummy._tools_tasks_label_size
    property color _tools_tasks_line_color: style_object.dentaldummy._tools_tasks_line_color
    property int _registration_dialog_title_font_pointSize: style_object.dentaldummy._registration_dialog_title_font_pointSize
    property int _registration_dialog_subtitle_font_pointSize: style_object.dentaldummy._registration_dialog_subtitle_font_pointSize
  }

  property QtObject i2g_top_menu_bar: QtObject{

    property color _main_bg_color: style_object.i2g_top_menu_bar._main_bg_color

    property int _icon_btn_width : style_object.i2g_top_menu_bar._icon_btn_width
    property int _icon_btn_height : style_object.i2g_top_menu_bar._icon_btn_height
    property int _icon_btn_radius : style_object.i2g_top_menu_bar._icon_btn_radius

    property color _normal_btn_bg_color : style_object.i2g_top_menu_bar._normal_btn_bg_color
    property color _hover_btn_bg_color : style_object.i2g_top_menu_bar._hover_btn_bg_color
    property color _active_btn_bg_color : style_object.i2g_top_menu_bar._active_btn_bg_color

    //NOTE section1

    //NOTE section2
    property string _ori_r_normal_image: style_object.i2g_top_menu_bar._ori_r_normal_image
    property string _ori_r45_normal_image: style_object.i2g_top_menu_bar._ori_r45_normal_image
    property string _ori_a_normal_image: style_object.i2g_top_menu_bar._ori_a_normal_image
    property string _ori_l45_normal_image: style_object.i2g_top_menu_bar._ori_l45_normal_image
    property string _ori_l_normal_image: style_object.i2g_top_menu_bar._ori_l_normal_image
    property string _ori_h_normal_image: style_object.i2g_top_menu_bar._ori_h_normal_image
    property string _ori_f_normal_image: style_object.i2g_top_menu_bar._ori_f_normal_image
    property string _ori_p_normal_image: style_object.i2g_top_menu_bar._ori_p_normal_image

    //NOTE section3
    property string _abutment_normal_image: style_object.i2g_top_menu_bar._abutment_normal_image
    property string _anchor_pin_normal_image: style_object.i2g_top_menu_bar._anchor_pin_normal_image
    property string _vol_normal_image: style_object.i2g_top_menu_bar._vol_normal_image
    property string _guide_stone_normal_image: style_object.i2g_top_menu_bar._guide_stone_normal_image
    property string _implant_normal_image: style_object.i2g_top_menu_bar._implant_normal_image
    property string _nerve_normal_image: style_object.i2g_top_menu_bar._nerve_normal_image
    property string _sleeve_normal_image: style_object.i2g_top_menu_bar._sleeve_normal_image
    property string _surgical_template_normal_image: style_object.i2g_top_menu_bar._surgical_template_normal_image
    property string _waxup_normal_image: style_object.i2g_top_menu_bar._waxup_normal_image
    property string _fixture_info_normal_image: style_object.i2g_top_menu_bar._fixture_info_normal_image
    property string _tooth_number_normal_image: style_object.i2g_top_menu_bar._tooth_number_normal_image

    //NOTE section4
    property string _pano_normal_image: style_object.i2g_top_menu_bar._pano_normal_image
    property string _axial_normal_image: style_object.i2g_top_menu_bar._axial_normal_image
    property string _cross_normal_image: style_object.i2g_top_menu_bar._cross_normal_image
    property string _parallel_normal_image: style_object.i2g_top_menu_bar._parallel_normal_image
    property string _outline_normal_image: style_object.i2g_top_menu_bar._outline_normal_image

    //NOTE section5
    property string _vol_clipping_normal_image: style_object.i2g_top_menu_bar._vol_clipping_normal_image

  }

  property QtObject leafimplantitem: QtObject{
    property int _title_font_pointSize: style_object.leafimplantitem._title_font_pointSize
    property int _subtitle_font_pointSize: style_object.leafimplantitem._subtitle_font_pointSize
    property int _title_text_width : style_object.leafimplantitem._title_text_width
    property int _title_text_height : style_object.leafimplantitem._title_text_height
  }

  property QtObject project_save_dialog: QtObject{
    property int _title_font_pointSize: style_object.project_save_dialog._title_font_pointSize
  }
}

