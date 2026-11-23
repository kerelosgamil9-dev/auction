# -*- coding: utf-8 -*-
"""Small Android-only helpers (pyjnius). On a PC every function just returns False.
Android does not let an app switch the hotspot on by itself, so the app opens the
right system screen and the player taps the switch there."""
from kivy.utils import platform


def _start(action=None, component=None):
    from jnius import autoclass
    activity = autoclass("org.kivy.android.PythonActivity").mActivity
    Intent = autoclass("android.content.Intent")
    if component:
        intent = Intent()
        intent.setClassName(component[0], component[1])
    else:
        intent = Intent(action)
    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    activity.startActivity(intent)


def _first_that_works(options):
    if platform != "android":
        return False
    for kind, value in options:
        try:
            _start(**({"action": value} if kind == "action" else {"component": value}))
            return True
        except Exception:
            continue
    return False


def open_hotspot_settings():
    """Open the 'portable hotspot' screen (falls back to wireless settings)."""
    return _first_that_works([
        ("component", ("com.android.settings", "com.android.settings.TetherSettings")),
        ("component", ("com.android.settings", "com.android.settings.Settings$TetherSettingsActivity")),
        ("action", "android.settings.WIRELESS_SETTINGS"),
        ("action", "android.settings.SETTINGS"),
    ])


def open_wifi_panel():
    """Open the quick Wi-Fi panel (Android 10+), or the Wi-Fi settings page."""
    return _first_that_works([
        ("action", "android.settings.panel.action.WIFI"),
        ("action", "android.settings.WIFI_SETTINGS"),
        ("action", "android.settings.SETTINGS"),
    ])
