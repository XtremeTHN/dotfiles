from ignis.utils.thread import run_in_thread
from ignis.utils.exec_sh import exec_sh
from ignis.base_service import BaseService
from ignis.services.hyprland.constants import HYPR_SOCKET_DIR
from gi.repository import GObject
import socket
import json

from typing import TypedDict

class Workspace(TypedDict):
    id: int
    name: str

class Client(TypedDict):
    address: str
    mapped: bool
    hidden: bool
    at: list[int]
    size: list[int]
    workspace: Workspace
    floating: bool
    pseudo: bool
    monitor: int
    title: str
    initialClass: str
    initialTitle: str
    pid: int
    xwayland: bool
    pinned: bool
    fullscreen: int
    fullscreenClient: int
    grouped: list
    tags: list
    swallowing: str
    focusHistoryID: int

class HyprEvents(BaseService):
    __gsignals__ = {
        "workspace": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "workspacev2": (GObject.SignalFlags.RUN_FIRST, None, (str,str)),
        "focusedmon": (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
        "activewindow": (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
        "activewindowv2": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "fullscreen": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "monitorremoved": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "monitoradded": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "monitoraddedv2": (GObject.SignalFlags.RUN_FIRST, None, (str,str,str)),
        "createworkspace": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "createworkspacev2": (GObject.SignalFlags.RUN_FIRST, None, (str,str)),
        "destroyworkspace": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "destroyworkspacev2": (GObject.SignalFlags.RUN_FIRST, None, (str,str)),
        "moveworkspace": (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
        "moveworkspacev2": (GObject.SignalFlags.RUN_FIRST, None, (str, str, str)),
        "renameworkspace": (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
        "activespecial": (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
        "activelayout": (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
        "openwindow": (GObject.SignalFlags.RUN_FIRST, None, (str, str, str, str)),
        "closewindow": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "movewindow": (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
        "movewindowv2": (GObject.SignalFlags.RUN_FIRST, None, (str, str, str)),
        "openlayer": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "closelayer": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "changefloatingmode": (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
        "submap": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "urgent": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "screencast": (GObject.SignalFlags.RUN_FIRST, None, (str,str)),
        "windowtitle": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "windowtitlev2": (GObject.SignalFlags.RUN_FIRST, None, (str,str)),
        "togglegroup": (GObject.SignalFlags.RUN_FIRST, None, tuple()),
        "moveintogroup": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "moveoutofgroup": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "ignoregrouplock": (GObject.SignalFlags.RUN_FIRST, None, tuple()),
        "lockgroups": (GObject.SignalFlags.RUN_FIRST, None, tuple()),
        "configreloaded": (GObject.SignalFlags.RUN_FIRST, None, tuple()),
        "pin": (GObject.SignalFlags.RUN_FIRST, None, (str,str)),
    }
    """
    Base class for listening to Hyprland events.
    """
    def __init__(self):
        """
        Initializes an instance of the class.

        Returns:
            None
        """
        self.running = True

        self.sock_hypr_events = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock_hypr_events.connect(f'{HYPR_SOCKET_DIR}/.socket2.sock')

        self._run()
        super().__init__()

    @run_in_thread
    def _run(self, *args):
        while self.running:
            data: list[str] = self.sock_hypr_events.recv(4096).decode().split('>>')

            event = data[0]
            args = data[1].split(',') if len(data) > 1 else []
            self.emit(event, *args)

    def close(self):
        self.sock_hypr_events.close()

class HyprlandService(BaseService):
    def __init__(self, **kwargs):
        super().__init__()

        self.__clients: dict[str, Client] = {}
        self.event_manager = HyprEvents.get_default()

        self.event_manager.connect("openwindow", self._sync_clients)
        self.event_manager.connect("closewindow", self._sync_clients)
        self._sync_clients()

    @GObject.Property(nick="clients")
    def clients(self):
        return self.__clients

    def message(self, msg: str, toJson=False):
        out = exec_sh(f"hyprctl {msg} " + "-j" if json else "").stdout

        if toJson:
            return json.loads(out)
        else:
            return out

    def _sync_clients(self, *_):
        clients = self.message("clients", toJson=True)

        self.__clients = {}
        for x in clients:
            self.__clients[x["address"]] = x

    def getClient(self, client) -> Client | None:
        return self.__clients.get(f"0x{client.strip("\n")}")
