# Pañol-App — compilación e instalación Android

## Requisitos

- Android Studio con JDK 17 compatible y Android SDK Platform 35.
- Para la configuración incluida: Android Gradle Plugin 8.13.0, Gradle 8.13 y Build Tools compatibles.
- Conexión a Internet para descargar dependencias durante la primera sincronización.
- Celular real con Android 6.0 (API 23) o posterior, cámara, Servicios de Google Play actualizados, y conexión inicial a Internet para descargar el módulo de escaneo Google Code Scanner (puede quedar cacheado luego).
- Este proyecto **no usa permiso CAMERA**: Google Play services administra la UI del lector y retorna el texto del QR.

## Abrir y compilar en Android Studio

1. Instalar Android Studio desde https://developer.android.com/studio y configurar Android SDK 35 en Tools > SDK Manager.
2. En Android Studio, seleccionar **Open** y elegir la carpeta `android/` (donde está `settings.gradle`).
3. Si Android Studio pregunta por Gradle, seleccionar/instalar **Gradle 8.13**. No se distribuye `gradle-wrapper.jar` porque no se pudo descargar en el entorno de generación; si se dispone de una instalación local de Gradle se puede crear con `gradle wrapper --gradle-version 8.13` dentro de `android/`.
4. Esperar `Sync Project with Gradle Files` (requiere Internet); permitir la descarga de la dependencia `play-services-code-scanner:16.1.0`.
5. Elegir **Build > Build Bundle(s) / APK(s) > Build APK(s)** (o ejecutar `gradle :app:assembleDebug` desde terminal con Gradle 8.13 instalado).
6. Localizar `android/app/build/outputs/apk/debug/app-debug.apk`.
7. Renombrar o copiar el APK resultante a **`pañol-app.apk`** (nombre de entrega; no modifica el identificador del paquete):
   - macOS/Linux: `cp app/build/outputs/apk/debug/app-debug.apk "pañol-app.apk"`
   - Windows PowerShell: `Copy-Item app\build\outputs\apk\debug\app-debug.apk "pañol-app.apk"`
8. El APK de variante **debug ya queda firmado** con la clave de depuración del entorno, y se puede instalar para pruebas; no es una firma apta para distribución pública.

## Instalación física

- Método A (USB): activar opciones de desarrollador y depuración USB; verificar `adb devices`; ejecutar `adb install -r "pañol-app.apk"`.
- Método B (archivo): transferir `pañol-app.apk` por USB, Drive o mensajería; abrirlo desde el administrador de archivos y permitir al instalador correspondiente **Instalar apps desconocidas** cuando Android lo solicite. Volver a desactivar esa autorización si no se necesita.
- Ejecutar la app; presionar **Escanear QR con la cámara** y apuntar a las etiquetas impresas de `etiquetas/Etiquetas_QR_Imprimir_A4.pdf`. Si el scanner requiere descargar el módulo, conectarse a Internet y reintentar.
- La primera lectura de `TAB-001` abre una vista previa; **Confirmar alta**. Volver a escanear para ver la ficha; despachar e ingresar legajo y tarea, luego devolverla. Las otras dos etiquetas permiten probar múltiples equipos.

## Plan alternativo sin acceso al escáner

Usar **Ingresar QR o serie por teclado**. Se puede pegar el JSON literal desde `etiquetas/TAB-001.txt` para registrar una tablet nueva o escribir `TAB-001` para consultar una ya registrada.

## Restricciones honestas

- Sin un SDK de Android y Gradle disponibles, el entorno donde se preparó la entrega no pudo ejecutar `assembleDebug` ni realizar pruebas en dispositivos reales. **Este repositorio contiene el código fuente y la configuración de compilación; no incluye un APK precompilado**.
- Google Code Scanner requiere Google Play Services; no se garantiza en dispositivos Android sin servicios de Google. El ingreso manual sigue funcionando en esos dispositivos.
- Los datos quedan en SQLite **en ese celular**, sin sincronización multiusuario. No se implementan autenticación, inventario compartido entre terminales ni respaldo remoto.
