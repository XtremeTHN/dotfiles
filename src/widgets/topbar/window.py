from ignis.widgets import Widget
from ignis.services.hyprland import HyprlandService

from src.lib.style import toggleClassName

Hyprland = HyprlandService.get_default()

def _workspace(id):
    def onUpdate(hypr, _, box):
        toggleClassName(box, "active", hypr.active_workspace["id"] == int(box.name))

    # name is the id of the workspace
    box = Widget.Box(name=str(id))
    box.add_css_class("topbar-workspace")
    Hyprland.connect("notify::workspaces", onUpdate, box)

    return box

def fixed_workspaces_widget():
    return Widget.Box(
        spacing=3,
        child=[_workspace(x + 1) for x in range(5)]
    )

def dynamic_workspaces_widget():
    def onUpdate(hypr, _, box: Widget.Box):
        for x in box.child:
            x.visible = any(w for w in Hyprland.workspaces if w["id"] == int(x.name))

    box = fixed_workspaces_widget()
    Hyprland.connect("notify::workspaces", onUpdate, box)
    return box

def window_title():
    def format_title(_h, _p, w):
        try:
            w.set_label(Hyprland.active_window["title"])
        except KeyError:
            w.set_label(f"Workspace {Hyprland.active_workspace["id"]}")

    title = Widget.Label()
    Hyprland.connect("notify", format_title, title)

    return title

def topbar_content():
    return Widget.Box(
        css_classes=["topbar"],
        child=[
            dynamic_workspaces_widget(),
            window_title()
        ]
    )

# Main widget
Widget.Window(
    "topbar",
    anchor=["top", "left", "right"],
    child=topbar_content()
)
