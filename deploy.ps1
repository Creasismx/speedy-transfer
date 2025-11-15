# PowerShell deployment script

# Remote server details
$REMOTE_HOST = "45.82.72.136"
$REMOTE_USER = "root"
$DEPLOY_DIR = "/var/www/speedy-transfer"
$VENV_DIR = "$DEPLOY_DIR/venv"

Write-Host "Starting deployment..."

# First, let's create a deployment package
$tempDir = Join-Path $env:TEMP "deploy-pkg"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

# Copy project files to temp directory, excluding unnecessary files
$excludeList = @("venv*", ".git", "__pycache__", "*.pyc")
Get-ChildItem -Path . -Exclude $excludeList | Copy-Item -Destination $tempDir -Recurse -Force

# Create the remote setup script
@"
#!/bin/bash
set -e

cd $DEPLOY_DIR

# Install system dependencies
apt-get update
apt-get install -y python3-venv python3-dev

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service file
cat > /etc/systemd/system/speedy.service << 'EOL'
[Unit]
Description=Speedy Transfer Daphne Service
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=$DEPLOY_DIR
Environment="PATH=$DEPLOY_DIR/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings.production"
ExecStart=$DEPLOY_DIR/venv/bin/daphne -b 0.0.0.0 -p 8000 config.asgi:application

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and start service
systemctl daemon-reload
systemctl enable speedy
systemctl restart speedy

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput

echo "Setup completed!"
"@ | Set-Content -Path "$tempDir/setup.sh" -Encoding UTF8

# Use PSCP (PuTTY) to copy files
Write-Host "Copying files to server..."
& pscp -r "$tempDir\*" "${REMOTE_USER}@${REMOTE_HOST}:$DEPLOY_DIR/"

# Use Plink (PuTTY) to execute remote commands
Write-Host "Running remote setup..."
& plink ${REMOTE_USER}@${REMOTE_HOST} "chmod +x $DEPLOY_DIR/setup.sh && $DEPLOY_DIR/setup.sh"

# Clean up
Remove-Item -Path $tempDir -Recurse -Force

Write-Host "Deployment completed!"