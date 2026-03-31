import paramiko
import time

HOST = '145.223.120.195'
USER = 'root'
PASS = 'YEJ+o.77SasiG(Pj'

def run_command(ssh, command):
    print(f"Executing: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(f"STDOUT: {out}")
    if err: print(f"STDERR: {err}")
    return exit_status, out, err

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        print("Connected to server.")

        # 1. Update apt and install certbot
        run_command(ssh, "apt-get update")
        run_command(ssh, "apt-get install -y certbot python3-certbot-nginx")

        # 2. Run certbot
        # We use --register-unsafely-without-email to avoid asking for email in non-interactive mode
        # or we could use a dummy email.
        cert_cmd = "certbot --nginx -d speedyvallarta.com -d www.speedyvallarta.com --non-interactive --agree-tos --register-unsafely-without-email --redirect"
        status, out, err = run_command(ssh, cert_cmd)
        
        if status == 0:
            print("SSL Certificate installed successfully!")
        else:
            print(f"Failed to install SSL Certificate. Status: {status}")

    finally:
        ssh.close()

if __name__ == "__main__":
    main()
