[app]
title = Grand Auction
package.name = grandauction
package.domain = org.auctiongame
source.dir = .
source.include_exts = py,png,wav,ttf
source.exclude_dirs = .github,__pycache__,bin,.buildozer
source.exclude_patterns = gen_assets.py
version = 1.0.0
requirements = python3==3.11.5,hostpython3==3.11.5,kivy==2.3.1
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png
orientation = portrait
fullscreen = 0

android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, CHANGE_WIFI_MULTICAST_STATE
android.api = 34
android.minapi = 26
android.ndk = 25b
android.ndk_api = 26
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
