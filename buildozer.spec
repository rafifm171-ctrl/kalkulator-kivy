[app]

title = Kalkulator Kivy
package.name = kalkulatorkivy
package.domain = org.kalkulator

source.include_exts = py,png,jpg,kv,atlas
source.dir = .
version = 2.0

requirements = python3,kivy

orientation = portrait
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.androidx = True
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
