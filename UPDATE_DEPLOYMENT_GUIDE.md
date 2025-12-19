# 🚀 CaRhythm Server Update Guide
**Deploying Latest Changes to Hostinger VPS**

---

## 📋 What's Being Updated

### New Features:
1. ✅ **Module Introduction Screens** - Gamified intro before each assessment module
2. ✅ **Module Completion Celebrations** - Confetti & stats when finishing modules
3. ✅ **Module Indicators** - Color-coded badges showing current chapter
4. ✅ **Feedback System** - User feedback collection after assessment
5. ✅ **UI Improvements** - Responsive design, numbered answers, gradient styling
6. ✅ **Database Updates** - Module metadata (colors, descriptions, emojis)

### Files Changed:
- **Backend:** 23 files (models, routers, templates)
- **Frontend:** 15 files (new pages, updated components)
- **Database:** Schema updates + new data

---

## 🔄 Step-by-Step Update Process

### **STEP 1: Commit & Push Changes to GitHub**

```bash
# Navigate to project directory
cd /media/mohamedramadan/work/Carhythm/carhythm

# Add all changes
git add .

# Commit with descriptive message
git commit -m "feat: Add module intro screens, completion celebrations, and feedback system

- Add ModuleIntro and ModuleCompletion pages with animations
- Add module badges and color theming to Question page  
- Update database schema with module metadata (colors, descriptions)
- Add feedback system with rating and text fields
- Improve UI responsiveness and styling
- Update navigation flow through module intro screens"

# Push to GitHub
git push origin main
```

**✅ Verify:** Check https://github.com/m7mdrmdn126/carhythm to confirm changes are pushed

---

### **STEP 2: SSH into Your VPS**

```bash
ssh root@145.14.158.174
# Or if using a different user:
# ssh your-username@145.14.158.174
```

---

### **STEP 3: Navigate to Application Directory**

```bash
cd /home/carhythm/carhythm
# Or wherever your app is deployed (common locations):
# cd /var/www/carhythm
# cd /opt/carhythm
```

---

### **STEP 4: Backup Current Setup**

```bash
# Backup database
cp career_dna.db career_dna.db.backup_$(date +%Y%m%d_%H%M%S)

# Backup entire app (optional but recommended)
cd ..
tar -czf carhythm_backup_$(date +%Y%m%d_%H%M%S).tar.gz carhythm/
cd carhythm
```

**✅ Verify:** `ls -lh *.backup*` should show your backup file

---

### **STEP 5: Pull Latest Code from GitHub**

```bash
# Stash any local changes (if any)
git stash

# Pull latest changes
git pull origin main

# If you had local changes, you can restore them:
# git stash pop
```

**✅ Expected Output:** Should show files being updated

---

### **STEP 6: Update Backend**

```bash
# Activate virtual environment
source venv/bin/activate
# Or: source .venv/bin/activate

# Install any new Python dependencies
pip install -r requirements.txt

# Update database schema (already done in SQLite, but verify)
python3 -c "from app.models.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

# Verify database updates
sqlite3 career_dna.db "PRAGMA table_info(pages);"
# Should show new columns: module_description, module_color_primary, module_color_secondary

# Restart backend service
sudo systemctl restart carhythm-backend
# Or whatever your service is named:
# sudo systemctl restart carhythm-api
# sudo systemctl restart carhythm

# Check backend status
sudo systemctl status carhythm-backend

# Check backend logs for any errors
sudo journalctl -u carhythm-backend -n 50 -f
# Press Ctrl+C to exit logs
```

**✅ Verify Backend:**
```bash
curl http://localhost:8000/api/v2/modules
# Should return JSON with 3 modules including new metadata
```

---

### **STEP 7: Update Frontend**

```bash
cd frontend

# Install any new dependencies
npm install

# Build production bundle
npm run build

# Copy built files to nginx directory
sudo rm -rf /var/www/carhythm/html/*
sudo cp -r dist/* /var/www/carhythm/html/

# Or if different nginx path:
# sudo cp -r dist/* /var/www/html/
# sudo cp -r dist/* /usr/share/nginx/html/
```

**✅ Verify Build:**
```bash
ls -lh dist/
# Should show: index.html, assets/, CaRhythm updated logo.png
```

---

### **STEP 8: Update Nginx Configuration** (if needed)

Only if you haven't configured nginx for React Router:

```bash
sudo nano /etc/nginx/sites-available/carhythm
```

Make sure you have this configuration:

```nginx
server {
    listen 80;
    server_name carhythm.com www.carhythm.com 145.14.158.174;

    # Frontend
    location / {
        root /var/www/carhythm/html;
        try_files $uri $uri/ /index.html;  # Important for React Router!
        index index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Static files cache
    location /assets/ {
        root /var/www/carhythm/html;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Test and reload nginx:
```bash
# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Check nginx status
sudo systemctl status nginx
```

---

### **STEP 9: Clear Browser Cache & Test**

```bash
# Clear nginx cache (if enabled)
sudo rm -rf /var/cache/nginx/*

# Restart nginx completely
sudo systemctl restart nginx
```

**Then in your browser:**
1. Open https://carhythm.com (or http://145.14.158.174)
2. Press `Ctrl+Shift+R` (hard refresh) to clear browser cache
3. Test the new features:
   - ✅ Module intro screen should appear before questions
   - ✅ Module badge should show in question header
   - ✅ Module completion screen after finishing a module
   - ✅ Feedback page after all modules
   - ✅ UI improvements (numbered answers, gradients)

---

### **STEP 10: Verify Everything Works**

**Backend Health Check:**
```bash
curl http://localhost:8000/api/v2/modules
curl http://localhost:8000/api/v2/questions?page_id=1
```

**Frontend Access:**
- Visit: http://145.14.158.174 or https://carhythm.com
- Check browser console (F12) for errors
- Test complete user flow

**Database Check:**
```bash
sqlite3 career_dna.db "SELECT id, module_name, module_emoji, module_color_primary FROM pages;"
# Should show:
# 1|RIASEC|🎯|#8b5cf6
# 2|Big Five|🧠|#14b8a6
# 3|Behavioral|⚡|#f59e0b
```

---

## 🐛 Troubleshooting

### Issue: Backend won't start
```bash
# Check logs
sudo journalctl -u carhythm-backend -n 100

# Common fixes:
# 1. Missing dependencies
pip install -r requirements.txt

# 2. Database permissions
sudo chown -R www-data:www-data career_dna.db

# 3. Port already in use
sudo lsof -i :8000
# Kill process if needed: sudo kill -9 <PID>
```

### Issue: Frontend shows 404 for routes
```bash
# Add try_files to nginx config
location / {
    try_files $uri $uri/ /index.html;
}

sudo nginx -t
sudo systemctl reload nginx
```

### Issue: Module intro page doesn't load
```bash
# Check API response includes module metadata
curl http://localhost:8000/api/v2/questions?page_id=1 | jq '.page'

# Verify new fields exist
# Should see: module_emoji, module_description, module_color_primary, etc.
```

### Issue: Database schema not updated
```bash
# Run migration manually
cd /home/carhythm/carhythm

sqlite3 career_dna.db "
ALTER TABLE pages ADD COLUMN module_description TEXT;
ALTER TABLE pages ADD COLUMN module_color_primary VARCHAR(20);
ALTER TABLE pages ADD COLUMN module_color_secondary VARCHAR(20);
"

# Populate data
sqlite3 career_dna.db < update_script.sql
```

---

## 📊 Service Management Commands

```bash
# Backend Service
sudo systemctl status carhythm-backend   # Check status
sudo systemctl start carhythm-backend    # Start
sudo systemctl stop carhythm-backend     # Stop
sudo systemctl restart carhythm-backend  # Restart
sudo systemctl enable carhythm-backend   # Enable on boot

# Nginx
sudo systemctl status nginx
sudo systemctl restart nginx
sudo nginx -t  # Test config

# View Logs
sudo journalctl -u carhythm-backend -f   # Follow backend logs
sudo tail -f /var/log/nginx/error.log    # Nginx errors
sudo tail -f /var/log/nginx/access.log   # Nginx access
```

---

## 🎯 Quick Update Script

Save this as `quick-update.sh` on your server:

```bash
#!/bin/bash
set -e

echo "🚀 CaRhythm Quick Update Script"
echo "================================"

# Navigate to app directory
cd /home/carhythm/carhythm

# Backup database
echo "📦 Backing up database..."
cp career_dna.db career_dna.db.backup_$(date +%Y%m%d_%H%M%S)

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Update backend
echo "🔧 Updating backend..."
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart carhythm-backend

# Update frontend
echo "🎨 Building frontend..."
cd frontend
npm install
npm run build
sudo cp -r dist/* /var/www/carhythm/html/
cd ..

# Reload nginx
echo "🔄 Reloading nginx..."
sudo systemctl reload nginx

# Check status
echo "✅ Checking services..."
sudo systemctl status carhythm-backend --no-pager
sudo systemctl status nginx --no-pager

echo ""
echo "✨ Update complete!"
echo "Visit: http://145.14.158.174"
```

Make it executable:
```bash
chmod +x quick-update.sh
```

Run it:
```bash
sudo ./quick-update.sh
```

---

## ✅ Post-Deployment Checklist

- [ ] Backend service running (`sudo systemctl status carhythm-backend`)
- [ ] Nginx running (`sudo systemctl status nginx`)
- [ ] Database backup created
- [ ] Frontend loads at http://145.14.158.174
- [ ] Module intro screens display correctly
- [ ] Module completion screens work
- [ ] Feedback page accessible
- [ ] All 3 modules have correct colors/emojis
- [ ] Browser console has no errors
- [ ] API endpoints responding correctly

---

## 🆘 Rollback Procedure (If Something Goes Wrong)

```bash
# Stop services
sudo systemctl stop carhythm-backend
sudo systemctl stop nginx

# Restore database
cp career_dna.db.backup_YYYYMMDD_HHMMSS career_dna.db

# Restore code (if you have tarball backup)
cd /home/carhythm
rm -rf carhythm
tar -xzf carhythm_backup_YYYYMMDD_HHMMSS.tar.gz

# Restart services
sudo systemctl start carhythm-backend
sudo systemctl start nginx
```

---

## 📞 Need Help?

**Common Issues:**
1. **502 Bad Gateway** → Backend not running
2. **404 on routes** → Nginx config needs `try_files`
3. **Module data missing** → Database not updated
4. **Old frontend showing** → Clear browser cache (Ctrl+Shift+R)

**Useful Commands:**
```bash
# See what's running on port 8000
sudo lsof -i :8000

# Check disk space
df -h

# Check memory
free -h

# See all systemd services
systemctl list-units --type=service --all | grep carhythm
```

---

**🎉 That's it! Your server should now be updated with all the latest features!**

Visit your site and enjoy the new module intro screens, completion celebrations, and feedback system! 🚀
