from gi.repository import Gio, GObject, GLib

from ignis.base_service import BaseService

conf = Gio.Settings.new("com.github.XtremeTHN.DotFile.ags")

def get_variant(data) -> GLib.Variant:
    if isinstance(data, str):
        return GLib.Variant.new_string(data)
    elif isinstance(data, int):
        return GLib.Variant.new_int32(data)
    elif isinstance(data, (list, tuple, set)):
        variant_builder: GLib.VariantBuilder = GLib.VariantBuilder.new(GLib.VariantType.new('av'))

        for value in data:
            variant_builder.add_value(GLib.Variant.new_variant(get_variant(value)))

        return variant_builder.end()
    elif isinstance(data, dict):
        variant_builder = GLib.VariantBuilder.new(GLib.VariantType.new('a{sv}'))

        for key in data:
            if data[key] is None:
                continue

            key_string = str(key)

            variant_builder.add_value(
                GLib.Variant.new_dict_entry(
                    get_variant(key_string), GLib.Variant.new_variant(get_variant(data[key]))
                )
            )

        return variant_builder.end()
    else:
        raise Exception(f"Unknown data type: {type(data)}")


class Opt(BaseService):
    __gsignals__ = {
        "changed": (GObject.SignalFlags.RUN_FIRST, None, tuple()),
    }

    def __init__(self, key, type):
        self.key = key
        self.type = type
        self._value = None

        super().__init__()
        conf.connect(f"changed::{key}", self.on_gio_changed)

    def on_gio_changed(self):
        self.emit("changed")
        self.notify("value")

        self.value = self.retrieve()

    def retrieve(self):
        return conf.get_value(self.key).unpack()

    def on_change(self, func):
        conf.connect(f"changed::{self.key}", lambda *_: self.retrieve())

    @GObject.Property(nick="value")
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        conf.set_value(self.key, get_variant(val))

        self.emit("changed")
        self.notify("value")

    def resetValue(self):
        conf.reset(self.key)

    def _bind(self):
        return self.bind("value")

    def _as(self, func):
        self.bind("value", func)
