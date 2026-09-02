#!/usr/bin/env /usr/bin/python3
"""Single daemon remapping two Lenovo Yoga keyboard quirks:

- Copilot key combo (LEFTMETA+LEFTSHIFT+F23 on the main keyboard) -> RIGHTCTRL
- Two Ideapad extra-buttons scancodes (reported as KEY_UNKNOWN, since the
  ideapad-laptop driver has no sparse_keymap table entry for them) -> F16/F17
  (resolve to XF86Launch7/XF86Launch8 in GNOME's keymap)

Grabs both physical devices exclusively and re-emits everything (unmodified,
except for the two remaps above) through one virtual uinput device.
"""
import select
import time

import evdev
from evdev import UInput, ecodes as e

COMBO = {e.KEY_LEFTMETA, e.KEY_LEFTSHIFT, e.KEY_F23}
COMBO_TARGET = e.KEY_RIGHTCTRL
COMBO_WINDOW = 0.05  # seconds to wait for the rest of the combo after the first key

SCAN_TO_KEY = {
    0x146: e.KEY_F16,
    0x148: e.KEY_F17,
}


def find_device(name):
    for path in evdev.list_devices():
        dev = evdev.InputDevice(path)
        if dev.name == name:
            return dev
    raise RuntimeError(f"{name!r} device not found")


class ComboRemap:
    """Buffers LEFTMETA to see if LEFTSHIFT+F23 follow; if so, swaps the
    whole combo for a single RIGHTCTRL press. Passes everything else through
    untouched, including a lone Super tap."""

    def __init__(self, ui):
        self.ui = ui
        self.pending = []
        self.pending_keys = set()
        self.active = False
        self.deadline = None

    def flush(self):
        for ev in self.pending:
            self.ui.write_event(ev)
        self.ui.syn()
        self.pending, self.pending_keys, self.deadline = [], set(), None

    def handle(self, event):
        if event.type != e.EV_KEY:
            self.ui.write_event(event)
            return
        code, value = event.code, event.value

        if self.active:
            if code in COMBO and value == 0:
                self.pending_keys.discard(code)
                if not self.pending_keys:
                    self.ui.write(e.EV_KEY, COMBO_TARGET, 0)
                    self.ui.syn()
                    self.active = False
            return  # swallow all combo-key traffic while active

        if code in COMBO and value == 1 and code not in self.pending_keys:
            self.pending.append(event)
            self.pending_keys.add(code)
            if self.pending_keys == COMBO:
                self.pending, self.pending_keys = [], set(COMBO)
                self.ui.write(e.EV_KEY, COMBO_TARGET, 1)
                self.ui.syn()
                self.active = True
                self.deadline = None
            else:
                self.deadline = time.time() + COMBO_WINDOW
            return

        if self.pending:
            self.flush()
        self.ui.write_event(event)

    def timed_out(self):
        self.flush()


class ScanRemap:
    """Substitutes specific (scancode -> keycode) pairs reported as
    KEY_UNKNOWN, distinguished by the preceding MSC_SCAN value."""

    def __init__(self, ui, mapping):
        self.ui = ui
        self.mapping = mapping
        self.last_scan = None

    def handle(self, event):
        if event.type == e.EV_MSC and event.code == e.MSC_SCAN:
            self.last_scan = event.value
            return
        if event.type == e.EV_KEY and event.code == e.KEY_UNKNOWN and self.last_scan in self.mapping:
            self.ui.write(e.EV_KEY, self.mapping[self.last_scan], event.value)
            self.ui.syn()
            return
        if event.type == e.EV_SYN:
            self.ui.syn()
        else:
            self.ui.write_event(event)


def build_uinput(keyboard, extra_buttons):
    caps = keyboard.capabilities()
    caps.pop(e.EV_SYN, None)
    extra_keys = set(extra_buttons.capabilities().get(e.EV_KEY, []))
    caps[e.EV_KEY] = sorted(set(caps.get(e.EV_KEY, [])) | extra_keys | set(SCAN_TO_KEY.values()))
    assert COMBO <= set(caps[e.EV_KEY]), "keyboard is missing one of the combo keys"
    return UInput(caps, name="yoga-key-remap")


def main():
    keyboard = find_device("AT Translated Set 2 keyboard")
    extra_buttons = find_device("Ideapad extra buttons")
    keyboard.grab()
    extra_buttons.grab()

    ui = build_uinput(keyboard, extra_buttons)
    combo = ComboRemap(ui)
    scan = ScanRemap(ui, SCAN_TO_KEY)

    try:
        while True:
            timeout = max(0, combo.deadline - time.time()) if combo.deadline else None
            ready, _, _ = select.select([keyboard.fd, extra_buttons.fd], [], [], timeout)
            if not ready:
                combo.timed_out()
                continue
            if keyboard.fd in ready:
                for event in keyboard.read():
                    combo.handle(event)
            if extra_buttons.fd in ready:
                for event in extra_buttons.read():
                    scan.handle(event)
    finally:
        keyboard.ungrab()
        extra_buttons.ungrab()
        ui.close()


if __name__ == "__main__":
    main()
