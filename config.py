import src.widgets.topbar.window
import src.lib.hyprfuncs

from ignis.utils.get_current_dir import get_current_dir
from ignis.utils.sass import sass_compile
from ignis.app import IgnisApp

app = IgnisApp.get_default()
app.apply_css(f"{get_current_dir()}/src/styles/main.scss")
