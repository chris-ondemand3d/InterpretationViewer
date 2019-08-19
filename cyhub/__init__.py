import locale
import psutil


def is_available_memory(notify_signal=None):
    # Memory check!!!
    mem_usage = psutil.virtual_memory()
    mem_available = mem_usage[1]
    mem_percent = mem_usage[2]
    if mem_available <= 1 * (1024 ** 3):
        if notify_signal:
            locale.setlocale(locale.LC_ALL, 'en_US')
            _bytes = locale.format("%d", mem_available, grouping=True)
            _title = "It's unable to load data."
            _text = "%d%% of memory is in used.\n%s bytes left.\nPlease check your memory." % (mem_percent, _bytes)
            notify_signal.emit(_title, _text)
        print("*** Memory Warning!!! ***\nIt's unable to load data.\n%d%% of memory is in use.\n%s bytes left.\n"
              % (mem_percent, mem_available))
        return False
    return True