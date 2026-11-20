#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v gradle >/dev/null 2>&1; then
  echo 'Error: Gradle 8.13 no se encuentra instalado o en PATH. Ver README_COMPILACION.md' >&2
  exit 1
fi
gradle :app:assembleDebug
cp app/build/outputs/apk/debug/app-debug.apk 'pañol-app.apk'
printf 'APK construido: %s\n' "$(pwd)/pañol-app.apk"
