# ================================
#  Speedy Transfer – Setup Script
# ================================
Write-Host "Configurando entorno para Speedy Transfer..." -ForegroundColor Cyan

# Ruta del proyecto
$projectPath = "C:\Users\adolf\Documents\speedy-transfer"

# Ruta del venv global
$globalVenv = "C:\venvs\speedy-transfer"

# 1. Crear carpeta global para entornos (si no existe)
if (!(Test-Path "C:\venvs")) {
    Write-Host "Creando directorio global C:\venvs ..."
    New-Item -ItemType Directory -Path "C:\venvs" | Out-Null
}

# 2. Eliminar venv viejo dentro del proyecto
$oldVenv = Join-Path $projectPath "venv"
$oldVenv311 = Join-Path $projectPath "venv311"

if (Test-Path $oldVenv) {
    Write-Host "Eliminando entorno virtual viejo: venv ..."
    Remove-Item -Recurse -Force $oldVenv
}

if (Test-Path $oldVenv311) {
    Write-Host "Eliminando entorno virtual viejo: venv311 ..."
    Remove-Item -Recurse -Force $oldVenv311
}

# 3. Crear nuevo entorno virtual global
if (!(Test-Path $globalVenv)) {
    Write-Host "Creando nuevo entorno virtual global..."
    python -m venv $globalVenv
} else {
    Write-Host "El entorno virtual global ya existe."
}

# 4. Activar el entorno
Write-Host "Activando entorno virtual..."
& "$globalVenv\Scripts\activate"

# 5. Instalar dependencias del proyecto
$reqFile = Join-Path $projectPath "requirements.txt"

if (Test-Path $reqFile) {
    Write-Host "Instalando dependencias del proyecto..."
    pip install -r $reqFile
} else {
    Write-Host "No existe requirements.txt — instalando Django mínimo."
    pip install django
}

# 6. Crear carpeta locale si no existe
$localePath = Join-Path $projectPath "locale"
if (!(Test-Path $localePath)) {
    Write-Host "Creando carpeta locale..."
    New-Item -ItemType Directory -Path $localePath | Out-Null
}

# 7. Ejecutar makemessages
Write-Host "Generando archivos de traducción..."
Set-Location $projectPath
python manage.py makemessages -l en

Write-Host ""
Write-Host "PROCESO COMPLETO — Speedy Transfer está listo." -ForegroundColor Green
Write-Host "Puedes comenzar a trabajar con tranquilidad."
