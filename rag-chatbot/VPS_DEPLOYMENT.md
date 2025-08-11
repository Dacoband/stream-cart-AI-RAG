# VPS Deployment Guide cho StreamCart AI Service

## 1. Cài đặt Python và dependencies trên VPS

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
sudo apt install git nginx supervisor -y
```

## 2. Clone và setup project

```bash
# Clone project to VPS
git clone <your-repo-url> /opt/streamcart-ai
cd /opt/streamcart-ai/rag-chatbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 3. Tạo file .env cho production

```bash
# /opt/streamcart-ai/rag-chatbot/.env
GOOGLE_API_KEY=AIzaSyAL3vF8MEsu7uTL6VOdq0bFjsHYw0Fayzk
BACKEND_API_URL=https://brightpa.me
```

## 4. Nginx configuration

```nginx
# /etc/nginx/sites-available/streamcart-ai
server {
    listen 80;
    server_name your-vps-domain.com;  # Thay bằng domain VPS của bạn

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/streamcart-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 5. Supervisor configuration

```ini
# /etc/supervisor/conf.d/streamcart-ai.conf
[program:streamcart-ai]
command=/opt/streamcart-ai/rag-chatbot/venv/bin/python main.py
directory=/opt/streamcart-ai/rag-chatbot
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/streamcart-ai.err.log
stdout_logfile=/var/log/streamcart-ai.out.log
```

```bash
# Start service
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start streamcart-ai
```

## 6. Update Backend C# configuration

Update appsettings.json:
```json
{
  "AiService": {
    "BaseUrl": "http://your-vps-domain.com"
  }
}
```

## 7. Firewall và Security

```bash
# Open port 80 and 443
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## 8. SSL Certificate (Optional but recommended)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-vps-domain.com
```

## 9. Test deployment

```bash
# Test AI service
curl http://your-vps-domain.com/health

# Test chat endpoint
curl -X POST http://your-vps-domain.com/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "Có những sản phẩm gì"}'
```
