#!/bin/bash
set -e

echo "🚀 CaRhythm Deployment Script"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_USER="carhythm"
APP_DIR="/home/$APP_USER/carhythm"
DOMAIN="145.14.158.174"  # Update with your domain if you have one

echo -e "${YELLOW}Step 1: Updating system packages...${NC}"
apt update && apt upgrade -y

echo -e "${YELLOW}Step 2: Installing required packages...${NC}"
apt install -y python3 python3-pip python3-venv nginx git curl wget ufw

echo -e "${YELLOW}Step 3: Installing Node.js 20.x...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

echo -e "${YELLOW}Step 4: Creating application user...${NC}"
if id "$APP_USER" &>/dev/null; then
    echo "User $APP_USER already exists"
else
    adduser $APP_USER --disabled-password --gecos ""
    echo -e "${GREEN}User $APP_USER created${NC}"
fi

echo -e "${YELLOW}Step 5: Cloning/Updating repository...${NC}"
if [ -d "$APP_DIR" ]; then
    echo "Directory exists, pulling latest changes..."
    cd $APP_DIR
    sudo -u $APP_USER git pull origin main
else
    echo "Cloning repository..."
    sudo -u $APP_USER git clone https://github.com/m7mdrmdn126/carhythm.git $APP_DIR
fi

cd $APP_DIR

echo -e "${YELLOW}Step 6: Setting up Python environment...${NC}"
sudo -u $APP_USER python3 -m venv venv
sudo -u $APP_USER $APP_DIR/venv/bin/pip install --upgrade pip
sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r requirements.txt

echo -e "${YELLOW}Step 7: Setting up environment variables...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    echo "Creating .env file..."
    cat > $APP_DIR/.env << 'EOF'
# EMAIL CONFIGURATION
SMTP_USER=your-gmail@gmail.com
SMTP_PASSWORD=your-gmail-app-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=CaRhythm Team

# ADMIN NOTIFICATIONS
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_NAME=CaRhythm Admin

# APPLICATION SETTINGS
APP_URL=http://145.14.158.174
ENABLE_EMAIL=true

# SECURITY
SECRET_KEY=CHANGE_THIS_TO_RANDOM_STRING
ADMIN_USERNAME=admin
ADMIN_PASSWORD=CHANGE_THIS_PASSWORD

# OPTIONAL
PDF_TEMPLATE_VERSION=v2
PREMIUM_CHECKOUT_URL=http://145.14.158.174/premium
EOF
    chown $APP_USER:$APP_USER $APP_DIR/.env
    echo -e "${RED}⚠️  IMPORTANT: Edit $APP_DIR/.env with your actual values!${NC}"
    echo -e "${RED}   Run: nano $APP_DIR/.env${NC}"
else
    echo ".env file already exists"
fi

echo -e "${YELLOW}Step 8: Setting up backend systemd service...${NC}"
cat > /etc/systemd/system/carhythm-backend.service << EOF
[Unit]
Description=CaRhythm Backend FastAPI Application
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${YELLOW}Step 9: Setting up frontend...${NC}"
cd $APP_DIR/frontend

# Create frontend environment file
cat > .env.production << EOF
VITE_API_URL=http://$DOMAIN/api
EOF

echo "Installing frontend dependencies..."
sudo -u $APP_USER npm install

echo "Building frontend..."
sudo -u $APP_USER npm run build

echo -e "${YELLOW}Step 10: Configuring Nginx...${NC}"
cat > /etc/nginx/sites-available/carhythm << 'NGINXCONF'
# Backend API Server
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name 145.14.158.174;
    
    client_max_body_size 20M;
    
    # Frontend (React App)
    location / {
        root /home/carhythm/carhythm/frontend/dist;
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "public, max-age=3600";
    }
    
    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Backend Admin Panel
    location /admin {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Backend Static Files
    location /static {
        alias /home/carhythm/carhythm/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Backend Docs
    location /docs {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
NGINXCONF

# Enable site
ln -sf /etc/nginx/sites-available/carhythm /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo "Testing Nginx configuration..."
nginx -t

echo -e "${YELLOW}Step 11: Setting up firewall...${NC}"
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable

echo -e "${YELLOW}Step 12: Setting permissions...${NC}"
chown -R $APP_USER:$APP_USER $APP_DIR
chmod -R 755 $APP_DIR

echo -e "${YELLOW}Step 13: Starting services...${NC}"
systemctl daemon-reload
systemctl enable carhythm-backend
systemctl start carhythm-backend
systemctl restart nginx

echo ""
echo -e "${GREEN}=============================="
echo "🎉 Deployment Complete!"
echo "==============================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Edit environment file: nano $APP_DIR/.env"
echo "2. Update the following in .env:"
echo "   - SMTP_USER and SMTP_PASSWORD (for email)"
echo "   - SECRET_KEY (generate with: python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
echo "   - ADMIN_PASSWORD"
echo ""
echo "3. After editing .env, restart the backend:"
echo "   systemctl restart carhythm-backend"
echo ""
echo -e "${YELLOW}Check Service Status:${NC}"
echo "   systemctl status carhythm-backend"
echo "   systemctl status nginx"
echo ""
echo -e "${YELLOW}View Logs:${NC}"
echo "   journalctl -u carhythm-backend -f"
echo "   tail -f /var/log/nginx/access.log"
echo ""
echo -e "${GREEN}Access Your Application:${NC}"
echo "   Frontend: http://145.14.158.174"
echo "   Admin Panel: http://145.14.158.174/admin"
echo "   API Docs: http://145.14.158.174/docs"
echo ""
