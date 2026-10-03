[app]
title = Kalkulator Serbaguna
package.name = kalkulatorserbaguna
package.domain = org.kalkulator
source.include_exts = py,png,jpg,kv,atlas
source.dir = .
version = 2.0
requirements = python3,kivy,requests,certifi,urllib3,idna,charset-normalizer
orientation = portrait
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.architectures = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
