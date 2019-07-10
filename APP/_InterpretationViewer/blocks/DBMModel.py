from PyQt5.QtCore import QObject, QModelIndex, QAbstractItemModel, QByteArray, Qt, QVariant


PROJECT_TREEVIEW_HEADER = [
    'PatientID', 'PatientName', 'PatientSex', 'PatientAge', 'DateTime',
    'Imgs', 'Modality', 'BodyPartExamined', 'Description', 'Comment',
    'Key'
]


class SeriesItem(object):
    def __init__(self, parent=None):
        self.itemData = dict()
        self.childItems = []
        self.parentItem = parent

    def create_parent_item(self, data):
        self.itemData['PatientID'] = data['PatientID']
        self.itemData['PatientName'] = data['PatientName']
        self.itemData['PatientSex'] = data['PatientSex']
        self.itemData['PatientAge'] = data['PatientAge']
        self.itemData['DateTime'] = data['StudyDateTime']
        self.itemData['Description'] = data['StudyDescription']

        _count_CT = 0
        _count_CT_series = 0
        _count_PRJ_series = 0

        for k, v in enumerate(data['Series']):
            if data['Series'][v]['Modality'] == "CT":
                _count_CT_series += 1
                _count_CT += data['Series'][v]['NumberOfImages']
            # elif data['Series'][v]['Modality'] == "PRJ":
            #     _count_PRJ_series += 1
            else:
                pass

        _imgs_str = str(_count_CT + _count_PRJ_series) + '(' + str(_count_CT_series + _count_PRJ_series) + ')'

        self.itemData['Imgs'] = _imgs_str
        self.itemData['Modality'] = None
        self.itemData['BodyPartExamined'] = data['BodyPartExamined']
        self.itemData['Comment'] = data['Comments']
        self.itemData['Key'] = data['Study_Key']

    def add_child_item(self, data):
        _data = data
        child_item = SeriesItem(self)
        child_item.itemData['PatientID'] = _data['SeriesNumber']
        child_item.itemData['PatientName'] = None
        child_item.itemData['PatientSex'] = None
        child_item.itemData['PatientAge'] = None
        child_item.itemData['DateTime'] = _data['SeriesDateTime']
        child_item.itemData['Description'] = _data['SeriesDescription']
        # if _data['Modality'] == 'CT':
        #     child_item.itemData['Imgs'] = len(_data['Image'])
        # else:
        child_item.itemData['Imgs'] = _data['NumberOfImages']
        child_item.itemData['Modality'] = _data['Modality']
        child_item.itemData['BodyPartExamined'] = None
        child_item.itemData['Comment'] = _data['Comments']
        child_item.itemData['Key'] = _data['Series_Key']

        self.childItems.append(child_item)

    def childAtRow(self, row):
        return self.childItems[row]

    def children(self):
        return self.childItems

    def parent(self):
        return self.parentItem

    def get_parent_data(self, role):
        column_data = {
            Qt.DisplayRole: QVariant(self.itemData['PatientID']),
            Qt.UserRole: QVariant(self.itemData['PatientName']),
            Qt.UserRole + 1: QVariant(self.itemData['PatientSex']),
            Qt.UserRole + 2: QVariant(self.itemData['PatientAge']),
            Qt.UserRole + 3: QVariant(self.itemData['DateTime']),
            Qt.UserRole + 4: QVariant(self.itemData['Imgs']),
            Qt.UserRole + 5: QVariant(self.itemData['Modality']),
            Qt.UserRole + 6: QVariant(self.itemData['BodyPartExamined']),
            Qt.UserRole + 7: QVariant(self.itemData['Description']),
            Qt.UserRole + 8: QVariant(self.itemData['Comment']),
            Qt.UserRole + 9: QVariant(self.itemData['Key'])
        }
        try:
            return column_data[role]
        except KeyError:
            return QVariant()

    #TODO! will be change series role
    def get_child_data(self, role):
        column_data = {
            Qt.DisplayRole: QVariant(self.itemData['PatientID']),
            Qt.UserRole: QVariant(self.itemData['PatientName']),
            Qt.UserRole + 1: QVariant(self.itemData['PatientSex']),
            Qt.UserRole + 2: QVariant(self.itemData['PatientAge']),
            Qt.UserRole + 3: QVariant(self.itemData['DateTime']),
            Qt.UserRole + 4: QVariant(self.itemData['Imgs']),
            Qt.UserRole + 5: QVariant(self.itemData['Modality']),
            Qt.UserRole + 6: QVariant(self.itemData['BodyPartExamined']),
            Qt.UserRole + 7: QVariant(self.itemData['Description']),
            Qt.UserRole + 8: QVariant(self.itemData['Comment']),
            Qt.UserRole + 9: QVariant(self.itemData['Key'])
        }
        try:
            return column_data[role]
        except KeyError:
            return QVariant()

            # def sort_children(self):
            #     if len(self.childItems) == 0 :
            #         return
            #     sorted_list = sorted(self.childItems, key = lambda _item : (_item.itemData['Series_Key'] ) )
            #     self.childItems = sorted_list[:]


class StudyModel(QAbstractItemModel):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.items = []
        self.headers = PROJECT_TREEVIEW_HEADER
        self.columns = len(self.headers)
        self.roles = dict()

        # TODO 새로운 Model 생성시 첫번째 Column Role 주의.
        for i, v in enumerate(self.headers):
            _temp = QByteArray()
            _temp.append(v)
            if i == 0:
                self.roles[Qt.DisplayRole] = _temp
            else:
                self.roles[Qt.UserRole + i - 1] = _temp

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headers[section])
        return QVariant()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            items = parent.internalPointer()
            return len(items.children())
        return len(self.items)

    def columnCount(self, parent):
        return self.columns

    def index(self, row, column, parent):
        if parent.isValid():
            item = parent.internalPointer()
            return self.createIndex(row, column, item.children()[row])
        else:
            pass

        return self.createIndex(row, column, self.items[row])

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        item = index.internalPointer()

        try:
            if not item.parentItem:
                return QModelIndex()
        except AttributeError:
            return QModelIndex()

        _children = item.parentItem.children()
        try:
            _index = self.items.index(_children[0].parentItem)
        except ValueError:
            _index = 0
        return self.createIndex(_index, 0, item.parentItem)

    def data(self, index, role):
        if not index.isValid():
            return None

        _item = index.internalPointer()

        if _item.parentItem is None:
            _model = self.items[index.row()]
            return _model.get_parent_data(role)
        else:
            child_item_counts = len(_item.parentItem.childItems)
            if child_item_counts > 0 :
                _model =_item.parentItem.childItems[index.row()]
                return _model.get_child_data(role)

    def roleNames(self):
        return self.roles

    def addData(self, data):
        for v1 in data['Study'].items():
            _parent_item = SeriesItem()
            _parent_item.create_parent_item(v1[1])
            self.items.append(_parent_item)
            for v2 in v1[1]['Series'].items():
                self.items[v1[0]].add_child_item(v2[1])
