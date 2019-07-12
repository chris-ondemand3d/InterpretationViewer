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
        self._win.rootContext().setContextProperty('study_treeview_model', self.study_model)
        # self.dbm.PT_sort_data(4, 0)

        _data = self._mgr.query_studies_series()
        self.study_model.beginResetModel()
        self.study_model.addData(_data)
        self.study_model.endResetModel()

        # win init
        _win_source = QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), '../layout/dbm/DBM_layout.qml'))
        self._win.setSource(_win_source)

        # connect signals
        study_treeview = self._win.rootObject().findChild(QObject, 'study_treeview')
        study_treeview.sig_childitem_dclick.connect(self.on_childitem_dblclick)

    def reset(self):
        #TODO!!!
        # win reset
        # self._win.reset()

        def _remove(X):
            if type(X) is not dict:
                for o in X:
                    del o
            X.clear()

    @pyqtSlot(QVariant, QVariant)
    def on_childitem_dblclick(self, index, prev_index_info):
        prev_index_info = prev_index_info.toVariant()
        prev_index = dict()
        prev_index['parent'] = prev_index_info[0]
        prev_index['child'] = prev_index_info[1]
        selected_model = index.internalPointer()
        vtk_img = self._mgr.retrieve_dicom(selected_model.parent().itemData['StudyInstanceUID'],
                                           selected_model.itemData['SeriesInstanceUID'])
        self._win.send_message.emit(['mpr::init_vtk', vtk_img])
