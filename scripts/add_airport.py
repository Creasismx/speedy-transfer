import paramiko

HOST = '145.223.120.195'
USER = 'root'
PASS = 'YEJ+o.77SasiG(Pj'

def run_command(ssh, command):
    print(f"Executing: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    return exit_status, out, err

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        print("Connected.")

        # Create the Airport Zone and Hotel using Django shell
        # We use a heredoc to pass the python code to manage.py shell
        # We use update_or_create to be idempotent
        django_code = """
from speedy_app.core.models import Zone, Hotel
try:
    zone, created = Zone.objects.update_or_create(
        id=0, 
        defaults={'name': 'AEROPUERTO', 'description': 'AEROPUERTO'}
    )
    print(f'Zone AEROPUERTO {"created" if created else "updated"}. ID: {zone.id}')
    
    hotel, h_created = Hotel.objects.update_or_create(
        id=0,
        defaults={'name': 'AEROPUERTO', 'zone': zone, 'description': 'AEROPUERTO'}
    )
    print(f'Hotel AEROPUERTO {"created" if h_created else "updated"}. ID: {hotel.id}')
except Exception as e:
    print(f'Error: {e}')
"""
        cmd = f"cd /var/www/speedy-transfer && /var/www/speedy-transfer/venv/bin/python manage.py shell -c \"{django_code}\""
        
        # We need to escape double quotes for the shell command
        # Let's use a simpler approach: write a temporary script on the server
        stdin, stdout, stderr = ssh.exec_command("cat > /tmp/add_airport.py")
        stdin.write(django_code)
        stdin.close()
        stdout.channel.recv_exit_status()

        status, out, err = run_command(ssh, "cd /var/www/speedy-transfer && /var/www/speedy-transfer/venv/bin/python manage.py shell < /tmp/add_airport.py")
        print("\n--- Command Output ---")
        print(out)
        if err:
            print("\n--- Command Error ---")
            print(err)

    finally:
        ssh.close()

if __name__ == "__main__":
    main()
