#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bash pruebas/ejecutar_pruebas.sh
python pruebas/validar_ejemplos.py
