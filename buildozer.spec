[app]
title = المزاد الكبير - Grand Auction
package.name = grandauction
package.domain = org.auctiongame
source.dir = .
source.include_exts = py,png,wav,ttf
source.exclude_dirs = .github,__pycache__,bin,.buildozer
source.exclude_patterns = gen_assets.py
version = 1.0.0
requirements = python3,kivy==2.3.1
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png
orientation = portrait
fullscreen = 0

# INTERNET + the Wi-Fi/network states are needed for sockets on the local network / hotspot.
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, CHANGE_WIFI_MULTICAST_STATE
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
