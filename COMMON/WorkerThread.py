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


__WORKER = __Worker()
__WORKER.set_id(1)
__WORKER_THREAD = QThread()
__WORKER.finished.connect(__WORKER_THREAD.quit)
__WORKER_THREAD.started.connect(__WORKER.run)

__WORKER2 = __Worker()
__WORKER2.set_id(2)
__WORKER_THREAD2 = QThread()
__WORKER2.finished.connect(__WORKER_THREAD2.quit)
__WORKER_THREAD2.started.connect(__WORKER2.run)


MUTEX = QMutex()
STOP = False

def get_event():
    return threading.Event()
EVENT = get_event


def start_worker(func, *args, _finished_func=None):
    # clean up
    global STOP
    STOP = False
    try: __WORKER_THREAD.finished.disconnect()
    except TypeError: pass
    __WORKER_THREAD.finished.connect(lambda: print("    Worker1 Thread is Finished :)"))
    if _finished_func:
        __WORKER_THREAD.finished.connect(_finished_func)
    # run
    __WORKER.set_params(func, *args)
    __WORKER.moveToThread(__WORKER_THREAD)
    __WORKER_THREAD.start()


def start_worker2(func, *args, _finished_func=None):
    # clean up
    global STOP
    STOP = False
    try: __WORKER_THREAD2.finished.disconnect()
    except TypeError: pass
    __WORKER_THREAD2.finished.connect(lambda: print("    Worker2 Thread is Finished :)"))
    if _finished_func:
        __WORKER_THREAD2.finished.connect(_finished_func)
    # run
    __WORKER2.set_params(func, *args)
    __WORKER2.moveToThread(__WORKER_THREAD2)
    __WORKER_THREAD2.start()


def is_running():
    return __WORKER_THREAD.isRunning()


def stop_all():
    __WORKER_THREAD.quit()
    __WORKER_THREAD2.quit()
