#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p pruebas/.classes
javac -encoding UTF-8 -d pruebas/.classes \
  android/app/src/main/java/ar/edu/et35/panolapp/domain/Tablet.java \
  android/app/src/main/java/ar/edu/et35/panolapp/domain/Reglas.java \
  pruebas/ReglasTest.java
java -ea -cp pruebas/.classes ReglasTest
