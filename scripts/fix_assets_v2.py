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

        # Using root instead of alias can be more reliable
        # For /assets/, if we use root /var/www/speedy-transfer/templates, 
        # then /assets/images/logo.png -> /var/www/speedy-transfer/templates/assets/images/logo.png
        # For /static/, we can use root /var/www/speedy-transfer; 
        # then /static/images/... -> /var/www/speedy-transfer/static/images/...

        nginx_conf = """server {
    server_name speedyvallarta.com www.speedyvallarta.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        root /var/www/speedy-transfer;
    }

    location /assets/ {
        root /var/www/speedy-transfer/templates;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/speedyvallarta.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/speedyvallarta.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

server {
    if ($host = www.speedyvallarta.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    if ($host = speedyvallarta.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    listen 80;
    server_name speedyvallarta.com www.speedyvallarta.com;
    return 404; # managed by Certbot
}
"""
        stdin, stdout, stderr = ssh.exec_command("cat > /etc/nginx/sites-available/speedy")
        stdin.write(nginx_conf)
        stdin.close()
        stdout.channel.recv_exit_status()
        
        run_command(ssh, "nginx -t")
        run_command(ssh, "systemctl reload nginx")
        print("Nginx updated with root directive.")

    finally:
        ssh.close()

if __name__ == "__main__":
    main()
