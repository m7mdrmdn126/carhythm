# 🚀 QUICK SERVER UPDATE - Copy & Paste Commands

## ✅ Changes Successfully Pushed to GitHub!
- Commit: d51d6f2
- 27 files changed (1234 insertions, 153 deletions)
- **Major Update:** Bilingual support (Arabic/English) + Branding refresh
- Ready to deploy!

---

## 📋 SSH & Update (Copy this entire block)

```bash
# 1. SSH into your VPS
ssh root@145.14.158.174

# 2. Navigate to app directory
cd /home/carhythm/carhythm

# 3. Pull latest code from GitHub
git pull origin main

# 4. Update database with Arabic translations & new modules
bash scripts/update_server_database.sh

# 5. Update backend dependencies
source venv/bin/activate
pip install -r requirements.txt

# 6. Restart backend
sudo systemctl restart carhythm-backend

# 7. Build and deploy frontend
cd frontend
npm install
npm run build
sudo cp -r dist/* /var/www/carhythm/html/
cd ..

# 8. Reload nginx
sudo systemctl reload nginx

# 9. Verify services are running
sudo systemctl status carhythm-backend --no-pager
sudo systemctl status nginx --no-pager
```

**The database update script will show:**
```
✅ Backup created
✅ Translation columns added
✅ Arabic translations added (73 questions)
✅ Module metadata updated

Module Configuration:
1|The Signal|الإشارة|🧠
2|The Fingerprint|البصمة|👆
3|The Compass|البوصلة|🎵
```

---

## 🧪 Test After Update

1. Open browser: http://145.14.158.174 or https://carhythm.com
2. Press `Ctrl+Shift+R` (hard refresh)
3. Test the new features:
   - ✅ **Language Switcher** - Toggle between EN/عربي in top right
   - ✅ **New Module Names** - "The Signal", "The Fingerprint", "The Compass"
   - ✅ **New Emojis** - 🧠 (Signal), 👆 (Fingerprint), 🎵 (Compass)
   - ✅ **Arabic Content** - All 73 questions translated
   - ✅ **RTL Layout** - Text direction switches for Arabic
   - ✅ **Updated Colors** - Purple/Coral theme matching logo
   - ✅ **Responsive Logo** - Large on desktop, smaller on mobile
   - ✅ **Module Descriptions** - New engaging descriptions on intro screens

---

## 🐛 If Something Goes Wrong

**Database update failed?**
```bash
# Restore from backup
ls -lt career_dna.db.backup_* | head -1  # Find latest backup
cp career_dna.db.backup_YYYYMMDD_HHMMSS career_dna.db
sudo systemctl restart carhythm-backend
```

**Backend not starting?**
```bash
sudo journalctl -u carhythm-backend -n 50
```

**Frontend showing old version?**
```bash
# Clear nginx cache
sudo rm -rf /var/cache/nginx/*
sudo systemctl restart nginx

# In browser: Ctrl+Shift+R (hard refresh)
```

---

## 📞 Quick Checks

```bash
# Is backend running?
curl http://localhost:8000/api/v2/modules

# What's using port 8000?
sudo lsof -i :8000

# View live logs
sudo journalctl -u carhythm-backend -f

# Check nginx config
sudo nginx -t
```

---

## 📚 Full Details

See `UPDATE_DEPLOYMENT_GUIDE.md` for complete documentation with:
- Detailed troubleshooting
- Rollback procedures
- Service management commands
- Common issues & solutions

---

**🎉 That's it! Your server will be updated in ~5 minutes!**
