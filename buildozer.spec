[app]
title = BookWho?
package.name = bookwho
package.domain = cl.uct
source.dir = .
source.include_exts = py,kv,ttf,png,jpg,json
source.exclude_dirs = .venv,tests,screenshots,.cache,bin,.buildozer,__pycache__
source.exclude_patterns = data.json
version = 1.0
# ponytail: KivyMD 2.0 no está en PyPI; sin materialshapes/pycairo porque la app no usa FitImage
requirements = python3,kivy==2.3.1,https://github.com/kivymd/KivyMD/archive/master.zip,materialyoucolor==3.0.4,asynckivy==0.6.4,asyncgui==0.6.3,exceptiongroup,pillow,plyer==2.1.0,certifi,filetype,charset_normalizer
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,POST_NOTIFICATIONS
android.api = 34
android.minapi = 24
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 0
