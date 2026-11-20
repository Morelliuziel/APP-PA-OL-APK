$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Get-Command gradle -ErrorAction SilentlyContinue)) {
    throw 'Gradle 8.13 no está en PATH. Leer README_COMPILACION.md.'
}
gradle :app:assembleDebug
if ($LASTEXITCODE -ne 0) { throw "Falló Gradle con salida $LASTEXITCODE" }
Copy-Item 'app\build\outputs\apk\debug\app-debug.apk' 'pañol-app.apk'
Write-Output 'APK creado: pañol-app.apk'
