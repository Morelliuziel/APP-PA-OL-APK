# Trabajo Práctico 2 — Pañol-App

**Escuela Técnica N.º 35 Ing. Eduardo Latzina · Desarrollo de Sistemas · 2026**

## Qué incluye esta entrega

- `documentacion/Carpeta_Tecnica_Panol_App.pdf` — carpeta técnica completa con modelo de datos, reglas, CU-01/02/03/04, sprints, riesgos, pruebas, build e interrogatorio oral.
- `documentacion/Carpeta_Tecnica_Panol_App.docx` — versión editable.
- `documentacion/Guion_Defensa_Oral.pdf` — ayuda memoria de 2 páginas.
- `android/` — proyecto Android nativo Java/SQLite + Google Code Scanner (lector QR mediante cámara, autzoom y fallback teclado).
- `android/.github/workflows/compilar-apk.yml` — alternativa de construcción de APK en GitHub Actions al colocar el contenido de `android/` como raíz de un repositorio.
- `android/README_COMPILACION.md` — instrucciones detalladas de compilación e instalación real.
- `etiquetas/Etiquetas_QR_Imprimir_A4.pdf` — 3 QR reales, con series TAB-001/002/003 y datos JSON, aptos para imprimir.
- `etiquetas/TAB-001.png`, etc. y `etiquetas/TAB-001.txt`, etc. — los QR y su contenido literal.
- `pruebas/` — tests JVM de reglas, validación SQLite y decodificación de los PNG mediante OpenCV, más reporte de ejecución.

## Estado real del proyecto

**Verificado automáticamente**: 15 casos JVM del dominio; restricciones SQL de unicidad, estados, Home Office, legajos y clave foránea; lectura de las 3 imágenes QR; creación y renderizado de los PDF de la entrega.

**No verificado en este entorno**: compilación con Android Gradle Plugin, instalación de APK y funcionamiento en cámara Android física. El contenedor de desarrollo no incluye SDK Android ni Gradle y no tiene acceso a los repositorios necesarios para obtenerlos. Por tanto, **no se incluye `pañol-app.apk` ya compilado**; tampoco hay un archivo falso con extensión `.apk`.

Para obtener el archivo exigido al entregar, seguir **`android/README_COMPILACION.md`**. El archivo `app-debug.apk` generado debe copiarse bajo el nombre `pañol-app.apk` (construido real y firmado por Android Studio).

## Uso funcional propuesto

1. Escanear físicamente TAB-001 desde `etiquetas/Etiquetas_QR_Imprimir_A4.pdf`.
2. Confirmar alta y examinar la ficha y el historial.
3. Despachar para Home Office sin tarea para ver el bloqueo rojo, y después ingresar legajo `EMP-123` y tarea `TSK-100`.
4. Volver a leer la etiqueta: comprobar la ubicación Home Office.
5. Recibir devolución dañada: comprobar Servicio Técnico, y cerrar el servicio.
6. Simular QR roto, escribir `TAB-001` por teclado, observar estado actual e historial.

## Reglas importantes

El QR representa un **identificador y datos estáticos**, nunca el estado ni el empleado. Todo movimiento se guarda en una transacción SQLite con validación de estado condicional. La ubicación se deriva del único estado. Es un prototipo monodispositivo, **no** un sistema corporativo sincronizado.

## Fuentes técnicas

- Google Code Scanner: https://developers.google.com/ml-kit/vision/barcode-scanning/code-scanner
- Build Android: https://developer.android.com/build/releases/about-agp
