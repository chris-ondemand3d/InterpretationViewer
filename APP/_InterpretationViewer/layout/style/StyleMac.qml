import QtQuick 2.0

QtObject{
  property QtObject mainwindow: QtObject{
    property int _module_menu_width: 60
    property int _module_menu_title_font_pointSize: 12

    property string _tutorial_image: "../resources/icon/misc/tutorial@3x.png"

    property color _normal_btn_bg_color : "#212222"
    property color _hover_btn_bg_color : "#404042"
    property color _active_btn_bg_color : "#000000"
  }

  property QtObject i2gwindow: QtObject{
    property int _i2g_title_font_pointSize: 12
    property int _i2g_text_overlay_font_pointSize: 12

    property string _i2g_mode_2_2_image: "../../resources/icon/misc/layout_2_2.png"
    property string _i2g_mode_2_3_image: "../../resources/icon/misc/layout_2_3.png"
  }

  property QtObject dbmwindow: QtObject{
    property int _db_title_font_pointSize: 16

    property color db_connect_rect_bg_color: "#232523"
    property color db_connect_title_bg_color: "#282A27"
    property color data_infomation_bg_color: "#1b1d1b"
    property color treeview_bg_color: "#232523"
    property color treeview_select_bg_color: "#1B1D1B"

    property color common_font_color: "#656565"
//    NOTE tooltip test
    property string btn_import_tooltip_text: qsTr("button for import *.dcm file")

    property string _search_normal_image: "../../resources/icon/misc/search.png"
    property string _treeview_PRJ_normal_image: "../../resources/icon/misc/dbm_treeview_PRJ.png"
    property string _treeview_DICOM_normal_image: "../../resources/icon/misc/dbm_treeview_DICOM.png"
    property string _treeview_STL_normal_image: "../../resources/icon/misc/dbm_treeview_STL.png"
  }

  property QtObject dentaldummy: QtObject{
    property int _width : 130

    property color _main_bg_color: "#2e2e2e"
    property color _tools_main_bg_color: "#2e2e2e"

    property string _tools_title_image: "../../resources/icon/misc/grouphead_icon.png"
    property color _tools_title_bg_color: "#2e2e2e"
    property color _tools_title_line_color: "#6b6b6b"
    property color _tools_title_label_color: "#6b6b6b"
    property int _tools_title_label_size: 12
    property int _tools_title_label_height: 30
    property int _tools_title_label_leftMargin: 15

    property int _tools_icon_btn_width : 32
    property int _tools_icon_btn_height : 32
    property int _tools_icon_btn_radius : 4

    property int _tools_tasks_btn_height : 30

    property color _normal_btn_bg_color : "#2e2e2e"
    property color _hover_btn_bg_color : "#404042"
    property color _active_btn_bg_color : "#212222"

    // View!!!!
    property string _pan_normal_image: "../../resources/icon/view/pan.png"
    property string _zoom_normal_image: "../../resources/icon/view/zoom.png"
    property string _vr_normal_image: "../../resources/icon/view/vr.png"
    property string _wwl_normal_image: "../../resources/icon/view/wwl.png"
    //      property string _text_overlay_normal_image: "../../resources/icon/view/text_overlay.png"
    property string _quickview_normal_image: "../../resources/icon/view/quickview.png"
    property int _quickview_title_font_pointSize: 12

    // Measure!!!!
    property string _ruler_menu_normal_image: "../../resources/icon/measure/ruler_menu.png"
    property string _ruler_normal_image: "../../resources/icon/measure/ruler.png"
    property string _tapeline_normal_image: "../../resources/icon/measure/tapeline.png"
    property string _curveline_normal_image: "../../resources/icon/measure/curveline.png"
    property string _analysis_normal_image: "../../resources/icon/measure/analysis.png"

    property string _angle_menu_normal_image: "../../resources/icon/measure/angle_menu.png"
    property string _angle_normal_image: "../../resources/icon/measure/angle.png"
    property string _point3_normal_image: "../../resources/icon/measure/point3.png"
    property string _point4_normal_image: "../../resources/icon/measure/point4.png"

    property string _area_menu_normal_image: "../../resources/icon/measure/area_menu.png"
    property string _area_normal_image: "../../resources/icon/measure/area.png"
    property string _linepen_normal_image: "../../resources/icon/measure/linepen.png"
    property string _curvepen_normal_image: "../../resources/icon/measure/curvepen.png"
    property string _smartpen_normal_image: "../../resources/icon/measure/smartpen.png"

    property string _note_menu_normal_image: "../../resources/icon/measure/note_menu.png"
    property string _note_normal_image: "../../resources/icon/measure/note.png"
    property string _rectangle_normal_image: "../../resources/icon/measure/rectangle.png"
    property string _circle_normal_image: "../../resources/icon/measure/circle.png"
    property string _arrow_normal_image: "../../resources/icon/measure/arrow.png"

    property string _profile_normal_image: "../../resources/icon/measure/profile.png"
    property string _reset_normal_image: "../../resources/icon/measure/reset.png"

    //Output!!!!
    property string _capture_normal_image: "../../resources/icon/output/capture.png"
    property string _export_normal_image: "../../resources/icon/output/export.png"
    property string _save_project_normal_image: "../../resources/icon/output/save_project.png"

    //Tasks!!!!
    property int _tools_tasks_label_size: 11
    property color _tools_tasks_line_color: "#282828"
    property int _registration_dialog_title_font_pointSize: 15
    property int _registration_dialog_subtitle_font_pointSize: 12
  }

  property QtObject i2g_top_menu_bar: QtObject{

    property color _main_bg_color: "#2e2e2e"

    property int _icon_btn_width : 32
    property int _icon_btn_height : 32
    property int _icon_btn_radius : 4

    property color _normal_btn_bg_color : "#2e2e2e"
    property color _hover_btn_bg_color : "#404042"
    property color _active_btn_bg_color : "#212222"

    //NOTE section1

    //NOTE section2
    property string _ori_r_normal_image: "../../resources/icon/horizontal_toolbar/section2/ori_r.png"
    property string _ori_r45_normal_image: "../../resources/icon/horizontal_toolbar/section2/ori_r45.png"
    property string _ori_a_normal_image: "../../resources/icon/horizontal_toolbar/section2/ori_a.png"
    property string _ori_l45_normal_image: "../../resources/icon/horizontal_toolbar/section2/ori_l45.png"
    property string _ori_l_normal_image: "../../resources/icon/horizontal_toolbar/section2/ori_l.png"
    property string _ori_h_normal_image: "../../resources/icon/horizontal_toolbar/section2/ori_h.png"
    property string _ori_f_normal_image: "../../resources/icon/horizontal_toolbar/section2/ori_f.png"
    property string _ori_p_normal_image: "../../resources/icon/horizontal_toolbar/section2/ori_p.png"

    //NOTE section3
    property string _abutment_normal_image: "../../resources/icon/horizontal_toolbar/section3/abutment.png"
    property string _anchor_pin_normal_image: "../../resources/icon/horizontal_toolbar/section3/anchor_pin.png"
    property string _vol_normal_image: "../../resources/icon/horizontal_toolbar/section3/volume.png"
    property string _guide_stone_normal_image: "../../resources/icon/horizontal_toolbar/section3/guide_stone.png"
    property string _implant_normal_image: "../../resources/icon/horizontal_toolbar/section3/implant.png"
    property string _nerve_normal_image: "../../resources/icon/horizontal_toolbar/section3/nerve.png"
    property string _sleeve_normal_image: "../../resources/icon/horizontal_toolbar/section3/sleeve.png"
    property string _surgical_template_normal_image: "../../resources/icon/horizontal_toolbar/section3/surgical_template.png"
    property string _waxup_normal_image: "../../resources/icon/horizontal_toolbar/section3/waxup.png"
    property string _fixture_info_normal_image: "../../resources/icon/horizontal_toolbar/section3/fixture_info.png"
    property string _tooth_number_normal_image: "../../resources/icon/horizontal_toolbar/section3/tooth_number.png"

    //NOTE section4
    property string _pano_normal_image: "../../resources/icon/horizontal_toolbar/section4/pano.png"
    property string _axial_normal_image: "../../resources/icon/horizontal_toolbar/section4/axial.png"
    property string _cross_normal_image: "../../resources/icon/horizontal_toolbar/section4/cross.png"
    property string _parallel_normal_image: "../../resources/icon/horizontal_toolbar/section4/parallel.png"
    property string _outline_normal_image: "../../resources/icon/horizontal_toolbar/section4/outline.png"

    //NOTE section5
    property string _vol_clipping_normal_image: "../../resources/icon/horizontal_toolbar/section5/clipping.png"

  }

  property QtObject leafimplantitem: QtObject{
    property int _title_font_pointSize: 14
    property int _subtitle_font_pointSize: 12
    property int _title_text_width : 80
    property int _title_text_height : 20
  }

  property QtObject project_save_dialog: QtObject{
    property int _title_font_pointSize: 15
  }
}

