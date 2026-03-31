import paramiko

HOST = '145.223.120.195'
USER = 'root'
PASS = 'YEJ+o.77SasiG(Pj'

def run_command(ssh, command):
    print(f"Executing: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return exit_status, out

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        print("Connected.")

        # List all files in assets/images/ recursively
        _, out = run_command(ssh, "find /var/www/speedy-transfer/templates/assets/images/ -type f")
        print("\n--- Remote Image Files ---")
        print(out)

    finally:
        ssh.close()

if __name__ == "__main__":
    main()
