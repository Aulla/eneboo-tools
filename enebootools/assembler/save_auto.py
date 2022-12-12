"""Save auto module."""
from watchdog import observers, events

from enebootools.assembler.kobjects import ObjectIndex, FeatureObject
from enebootools.assembler import database as asmdb
import os, time

from typing import List


class ObserverAction:
    """ObserverAction class."""

    _iface = None
    _feat: str = ""
    _watcher = None
    _event_handler = None
    _src_folder = None
    _queqe_events: List

    def __init__(self, iface, feat):
        self._iface = iface
        self._feat = feat
        self._watcher = observers.Observer()
        self._event_handler = events.FileSystemEventHandler()
        self._queqe_events = []

    def run(self):
        started = self.start_observer()
        try:
            if started:
                while True:
                    time.sleep(1)
                    self.proccess_queqe()

        except KeyboardInterrupt as error:
            pass

        if started:
            self._watcher.stop()
            self._watcher.join()

        print("Terminada la escucha de", self._feat)
        return 0

    def start_observer(self):
        self.resolve_folder()
        if not os.path.exists(self._src_folder):
            self._iface.warn("La carpeta %s no existe" % (self._src_folder))
            return False
        self._watcher.schedule(self._event_handler, self._src_folder, recursive=True)
        print("Escuchando cambios en", self._feat, "-->", self._src_folder)
        self._event_handler.on_any_event = self.queqe_event

        self._watcher.start()
        return True

    def resolve_folder(self):
        db = asmdb.init_database()
        oi = ObjectIndex(self._iface)
        oi.analyze_objects()
        feature = FeatureObject.find(self._feat)
        if not feature:
            self._iface.error("Funcionalidad %s desconocida." % self._feat)
            return None
        # print("*", feature, self._feat)
        # result = []
        # for patch_folder in feature.get_patch_list():
        #    result.append(os.path.join(feature.fullpath, "patches", patch_folder))
        self._src_folder = os.path.join(feature.fullpath, "build", "src")

    def proccess_queqe(self):

        for num, event in enumerate(list(self._queqe_events)):
            print("Procesando evento en fichero", num, event.src_path)
            self.launch_action()
            for ev_orig in self._queqe_events:
                if ev_orig.src_path == event.src_path:
                    self._queqe_events.remove(ev_orig)
                    break

    def queqe_event(self, new_event):

        if new_event.is_directory:
            return
        file_name = str(os.path.basename(new_event.src_path))
        if file_name.startswith("."):
            return

        for ev_ in self._queqe_events:
            if new_event.src_path == ev_.src_path:
                return

        self._queqe_events.append(new_event)

    def launch_action(self):

        try:
            asmdb.do_save_recent(self._iface, self._feat)
            self._iface.do_build("final", self._feat)

        except Exception as error:
            self._iface.error(str(error))
