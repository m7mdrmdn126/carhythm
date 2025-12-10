# CaRhythm Story Mode - Deployment Guide

Complete guide for deploying the CaRhythm Story Mode assessment to production.

## 🏗️ Architecture Overview

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   Frontend  │────────▶│   Backend    │────────▶│   Database   │
│  (React)    │  HTTP   │  (FastAPI)   │  SQL    │  (SQLite)    │
│  Port 5173  │         │  Port 8000   │         │              │
└─────────────┘         └──────────────┘         └──────────────┘
```

## 🚀 Quick Deployment

### Option 1: Single Server (Recommended for Small Scale)

Deploy both frontend and backend on one server using nginx as reverse proxy.

**Requirements:**
- Ubuntu 20.04+ or similar Linux
- 2GB RAM minimum
- Python 3.9+
- Node.js 18+
- nginx

**Steps:**

1. **Setup Server**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nodejs npm nginx
```

2. **Deploy Backend**
```bash
# Clone repository
git clone https://github.com/m7mdrmdn126/carhythm.git
cd carhythm

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migration
python migrate_story_mode.py

# Create systemd service
sudo nano /etc/systemd/system/carhythm-api.service
```

**Service file content:**
```ini
[Unit]
Description=CaRhythm API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/carhythm
Environment="PATH=/var/www/carhythm/.venv/bin"
ExecStart=/var/www/carhythm/.venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable carhythm-api
sudo systemctl start carhythm-api
```

3. **Deploy Frontend**
```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Copy build to nginx
sudo cp -r dist/* /var/www/carhythm-frontend/
```

4. **Configure nginx**
```bash
sudo nano /etc/nginx/sites-available/carhythm
```

**nginx config:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /var/www/carhythm-frontend;
        try_files $uri $uri/ /index.html;
        
        # Enable gzip
        gzip on;
        gzip_types text/css application/javascript application/json;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Admin panel
    location /admin/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Static files
    location /static/ {
        alias /var/www/carhythm/app/static/;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/carhythm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

5. **Setup SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Option 2: Separate Deployment (Scalable)

Deploy frontend and backend separately for better scalability.

**Frontend → Vercel/Netlify**
**Backend → DigitalOcean/AWS**

#### Deploy Frontend to Vercel

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Configure Environment**
```bash
cd frontend
echo "VITE_API_BASE_URL=https://api.your-domain.com" > .env.production
```

3. **Deploy**
```bash
vercel --prod
```

#### Deploy Backend to DigitalOcean

1. **Create Droplet** (Ubuntu 20.04, 2GB RAM)

2. **Setup Backend** (same as Option 1, steps 1-2)

3. **Configure Domain**
- Point `api.your-domain.com` to droplet IP
- Setup SSL with certbot

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
DATABASE_URL=sqlite:///./career_dna.db
SECRET_KEY=your-secret-key-change-this-in-production
CORS_ORIGINS=https://your-frontend-domain.com
DEBUG=False
```

**Frontend (.env.production):**
```env
VITE_API_BASE_URL=https://api.your-domain.com
```

### Database Setup

**Development (SQLite):**
```bash
python migrate_story_mode.py
python populate_db.py  # Optional: seed data
```

**Production (PostgreSQL - Optional):**
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb carhythm

# Update .env
DATABASE_URL=postgresql://user:password@localhost/carhythm

# Run migrations
python migrate_story_mode.py
```

## 📊 Monitoring

### Backend Health Check
```bash
curl https://api.your-domain.com/api/v2/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

### Frontend Check
```bash
curl -I https://your-domain.com
```

Should return `200 OK`

### Log Monitoring

**Backend logs:**
```bash
sudo journalctl -u carhythm-api -f
```

**nginx logs:**
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🔒 Security

### Backend Security

1. **Change default secrets**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Enable HTTPS only**
```python
# In main.py
app.add_middleware(
    HTTPSRedirectMiddleware
)
```

3. **Rate limiting**
```bash
pip install slowapi
```

4. **CORS configuration**
```python
# Only allow your frontend domain
CORS_ORIGINS = ["https://your-domain.com"]
```

### Frontend Security

1. **Content Security Policy**
```html
<!-- In index.html -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';">
```

2. **Environment variables**
- Never commit `.env` files
- Use build-time variables only

## 📈 Performance Optimization

### Frontend

1. **Enable compression**
```bash
# nginx already configured with gzip
```

2. **Asset optimization**
```bash
# Optimize images
npm install -D vite-plugin-imagemin
```

3. **Code splitting**
```javascript
// Already handled by Vite
```

### Backend

1. **Database indexing**
```sql
CREATE INDEX idx_question_page_id ON questions(page_id);
CREATE INDEX idx_response_session ON responses(session_id);
```

2. **Caching**
```bash
pip install redis
```

3. **Connection pooling**
```python
# In database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40
)
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: cd frontend && npm install
      - run: cd frontend && npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          deploy_key: ${{ secrets.DEPLOY_KEY }}
          publish_dir: ./frontend/dist

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /var/www/carhythm
            git pull
            source .venv/bin/activate
            pip install -r requirements.txt
            sudo systemctl restart carhythm-api
```

## 🆘 Troubleshooting

### Frontend not connecting to API
- Check CORS configuration in backend
- Verify `VITE_API_BASE_URL` is correct
- Test API directly: `curl https://api.your-domain.com/api/v2/health`

### Backend 502 Bad Gateway
- Check if backend service is running: `sudo systemctl status carhythm-api`
- Check logs: `sudo journalctl -u carhythm-api -n 50`
- Verify port 8000 is not blocked

### Database errors
- Check file permissions: `ls -la career_dna.db`
- Verify migrations ran: `python migrate_story_mode.py`
- Check disk space: `df -h`

### SSL certificate issues
- Renew certificate: `sudo certbot renew`
- Check expiration: `sudo certbot certificates`

## 📞 Support

For deployment assistance:
- GitHub Issues: https://github.com/m7mdrmdn126/carhythm/issues
- Email: support@carhythm.com

## 📋 Deployment Checklist

- [ ] Server provisioned and secured
- [ ] Backend dependencies installed
- [ ] Database migrated
- [ ] Backend service running
- [ ] Frontend built and deployed
- [ ] nginx configured
- [ ] SSL certificate installed
- [ ] Domain DNS configured
- [ ] Environment variables set
- [ ] CORS configured
- [ ] Health checks passing
- [ ] Monitoring setup
- [ ] Backups configured
- [ ] Admin account created
- [ ] Test assessment completed

---

**Last Updated**: November 2025  
**Version**: 2.0.0
