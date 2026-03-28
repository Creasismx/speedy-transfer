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
        print("Connected to server.")

        # 1. Check Nginx config
        _, out, _ = run_command(ssh, "cat /etc/nginx/sites-enabled/speedy")
        print("\n--- Nginx Config ---")
        print(out)

        # 2. Check directory structure
        _, out, _ = run_command(ssh, "ls -F /var/www/speedy-transfer/static/")
        print("\n--- Static Directory ---")
        print(out)

        _, out, _ = run_command(ssh, "ls -F /var/www/speedy-transfer/templates/assets/")
        print("\n--- Templates Assets Directory ---")
        print(out)

        # 3. Check where images are
        _, out, _ = run_command(ssh, "find /var/www/speedy-transfer -name 'Copia-de-logos-Mesa-de-trabajo-1-02.png'")
        print("\n--- Logo Location ---")
        print(out)

    finally:
        ssh.close()

if __name__ == "__main__":
    main()
