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

        _win_source = QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), '../layout/dbm/DBM_layout.qml'))
        self._win.setSource(_win_source)

        # connect signals
        study_treeview = self._win.rootObject().findChild(QObject, 'study_treeview')
        study_treeview.sig_childitem_dclick.connect(self.on_childitem_dblclick)
        study_treeview.sig_menu_trigger.connect(self.on_data_load)

    def reset(self):
        #TODO!!!
        # win reset
        # self._win.reset()

        def _remove(X):
            if type(X) is not dict:
                for o in X:
                    del o
            X.clear()

    @pyqtSlot(QVariant)
    def on_childitem_dblclick(self, index):
        selected_model = index.internalPointer()
        self.load_data_from_model(selected_model)

        # if selected_model.parent() is None:
        #     """
        #     case of study
        #     """
        #     children = selected_model.children()
        #     layout_idx = 0
        #     for series in children[:]:
        #         vtk_img = self._mgr.retrieve_dicom(selected_model.itemData['StudyInstanceUID'],
        #                                            series.itemData['SeriesInstanceUID'])
        #         self._win.send_message.emit(['slice::init_vtk', (vtk_img, layout_idx)])
        #         layout_idx += 1
        # else:
        #     """
        #     case of series
        #     """
        #     vtk_img = self._mgr.retrieve_dicom(selected_model.parent().itemData['StudyInstanceUID'],
        #                                        selected_model.itemData['SeriesInstanceUID'])
        #     self._win.send_message.emit(['slice::init_vtk', (vtk_img, 0)])

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

            # set layout
            # layout = (1,1) if len(children) == 1 else (4,4)
            # self._win.send_message.emit(['slice::set_layout', layout])

            # init vtk
            layout_idx = 0
            for series in children[:]:
                vtk_img = self._mgr.retrieve_dicom(selected_model.itemData['StudyInstanceUID'],
                                                   series.itemData['SeriesInstanceUID'])
                self._win.send_message.emit(['slice::init_vtk', (vtk_img, 'append', layout_idx)])
                layout_idx += 1
        else:
            """
            case of series
            """
            vtk_img = self._mgr.retrieve_dicom(selected_model.parent().itemData['StudyInstanceUID'],
                                               selected_model.itemData['SeriesInstanceUID'])
            # self._win.send_message.emit(['slice::set_layout', (1,1)])
            self._win.send_message.emit(['slice::init_vtk', (vtk_img, 'new', 0)])
