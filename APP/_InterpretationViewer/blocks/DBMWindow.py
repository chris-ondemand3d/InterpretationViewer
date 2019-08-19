import os, sys

from cyhub.cy_image_holder import CyQQuickView

from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import QObject, QUrl, QTimer, Qt, pyqtSlot, QVariant
from PyQt5.QtQml import QQmlProperty


class DBMWindow(QObject):
    def __init__(self, _app, _mgr, *args, **kdws):
        super().__init__()
        self._app = _app
        self._mgr = _mgr

        # self.reset()
        self.initialize()

    def initialize(self):
        self.study_model = self._mgr.get_study_model()
        self.related_study_model = self._mgr.get_related_study_model()
        self._app.rootContext().setContextProperty('study_treeview_model', self.study_model)
        self._app.rootContext().setContextProperty('related_study_treeview_model', self.related_study_model)
        # self.dbm.PT_sort_data(4, 0)

        # query studies & init treeview
        self.refresh_study_model()

        _win_source = QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), '../layout/dbm/DBM_layout.qml'))
        self._app.setSource(_win_source)

        self.dbm_msg_box_item = self._app.rootObject().findChild(QObject, 'dbm_message_box')

        # connect signals
        study_treeview_item = self._app.rootObject().findChild(QObject, 'study_treeview')
        study_treeview_item.sig_changed_index.connect(self.on_index_changed)
        study_treeview_item.sig_childitem_dclick.connect(self.on_childitem_dblclick)
        study_treeview_item.sig_menu_trigger.connect(self.on_data_load)
        related_study_treeview_item = self._app.rootObject().findChild(QObject, 'related_study_treeview')
        related_study_treeview_item.sig_childitem_dclick.connect(self.on_childitem_dblclick)
        related_study_treeview_item.sig_menu_trigger.connect(self.on_data_load)

    def reset(self):
        #TODO!!!
        # win reset
        # self._app.reset()

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
        # to check the dicom data is already exists.
        self._app.send_message.emit(['dbm::load_data', [[selected_model, ], 0]])

    @pyqtSlot(str, QVariant)
    def on_data_load(self, cmd, indices):
        indices = indices.toVariant()
        models = [index.internalPointer() for index in indices]
        if cmd == 'view(1)':
            self._app.send_message.emit(['dbm::load_data', [models, 0]])
        if cmd == 'view(2)':
            self._app.send_message.emit(['dbm::load_data', [models, 1]])
