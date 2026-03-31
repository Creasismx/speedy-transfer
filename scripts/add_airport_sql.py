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

        # Use raw SQL to insert ID 0
        sql_code = """
from django.db import connection
try:
    with connection.cursor() as cursor:
        # Check if exists
        cursor.execute("SELECT id FROM core_zone WHERE id = 0")
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO core_zone (id, name, description) VALUES (0, 'AEROPUERTO', 'AEROPUERTO')")
            print('Zone AEROPUERTO created with ID 0.')
        else:
            print('Zone AEROPUERTO already exists with ID 0.')

        cursor.execute("SELECT id FROM core_hotel WHERE id = 0")
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO core_hotel (id, name, description, zone_id) VALUES (0, 'AEROPUERTO', 'AEROPUERTO', 0)")
            print('Hotel AEROPUERTO created with ID 0.')
        else:
            print('Hotel AEROPUERTO already exists with ID 0.')
except Exception as e:
    print(f'Error: {e}')
"""
        stdin, stdout, stderr = ssh.exec_command("cat > /tmp/add_airport_sql.py")
        stdin.write(sql_code)
        stdin.close()
        stdout.channel.recv_exit_status()

        status, out, err = run_command(ssh, "cd /var/www/speedy-transfer && /var/www/speedy-transfer/venv/bin/python manage.py shell < /tmp/add_airport_sql.py")
        print("\n--- Command Output ---")
        print(out)
        if err:
            print("\n--- Command Error ---")
            print(err)

    finally:
        ssh.close()

if __name__ == "__main__":
    main()
