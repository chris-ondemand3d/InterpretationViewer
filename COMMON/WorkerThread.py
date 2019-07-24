import os
import threading
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QThread, QMutex


class __Worker(QtCore.QObject):

    finished = QtCore.pyqtSignal()

    def set_params(self, func, *args):
        self.func = func
        self.args = args

    @QtCore.pyqtSlot()
    def run(self):
        print("    Worker(%d) Thread is Started!!" % self.id)
        self.func(*self.args)
        self.finished.emit()

    def set_id(self, id):
        self.id = id


MUTEX = QMutex()
STOP = False

def get_event():
    return threading.Event()
EVENT = get_event


def create_worker(idx):
    _worker = __Worker()
    _worker.set_id(idx)
    _worker_thread = QThread()
    _worker.finished.connect(_worker_thread.quit)
    _worker_thread.started.connect(_worker.run)
    return _worker, _worker_thread

def start_worker(worker, worker_thread, func, *args, _finished_func=None):
    # clean up
    global STOP
    STOP = False
    try: worker_thread.finished.disconnect()
    except TypeError: pass
    worker_thread.finished.connect(lambda: print("    Worker(%d) Thread is Finished :)"%worker.id))
    if _finished_func:
        worker_thread.finished.connect(_finished_func)
    # run
    worker.set_params(func, *args)
    worker.moveToThread(worker_thread)
    worker_thread.start()
