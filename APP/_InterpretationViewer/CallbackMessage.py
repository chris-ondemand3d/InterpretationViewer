import os, sys
import shutil

from cyhub import is_available_memory


def register_global_attribute(attrs_dict):
    # TODO is this correct..?
    for k, v in attrs_dict.items():
        if k in globals():
            assert False, "[***] global attribute's name is repeated.! [***]"
        globals()[k] = v


def onMessage(msg):

    _msg, _params = msg

    """
    # Common
    """
    if _msg == 'common::set_key_event':
        _key, _modifiers = _params
        app_slice.set_key_event(_key, _modifiers)
        app_slice2.set_key_event(_key, _modifiers)

    """
    # DBM
    """
    if _msg == 'dbm::load_data':
        _selected_models, _app_id = _params
        # TODO should remove redundancy!!
        _exist_list = []
        for _model in _selected_models:
            if _model.parent() is None:
                """
                case of study
                """
                _children = _model.children()
                for _series in _children[:]:
                    _study_uid = _model.itemData['StudyInstanceUID']
                    _series_uid = _series.itemData['SeriesInstanceUID']
                    _patient_info = {'id': _model.itemData['PatientID'],
                                     'name': _model.itemData['PatientName'],
                                     'sex': _model.itemData['PatientSex'],
                                     'age': _model.itemData['PatientAge'],
                                     'date': _model.itemData['DateTime'],
                                     'modality': _series.itemData['Modality'],
                                     # NOTE PatientID is equal to SeriesID when series item is referred
                                     'series_id': _series.itemData['PatientID']
                                     }
                    # is exist
                    if app_slice.slice_mgr.is_exist(_study_uid, _series_uid) or app_slice2.slice_mgr.is_exist(
                            _study_uid, _series_uid):
                        _exist_list.append([_patient_info['id'], _patient_info['series_id']])
                        continue
                    # Memory check!!!
                    if not is_available_memory(app_dbm.sig_msgbox):
                        return
                    _vtk_img, _patient_pos_ori, _wwl = app_dbm.dbm_mgr.retrieve_dicom(_study_uid, _series_uid)
                    onMessage(['slice::init_vtk', (_vtk_img, _patient_pos_ori, _wwl, _patient_info,
                                                   _study_uid, _series_uid, _app_id)])
            else:
                """
                case of series
                """
                _study_uid = _model.parent().itemData['StudyInstanceUID']
                _series_uid = _model.itemData['SeriesInstanceUID']
                _patient_info = {'id': _model.parent().itemData['PatientID'],
                                 'name': _model.parent().itemData['PatientName'],
                                 'sex': _model.parent().itemData['PatientSex'],
                                 'age': _model.parent().itemData['PatientAge'],
                                 'date': _model.parent().itemData['DateTime'],
                                 'modality': _model.itemData['Modality'],
                                 # NOTE PatientID is equal to SeriesID when series item is referred
                                 'series_id': _model.itemData['PatientID']
                                 }
                if app_slice.slice_mgr.is_exist(_study_uid, _series_uid) or app_slice2.slice_mgr.is_exist(_study_uid,
                                                                                                          _series_uid):
                    _exist_list.append([_patient_info['id'], _patient_info['series_id']])
                    continue
                # Memory check!!!
                if not is_available_memory(app_dbm.sig_msgbox):
                    return
                _vtk_img, _patient_pos_ori, _wwl = app_dbm.dbm_mgr.retrieve_dicom(_study_uid, _series_uid)
                onMessage(['slice::init_vtk', (_vtk_img, _patient_pos_ori, _wwl, _patient_info,
                                               _study_uid, _series_uid, _app_id)])

        if len(_exist_list) > 0:
            _exist_list.reverse()
            _str_sids = ""
            while True:
                _pid, _sid = _exist_list.pop()
                _str_sids += " * %s [%s]"%(str(_pid), str(_sid))
                if len(_exist_list) == 0:
                    break
                else:
                    _str_sids += "\n"
            app_dbm.sig_msgbox.emit('Already loaded.',
                                    'The dicom file is already loaded.\n%s' % _str_sids)
            _exist_list.clear()


    elif _msg == 'dbm::stop':
        _study_uid, _series_uid = _params
        app_dbm.release_downloader(_study_uid, _series_uid)

    elif _msg == 'dbm::update_thumbnail_img':
        app_dbm.refresh_thumbnail_img()


    """
    # SLICE
    """
    if _msg == 'slice::init_vtk':
        _vtk_img, patient_pos_ori, _wwl, _patient_info, _study_uid, _series_uid, _target_app_id = _params
        if _target_app_id == 0:
            next_id = app_slice.get_next_layout_id2(_study_uid)
            if next_id >= 0:
                app_slice.init_vtk(_vtk_img, patient_pos_ori, _wwl, _patient_info, _study_uid, _series_uid, next_id)
        elif _target_app_id == 1:
            next_id = app_slice2.get_next_layout_id2(_study_uid)
            if next_id >= 0:
                app_slice2.init_vtk(_vtk_img, patient_pos_ori, _wwl, _patient_info, _study_uid, _series_uid, next_id)

    elif _msg == 'slice::busy_check':
        app_slice.busy_check()
        app_slice2.busy_check()

    elif _msg == 'slice::try_fullscreen_mode':
        _full_screen_mode = _params
        # next_id_1 = app_slice.get_next_layout_id()
        # img_cnt_1 = app_slice.slice_mgr.get_vtk_img_count()
        # next_id_2 = app_slice2.get_next_layout_id()
        # img_cnt_2 = app_slice2.slice_mgr.get_vtk_img_count()
        #
        # # if app1 is available
        # if next_id_1 >= 0:
        #     # if any vtk img isn't initialized in app1, do fullscreen mode of app1
        #     if img_cnt_1 == 0:
        #         app_slice.fullscreen(next_id_1, _full_screen_mode)
        #     # else, do nothing
        #     else:
        #         return
        # else:
        #     # if app2 is available
        #     if next_id_2 >= 0:
        #         # if any vtk img isn't initialized in app2, do fullscreen mode of app2
        #         if img_cnt_2 == 0:
        #             app_slice2.fullscreen(next_id_2, _full_screen_mode)
        #         # else, do nothing
        #         else:
        #             return

    elif _msg == 'slice::update_thumbnail_img':
        app_slice.refresh_thumbnail_img()
        app_slice2.refresh_thumbnail_img()

    elif _msg == 'slice::refresh_all':
        app_slice.sig_refresh_all.emit()
        app_slice2.sig_refresh_all.emit()

    elif _msg == 'slice::set_dummy_thumbnail':
        _global_pos, _img_url, _mode = _params
        if app_slice.is_contained(_global_pos):
            app_slice.set_dummy_thumbnail(_global_pos, _img_url, _mode)
        elif app_slice2.is_contained(_global_pos):
            app_slice2.set_dummy_thumbnail(_global_pos, _img_url, _mode)

    elif _msg == 'slice::release_dummy_thumbnail':
        app_slice.release_dummy_thumbnail()
        app_slice2.release_dummy_thumbnail()

    elif _msg == 'slice::send_to_other_app':
        _global_mouse, _study_uid, _series_uid = _params
        if app_slice.is_contained(_global_mouse):
            _slices = []
            _indices = []
            if _series_uid is None:
                _slices, _indices = app_slice2.slice_win.get_slice_objs(_study_uid)
            else:
                _slices = [app_slice2.slice_win.get_slice_obj(_study_uid, _series_uid)]
                _indices = [None]
            for _s, _i in zip(_slices, _indices):
                if app_slice.insert_slice_obj(_s, _i):
                    app_slice2.remove_slice_obj(_study_uid, _series_uid)
        elif app_slice2.is_contained(_global_mouse):
            _slices = []
            _indices = []
            if _series_uid is None:
                _slices, _indices = app_slice.slice_win.get_slice_objs(_study_uid)
            else:
                _slices = [app_slice.slice_win.get_slice_obj(_study_uid, _series_uid)]
                _indices = [None]
            for _s, _i in zip(_slices, _indices):
                if app_slice2.insert_slice_obj(_s, _i):
                    app_slice.remove_slice_obj(_study_uid, _series_uid)

    elif _msg == 'slice::change_selected_slice_of_other_app':
        _value, _sender = _params
        if _sender is app_slice:
            app_slice2.move_selected_slice(_value)
        elif _sender is app_slice2:
            app_slice.move_selected_slice(_value)

    # # MPR
    # elif _msg == 'mpr::init_vtk':
    #     app_mpr.mpr_mgr.init_vtk(_params)
    #     # app_mpr2.mpr_mgr.init_vtk(_params)
    # elif _msg == 'mpr::clear_all_actors':
    #     app_mpr.mpr_mgr.clear_all_actors()
    #     app_mpr.mpr_mgr.on_refresh_all()
    #     # app_mpr2.mpr_mgr.clear_all_actors()
    #     # app_mpr2.mpr_mgr.on_refresh_all()
    # elif _msg == 'mpr::refresh_all':
    #     app_mpr.sig_refresh_all.emit()
    #     # app_mpr2.sig_refresh_all.emit()

    # debug
    elif _msg == 'test_msg':
        print("This is test msg :: ", _params)
