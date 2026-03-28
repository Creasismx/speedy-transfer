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

        # Correcting the data via raw SQL
        sql_code = """
from django.db import connection
try:
    with connection.cursor() as cursor:
        # 1. Remove Zone 36 if it exists and is named AEROPUERTO
        cursor.execute("DELETE FROM core_zone WHERE name = 'AEROPUERTO' AND id != 0")
        print('Deleted redundant AEROPUERTO zones.')

        # 2. Force Zone ID 0
        cursor.execute("SELECT id FROM core_zone WHERE id = 0")
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO core_zone (id, name, description) VALUES (0, 'AEROPUERTO', 'AEROPUERTO')")
            print('Zone AEROPUERTO created with ID 0.')
        else:
            print('Zone AEROPUERTO already exists with ID 0.')

        # 3. Ensure Hotel ID 0 is linked correctly
        cursor.execute("UPDATE core_hotel SET zone_id = 0, name = 'AEROPUERTO' WHERE id = 0")
        print('Hotel ID 0 updated to point to Zone 0.')

        # 4. If Hotel 0 doesn't exist, create it
        cursor.execute("SELECT id FROM core_hotel WHERE id = 0")
        if not cursor.fetchone():
             cursor.execute("INSERT INTO core_hotel (id, name, description, zone_id) VALUES (0, 'AEROPUERTO', 'AEROPUERTO', 0)")
             print('Hotel AEROPUERTO created with ID 0.')

except Exception as e:
    print(f'Error: {e}')
"""
        stdin, stdout, stderr = ssh.exec_command("cat > /tmp/fix_airport_ids.py")
        stdin.write(sql_code)
        stdin.close()
        stdout.channel.recv_exit_status()

        status, out, err = run_command(ssh, "cd /var/www/speedy-transfer && /var/www/speedy-transfer/venv/bin/python manage.py shell < /tmp/fix_airport_ids.py")
        print("\n--- Command Output ---")
        print(out)
        
        # Clear cache again
        run_command(ssh, "systemctl restart speedy-daphne")

    finally:
        ssh.close()

if __name__ == "__main__":
    main()
