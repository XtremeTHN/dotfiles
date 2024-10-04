from ignis.widgets import Widget

def toggleClassName(w: Widget.Box, _class: str, condition=None):
    if condition is not None:
        if condition:
            w.add_css_class(_class)
        else:
            w.remove_css_class(_class)
        return
    if _class in w.props.css_classes:
        w.remove_css_class(_class)
    else:
        w.add_css_class(_class)
