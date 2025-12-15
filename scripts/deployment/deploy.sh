#!/bin/bash

# Remote server details
REMOTE_HOST="45.82.72.136"
REMOTE_USER="root"
DEPLOY_DIR="/var/www/speedy-transfer"
VENV_DIR="$DEPLOY_DIR/venv"

# Ensure the remote directory exists
ssh $REMOTE_USER@$REMOTE_HOST "mkdir -p $DEPLOY_DIR"

# Copy project files
echo "Copying project files..."
rsync -avz --exclude 'venv*' --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' ./ $REMOTE_USER@$REMOTE_HOST:$DEPLOY_DIR/

# Setup commands to run on the remote server
ssh $REMOTE_USER@$REMOTE_HOST "bash -s" << 'EOF'
    # Navigate to project directory
    cd /var/www/speedy-transfer

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
WorkingDirectory=/var/www/speedy-transfer
Environment="PATH=/var/www/speedy-transfer/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings.production"
ExecStart=/var/www/speedy-transfer/venv/bin/daphne -b 0.0.0.0 -p 8000 config.asgi:application

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

EOF

echo "Deployment completed!"