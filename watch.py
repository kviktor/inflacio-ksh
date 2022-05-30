import traceback
from importlib import reload
from pyinotify import (
    WatchManager,
    IN_DELETE,
    IN_CREATE,
    IN_CLOSE_WRITE,
    ProcessEvent,
    Notifier,
)
import core


class Process(ProcessEvent):
    def _run_build(self, event):
        if event.name.endswith((".py", ".jinja")):
            reload(core)
            core.build()
            print("Reloaded for", event.name)

    def process_IN_CREATE(self, event):
        self._run_build(event)

    def process_IN_CLOSE_WRITE(self, event):
        self._run_build(event)


while True:
    wm = WatchManager()
    process = Process()
    notifier = Notifier(wm, process)
    mask = IN_DELETE | IN_CREATE | IN_CLOSE_WRITE
    wdd = wm.add_watch(".", mask, rec=True)

    try:
        while True:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
    except KeyboardInterrupt:
        notifier.stop()
        break
    except Exception:
        print(traceback.format_exc())
