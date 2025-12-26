# 🚀 QUICK SERVER UPDATE - Copy & Paste Commands

## ✅ Changes Successfully Pushed to GitHub!
- Commit: 6ea45c0
- 32 files changed
- Ready to deploy!

---

## 📋 SSH & Update (Copy this entire block)

```bash
# 1. SSH into your VPS
ssh root@145.14.158.174

# 2. Navigate to app directory (adjust path if different)
cd /home/carhythm/carhythm

# 3. Backup database
cp career_dna.db career_dna.db.backup_$(date +%Y%m%d_%H%M%S)

# 4. Pull latest code
git pull origin main

# 5. Update database schema
sqlite3 career_dna.db < database_update.sql

# 6. Update backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart carhythm-backend

# 7. Build and deploy frontend
cd frontend
npm install
npm run build
sudo cp -r dist/* /var/www/carhythm/html/
cd ..

# 8. Reload nginx
sudo systemctl reload nginx

# 9. Verify everything is running
sudo systemctl status carhythm-backend --no-pager
sudo systemctl status nginx --no-pager

# 10. Check module data
sqlite3 career_dna.db "SELECT id, module_name, module_emoji, module_color_primary FROM pages;"
```

**Expected output from step 10:**
```
1|RIASEC|🎯|#8b5cf6
2|Big Five|🧠|#14b8a6
3|Behavioral|⚡|#f59e0b
```

---

## 🧪 Test After Update

1. Open browser: http://145.14.158.174 or https://carhythm.com
2. Press `Ctrl+Shift+R` (hard refresh)
3. Start assessment
4. Verify you see:
   - ✅ Module intro screen with emoji & description
   - ✅ Module badge in question header (colored)
   - ✅ Completion celebration after each module
   - ✅ Feedback page at the end
   - ✅ Numbered answers (1. 2. 3. instead of emojis)

---

## 🐛 If Something Goes Wrong

**Backend not starting?**
```bash
sudo journalctl -u carhythm-backend -n 50
```

**Frontend showing old version?**
```bash
# Clear nginx cache
sudo rm -rf /var/cache/nginx/*
sudo systemctl restart nginx

# In browser: Ctrl+Shift+R
```

**Database error?**
```bash
# Restore backup
cp career_dna.db.backup_YYYYMMDD_HHMMSS career_dna.db
sudo systemctl restart carhythm-backend
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
