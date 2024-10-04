from .services.hyprland import HyprlandService, HyprEvents

from typing import Callable
from ignis.utils.exec_sh import exec_sh

import json

Events = HyprEvents.get_default()
Hyprland = HyprlandService.get_default()

def focus_urgent_window():
    def cb(_, address: str):
        win = Hyprland.getClient(address)
        if win is None:
            return

        # idk why picture-in-picture of zen browser sends an urgent signal
        if win["title"] == "Picture-in-Picture":
            return

        Hyprland.message(f"dispatch workspace {win["workspace"]["id"]}")

    Events.connect("urgent", cb)


focus_urgent_window()
