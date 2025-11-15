import paramiko
import os
import sys
from pathlib import Path

# SSH Configuration
HOST = '45.82.72.136'
USERNAME = 'root'
PASSWORD = '*Adolfo1971*#2013$20'
REMOTE_DIR = '/var/www/speedy-transfer'

def upload_file(sftp, local_path, remote_path):
    print(f"Uploading: {local_path} -> {remote_path}")
    sftp.put(local_path, remote_path)

def deploy():
    print(f"Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("Connected successfully!")

        # Create remote directory
        print("Creating remote directory...")
        stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {REMOTE_DIR}")
        stdout.channel.recv_exit_status()  # Wait for command to complete

        # Get SFTP client
        sftp = ssh.open_sftp()

        print("Preparing files...")
        local_dir = Path('.')
        exclude = {'.git', '__pycache__', 'venv', '.pytest_cache'}

        print("Uploading files...")
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in exclude]
            
            for file in files:
                if not any(x in root for x in exclude):
                    local_path = os.path.join(root, file)
                    remote_path = f"{REMOTE_DIR}/{local_path.replace(os.sep, '/')}"
                    remote_dir = os.path.dirname(remote_path)
                    
                    # Create remote directory if it doesn't exist
                    try:
                        sftp.stat(remote_dir)
                    except FileNotFoundError:
                        ssh.exec_command(f"mkdir -p {remote_dir}")
                    
                    upload_file(sftp, local_path, remote_path)

        print("Setting up virtual environment and installing dependencies...")
        commands = [
            f"cd {REMOTE_DIR}",
            "python3 -m venv venv",
            "source venv/bin/activate",
            "pip install --upgrade pip",
            "pip install -r requirements.txt"
        ]
        ssh.exec_command(" && ".join(commands))

        # Create and setup systemd service
        service_config = f"""[Unit]
Description=Speedy Transfer Django Application
After=network.target

[Service]
User=root
Group=root
WorkingDirectory={REMOTE_DIR}
Environment="PATH={REMOTE_DIR}/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings.production"
ExecStart={REMOTE_DIR}/venv/bin/daphne -b 0.0.0.0 -p 8000 config.asgi:application

[Install]
WantedBy=multi-user.target
"""
        
        print("Starting application setup...")
        commands = [
            f'echo "{service_config}" > /etc/systemd/system/speedy.service',
            "systemctl daemon-reload",
            "systemctl enable speedy",
            "systemctl restart speedy",
            f"cd {REMOTE_DIR}",
            "source venv/bin/activate",
            "python manage.py collectstatic --noinput",
            "python manage.py migrate --noinput"
        ]
        
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.channel.recv_exit_status()

        print("Deployment completed successfully!")

    except Exception as e:
        print(f"Error during deployment: {e}")
        sys.exit(1)
    finally:
        ssh.close()

if __name__ == '__main__':
    deploy()