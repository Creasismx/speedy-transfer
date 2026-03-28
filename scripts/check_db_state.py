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

        # Check the data
        django_code = """
from speedy_app.core.models import Zone, Hotel
zones = Zone.objects.all().order_by('id')
print("--- ZONES ---")
for z in zones:
    print(f"ID: {z.id}, Name: {z.name}")

hotels = Hotel.objects.all().order_by('zone_id', 'id')
print("\\n--- HOTELS (Top 10) ---")
for h in hotels[:10]:
    print(f"ID: {h.id}, Name: {h.name}, Zone: {h.zone_id}")

# Check specifically for Airport
try:
    airport_zone = Zone.objects.get(id=0)
    print(f"\\nAirport Zone: {airport_zone.name}")
except Zone.DoesNotExist:
    print("\\nAirport Zone NOT FOUND")

try:
    airport_hotel = Hotel.objects.get(id=0)
    print(f"Airport Hotel: {airport_hotel.name}, Zone: {airport_hotel.zone_id}")
except Hotel.DoesNotExist:
    print("Airport Hotel NOT FOUND")
"""
        stdin, stdout, stderr = ssh.exec_command("cat > /tmp/check_db.py")
        stdin.write(django_code)
        stdin.close()
        stdout.channel.recv_exit_status()

        status, out, err = run_command(ssh, "cd /var/www/speedy-transfer && /var/www/speedy-transfer/venv/bin/python manage.py shell < /tmp/check_db.py")
        print("\n--- Command Output ---")
        print(out)

        # Clear cache
        run_command(ssh, "systemctl restart speedy-daphne")
        print("\nApplication restarted (to clear any in-memory cache).")

    finally:
        ssh.close()

if __name__ == "__main__":
    main()
