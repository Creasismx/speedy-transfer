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

        # 1. Check Nginx error logs
        _, out, _ = run_command(ssh, "tail -n 20 /var/log/nginx/error.log")
        print("\n--- Nginx Error Log ---")
        print(out)

        # 2. Check permissions
        _, out, _ = run_command(ssh, "ls -ld /var/www/speedy-transfer/templates/assets/images/")
        print("\n--- Images Directory Permissions ---")
        print(out)

        _, out, _ = run_command(ssh, "ls -l /var/www/speedy-transfer/templates/assets/images/Copia-de-logos-Mesa-de-trabajo-1-02.png")
        print("\n--- Logo File Permissions ---")
        print(out)

        # 3. Try to fix permissions just in case
        run_command(ssh, "chown -R www-data:www-data /var/www/speedy-transfer/")
        run_command(ssh, "chmod -R 755 /var/www/speedy-transfer/")
        print("\nPermissions reset to www-data:www-data 755.")

    finally:
        ssh.close()

if __name__ == "__main__":
    main()
