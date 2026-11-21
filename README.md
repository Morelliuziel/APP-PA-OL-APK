# Trabajo Práctico 2 — Pañol-App

**Escuela Técnica N.º 35 Ing. Eduardo Latzina · Desarrollo de Sistemas · 2026**

Sistema móvil de gestión y trazabilidad de tablets corporativas con lectura de códigos QR, estados exclusivos y persistencia local SQLite.

## Qué incluye esta entrega

- `android/` — proyecto Android nativo en Java con SQLite y Google Code Scanner (lector QR mediante cámara y alternativa de identificación manual).
- `.github/workflows/compilar-apk.yml` — compilación automática del APK con GitHub Actions. **Este es el workflow activo**, ubicado en la raíz del repositorio.
- `android/.github/workflows/compilar-apk.yml` — copia del workflow original dentro del proyecto Android; no es la que ejecuta GitHub Actions en este repositorio.
- `android/README_COMPILACION.md` — instrucciones adicionales para compilar e instalar en Android.
- `etiquetas/Etiquetas_QR_Imprimir_A4.pdf` — tres QR de ejemplo, con series TAB-001/002/003 y datos JSON, aptos para imprimir.
- `etiquetas/TAB-001.png`, `etiquetas/TAB-002.png`, `etiquetas/TAB-003.png` y los `.txt` correspondientes — códigos QR y su contenido literal.
- `pruebas/` — pruebas de reglas de negocio y validaciones de ejemplo.

> Los documentos originales de la entrega (carpeta técnica y guion de defensa) se distribuyeron por separado. Su presencia en el repositorio depende de que se hayan subido a GitHub.

## Estado verificado del proyecto

- **Pruebas previas:** 15 casos JVM del dominio, restricciones SQL y decodificación de tres imágenes QR, según el reporte incluido en `pruebas/`.
- **Compilación Android:** el workflow de GitHub Actions **#2 terminó correctamente** y publicó el artifact `panol-app-apk` con un APK debug instalable.
- **Pendiente de probar:** instalación y ejecución en un dispositivo Android físico, cámara, escaneo de códigos QR y recorrido completo de los préstamos/devoluciones.

**Evidencia de compilación exitosa:** [Compilar Pañol-App APK — ejecución #2](https://github.com/Morelliuziel/APP-PA-OL-APK/actions/runs/44841826021).

## Cómo descargar el APK compilado

1. Ingresar a [la ejecución exitosa #2 de GitHub Actions](https://github.com/Morelliuziel/APP-PA-OL-APK/actions/runs/44841826021) e iniciar sesión en GitHub si se solicita.
2. Ir hasta la sección **Artifacts** al final de la página.
3. Descargar **`panol-app-apk`**. GitHub entrega el artifact como archivo ZIP.
4. Descomprimir el ZIP para obtener **`panol-app.apk`**.
5. Transferir el APK al celular Android, si todavía no se descargó allí.
6. Abrirlo desde Archivos/Descargas y autorizar la instalación desde esa fuente si Android la solicita. Una vez instalado, abrir **Pañol-App**.

> El APK generado con `assembleDebug` es una **compilación de prueba (debug)**, no una versión de publicación para Google Play. La compilación correcta no sustituye las pruebas en un celular real.

## Cómo volver a compilar sin Android Studio

El repositorio incluye un workflow listo para construir el APK en los servidores de GitHub.

1. Abrir la pestaña [**Actions**](https://github.com/Morelliuziel/APP-PA-OL-APK/actions).
2. En la barra lateral, seleccionar **Compilar Pañol-App APK**.
3. Elegir **Run workflow**, mantener la rama `main` y confirmar.
4. Abrir la nueva ejecución y comprobar que termine con el ícono verde de éxito.
5. Descargar el artifact **`panol-app-apk`** siguiendo los pasos anteriores.

El workflow también se dispara con cada `push` a `main`, incluido un cambio del README. Su configuración activa está en [`.github/workflows/compilar-apk.yml`](https://github.com/Morelliuziel/APP-PA-OL-APK/blob/main/.github/workflows/compilar-apk.yml).

**Detalles técnicos de la compilación automática:**

- Sistema de construcción: GitHub Actions sobre `ubuntu-latest`.
- Java: Temurin JDK 17.
- Preparación de Android: `android-actions/setup-android@v4` e instalación del SDK Android 35.
- Gradle: 8.13.
- Compilación desde la raíz del repositorio: `gradle -p android :app:assembleDebug`.
- Archivo original generado: `android/app/build/outputs/apk/debug/app-debug.apk`.
- Renombrado: `panol-app.apk` y publicación con `actions/upload-artifact@v4`.

### Incidente y solución registrados

- **Ejecución #1:** falló durante `android-actions/setup-android@v3` con `Warning: Failed to find package 'tools'`. No se llegó a compilar el código Android.
- **Corrección:** se actualizó la acción de preparación de Android a `android-actions/setup-android@v4`.
- **Ejecución #2:** finalizó exitosamente y publicó el artifact `panol-app-apk`.

En caso de otro fallo, abrir la ejecución fallida, seleccionar el trabajo **build**, localizar el paso que falló y leer las líneas de error. No hace falta volver a subir todo el proyecto para modificar el workflow.

## Uso funcional propuesto para la demostración

1. Escanear físicamente TAB-001 desde `etiquetas/Etiquetas_QR_Imprimir_A4.pdf`.
2. Confirmar el alta y examinar la ficha y el historial.
3. Intentar despachar para Home Office sin tarea para comprobar el bloqueo visual; después ingresar legajo `EMP-123` y tarea `TSK-100`.
4. Volver a leer la etiqueta para comprobar el estado de uso externo.
5. Registrar una devolución dañada y verificar el paso a Servicio Técnico.
6. Simular un QR ilegible: ingresar `TAB-001` mediante el teclado y consultar su estado e historial.

Estos pasos son un **guion de pruebas a realizar en el dispositivo**, no una afirmación de que ya se ejecutaron en un Android real.

## Reglas importantes

El QR representa un **identificador y datos estáticos**, no el estado vigente ni el empleado. Cada movimiento se registra en SQLite, con comprobación de las transiciones de estado. La ubicación se deriva del estado exclusivo del dispositivo. Esta implementación funciona como **prototipo local monodispositivo**; no ofrece sincronización entre varios celulares.

## Referencias técnicas

- [Google Code Scanner](https://developers.google.com/ml-kit/vision/barcode-scanning/code-scanner)
- [Compilación Android / Android Gradle Plugin](https://developer.android.com/build/releases/about-agp)
- [GitHub Actions: artifacts](https://docs.github.com/en/actions/tutorials/store-and-share-data)
