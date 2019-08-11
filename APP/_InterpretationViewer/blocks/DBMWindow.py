import os, sys

from cyhub.cy_image_holder import CyQQuickView

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QObject, QUrl, QTimer, Qt, pyqtSlot, QVariant
from PyQt5.QtQml import QQmlProperty


class DBMWindow(QObject):
    def __init__(self, _win, _mgr, *args, **kdws):
        super().__init__()
        self._win = _win
        self._mgr = _mgr

        # self.reset()
        self.initialize()

    def initialize(self):
        self.study_model = self._mgr.get_study_model()
        self.related_study_model = self._mgr.get_related_study_model()
        self._win.rootContext().setContextProperty('study_treeview_model', self.study_model)
        self._win.rootContext().setContextProperty('related_study_treeview_model', self.related_study_model)
        # self.dbm.PT_sort_data(4, 0)

        # query studies & init treeview
        self.refresh_study_model()

        _win_source = QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), '../layout/dbm/DBM_layout.qml'))
        self._win.setSource(_win_source)

        # connect signals
        study_treeview_item = self._win.rootObject().findChild(QObject, 'study_treeview')
        study_treeview_item.sig_changed_index.connect(self.on_index_changed)
        study_treeview_item.sig_childitem_dclick.connect(self.on_childitem_dblclick)
        study_treeview_item.sig_menu_trigger.connect(self.on_data_load)
        related_study_treeview_item = self._win.rootObject().findChild(QObject, 'related_study_treeview')
        related_study_treeview_item.sig_childitem_dclick.connect(self.on_childitem_dblclick)
        related_study_treeview_item.sig_menu_trigger.connect(self.on_data_load)

    def reset(self):
        #TODO!!!
        # win reset
        # self._win.reset()

        def _remove(X):
            if type(X) is not dict:
                for o in X:
                    del o
            X.clear()

    def refresh_study_model(self):
        return self._mgr.refresh_study_model()

    def refresh_related_study_model(self, _model):

        # 1. clear model
        self._mgr.clear_related_study_model()

        # 2. get patiend id
        if _model.parent() is None:
            """
            case of study
            """
            _patiend_id = _model.itemData['PatientID']
        else:
            """
            case of series
            """
            _patiend_id = _model.parent().itemData['PatientID']

        if _patiend_id is None:
            return False

        # 3. filter by patiend id & set model
        self._mgr.refresh_related_study_model(_patiend_id)

    @pyqtSlot(QVariant, bool)
    def on_index_changed(self, index, trigger):
        selected_model = index.internalPointer()
        self.refresh_related_study_model(selected_model)

    @pyqtSlot(QVariant)
    def on_childitem_dblclick(self, index):
        selected_model = index.internalPointer()
        self.load_data_from_model(selected_model)

    @pyqtSlot(str, QVariant)
    def on_data_load(self, cmd, indices):
        indices = indices.toVariant()
        for index in indices:
            model = index.internalPointer()
            if cmd == 'view':
                self.load_data_from_model(model)

    def load_data_from_model(self, selected_model):
        if selected_model.parent() is None:
            """
            case of study
            """
            children = selected_model.children()

            # init vtk
            if len(children[:]) == 1:
                self._win.send_message.emit(['slice::try_fullscreen_mode', True])

            for series in children[:]:
                patient_info = {'id': selected_model.itemData['PatientID'],
                                'name': selected_model.itemData['PatientName'],
                                'sex': selected_model.itemData['PatientSex'],
                                'age': selected_model.itemData['PatientAge'],
                                'date': selected_model.itemData['DateTime'],
                                'modality': series.itemData['Modality'],

                                # NOTE PatientID is equal to SeriesID when series item is referred
                                'series_id': series.itemData['PatientID']
                                }
                study_uid = selected_model.itemData['StudyInstanceUID']
                series_uid = series.itemData['SeriesInstanceUID']
                vtk_img, wwl = self._mgr.retrieve_dicom(study_uid, series_uid)
                self._win.send_message.emit(['slice::init_vtk',
                                             (vtk_img, wwl, patient_info, study_uid, series_uid, 'append')])
        else:
            """
            case of series
            """
            self._win.send_message.emit(['slice::try_fullscreen_mode', True])
            patient_info = {'id': selected_model.parent().itemData['PatientID'],
                            'name': selected_model.parent().itemData['PatientName'],
                            'sex': selected_model.parent().itemData['PatientSex'],
                            'age': selected_model.parent().itemData['PatientAge'],
                            'date': selected_model.parent().itemData['DateTime'],
                            'modality': selected_model.itemData['Modality'],

                            # NOTE PatientID is equal to SeriesID when series item is referred
                            'series_id': selected_model.itemData['PatientID']
                            }
            study_uid = selected_model.parent().itemData['StudyInstanceUID']
            series_uid = selected_model.itemData['SeriesInstanceUID']
            vtk_img, wwl = self._mgr.retrieve_dicom(study_uid, series_uid)
            self._win.send_message.emit(['slice::init_vtk',
                                         (vtk_img, wwl, patient_info, study_uid, series_uid, 'new')])
