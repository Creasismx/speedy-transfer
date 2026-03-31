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

        # Updated Nginx config
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
        alias /var/www/speedy-transfer/static/;
    }

    location /assets/ {
        alias /var/www/speedy-transfer/templates/assets/;
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
        # Save to temp file on server and move to nginx
        # We'll use a safer way: echo 'conf' > /etc/nginx/sites-available/speedy
        # Use a heredoc for complex strings
        stdin, stdout, stderr = ssh.exec_command("cat > /etc/nginx/sites-available/speedy")
        stdin.write(nginx_conf)
        stdin.close()
        stdout.channel.recv_exit_status()
        
        # Test and reload
        run_command(ssh, "nginx -t")
        run_command(ssh, "systemctl reload nginx")
        print("Nginx configuration updated and reloaded.")

    finally:
        ssh.close()

if __name__ == "__main__":
    main()
