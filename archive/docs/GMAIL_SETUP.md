# Gmail SMTP Setup Guide for CaRhythm

This guide will help you configure Gmail to send emails from the CaRhythm application.

## 🔐 Why Do I Need an App Password?

Google requires **App Passwords** for applications to access Gmail via SMTP. You **cannot** use your regular Gmail password - this is a security feature to protect your account.

---

## 📋 Step-by-Step Setup

### Step 1: Enable 2-Step Verification

App Passwords only work if you have 2-Step Verification enabled on your Google account.

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** in the left sidebar
3. Under "How you sign in to Google", click **2-Step Verification**
4. If not already enabled, click **Get Started** and follow the instructions
5. You'll need to verify your identity via phone

**✅ Once enabled, you should see "2-Step Verification is on"**

---

### Step 2: Generate an App Password

**Method 1: Direct Link (Easiest)**

1. Go directly to: **https://myaccount.google.com/apppasswords**
2. You may need to sign in again
3. If you see "App passwords", continue to step 7 below
4. If you see an error or it says unavailable, use Method 2

**Method 2: Through Security Settings**

1. Go to: **https://myaccount.google.com/security**
2. Scroll down to "How you sign in to Google" section
3. Click **2-Step Verification** (sign in again if prompted)
4. Scroll all the way to the bottom of the 2-Step Verification page
5. Look for **App passwords** link (it should be near the bottom)
6. Click on **App passwords**

**Method 3: Search in Account Settings**

1. Go to: **https://myaccount.google.com/**
2. Use the search box at the top and type "app passwords"
3. Click on the "App passwords" result
4. Sign in again if prompted

---

**If you still don't see "App passwords" option:**

Common reasons and solutions:

1. **"The setting you are looking for is not available for your account"**
   
   This means Google has restricted App Passwords for your account. Common reasons:
   
   - **Work/School/Organization Account**: Your organization's admin has disabled this feature
     - **Solution**: Use a personal Gmail account (@gmail.com) instead
     - Or ask your IT admin to enable App Passwords for your account
   
   - **New Gmail Account**: Accounts created recently may need more time
     - **Solution**: Wait 24-48 hours after creating the account
     - Verify your phone number if you haven't already
   
   - **Security Restrictions**: Google may have flagged your account
     - **Solution**: Complete account security verification
     - Go to: https://myaccount.google.com/security-checkup
   
   - **Advanced Protection Program**: If enrolled, app passwords are disabled
     - **Solution**: Disable Advanced Protection or use OAuth2 (advanced)
   
   **Quick Fix - Use a Different Gmail Account:**
   
   1. Create a new personal Gmail account specifically for CaRhythm
   2. Example: `carhythm.notifications@gmail.com`
   3. Enable 2-Step Verification on the new account
   4. Generate App Password for the new account
   5. Use the new account's credentials in your `.env` file
   
   This is actually recommended for production anyway!

2. **2-Step Verification not fully enabled**
   - Go to https://myaccount.google.com/signinoptions/two-step-verification
   - Make sure it shows "2-Step Verification is on"
   - Wait 5-10 minutes after enabling, then try again

3. **Using a Work/School Google Account**
   - App passwords may be disabled by your organization
   - Contact your IT administrator
   - Or use a personal Gmail account instead

4. **Advanced Protection Program enrolled**
   - If you're enrolled in Google's Advanced Protection Program, app passwords are not available
   - You'll need to use a different email provider or disable Advanced Protection

5. **Browser cache issues**
   - Try opening in an Incognito/Private window
   - Clear browser cache and cookies
   - Try a different browser

---

**Once you can access App Passwords:**

7. On the App passwords page, you'll see a form:
   - **Select app**: Choose **Mail** (or "Other" if Mail isn't available)
   - **Select device**: Choose **Other (Custom name)**
   - Type: **CaRhythm** (or any name you prefer)

8. Click **Generate**

9. **Google will display a 16-character password** in a yellow box like this:
   ```
   abcd efgh ijkl mnop
   ```
   The password will be shown with spaces, but you'll need to remove them when copying.

10. **IMPORTANT:** 
    - Copy this password immediately!
    - Click the copy button or manually select and copy
    - You won't be able to see it again
    - If you lose it, you'll need to generate a new one

---

### Step 3: Add to Your .env File

1. Open your `.env` file in the CaRhythm project root
2. Find these lines:
   ```env
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   SMTP_FROM_EMAIL=your-email@gmail.com
   ```

3. Replace with your actual values:
   ```env
   SMTP_USER=john.doe@gmail.com
   SMTP_PASSWORD=abcdefghijklmnop
   SMTP_FROM_EMAIL=john.doe@gmail.com
   ```

   > **Note:** Remove all spaces from the app password (paste as one continuous string)

4. Also set your admin email:
   ```env
   ADMIN_EMAIL=admin@example.com
   ```

5. Save the file

---

### Step 4: Test the Configuration

1. Start your CaRhythm backend server:
   ```bash
   source .venv/bin/activate
   python run.py
   ```

2. Complete an assessment and submit student info

3. Check if the email arrives in the inbox

4. **If email doesn't arrive:**
   - Check spam/junk folder
   - Check server logs for error messages
   - Verify all .env values are correct
   - Ensure no extra spaces in SMTP_PASSWORD

---

## 🔍 Troubleshooting

### Problem: "The setting you are looking for is not available for your account"

This is Google's way of saying App Passwords are disabled for your account.

**Why this happens:**

1. **Work/School/Organization email** (@yourcompany.com, @university.edu)
   - Your organization controls this setting
   - IT admin has disabled App Passwords for security

2. **Google Workspace account** (even if it looks like @gmail.com)
   - Some gmail addresses are actually Workspace accounts
   - Managed by an organization with restrictions

3. **Account too new**
   - Very recently created accounts may need 24-48 hours
   - Google needs to verify account legitimacy

4. **Account security issues**
   - Google detected suspicious activity
   - Account needs security verification

**Solutions:**

✅ **Best Solution: Create a New Personal Gmail Account**

1. Go to https://accounts.google.com/signup
2. Create a fresh Gmail account like:
   - `carhythm.mailer@gmail.com`
   - `yourname.carhythm@gmail.com`
   - `noreply.carhythm@gmail.com`
3. Complete phone verification
4. Wait 1 hour (to be safe)
5. Enable 2-Step Verification on new account
6. Generate App Password for new account
7. Use new account in your `.env` file

This is the **recommended approach** even for production use!

✅ **Alternative: Check if it's a Workspace Account**

1. Go to: https://myaccount.google.com/
2. Look at top left corner - if you see your company/organization name, it's a Workspace account
3. Contact your IT administrator to enable App Passwords
4. Or just use a personal Gmail account instead

✅ **Alternative: Use a Different Email Service**

If you can't get Gmail to work, you can use:
- **Outlook.com** (also free, similar setup)
- **SendGrid** (100 free emails/day, more reliable)
- **Mailgun** (100 free emails/day)

See "Production Recommendations" section below for details.

### Problem: Can't find or access "App passwords" option

**Solutions:**

1. **Verify 2-Step Verification is ON:**
   - Go to: https://myaccount.google.com/signinoptions/two-step-verification
   - Must show "2-Step Verification is on"
   - If just enabled, wait 10-15 minutes before trying app passwords

2. **Try the direct link:**
   - https://myaccount.google.com/apppasswords
   - Bookmark this for future use

3. **Check your account type:**
   - Work/School accounts: App passwords may be disabled by admin
   - Solution: Use a personal Gmail account for CaRhythm

4. **Clear browser and try again:**
   ```bash
   # Try in incognito mode or different browser
   # Clear cache: Ctrl+Shift+Delete (Chrome/Firefox)
   ```

5. **Google Workspace accounts:**
   - Admin must enable "Allow users to manage their access to less secure apps"
   - Contact your Google Workspace administrator

6. **Alternative: Use OAuth2 (Advanced)**
   - Requires code changes
   - More secure but more complex setup
   - Not covered in this guide

### Problem: "App passwords" option not showing

**Solution:**
- Make sure 2-Step Verification is fully enabled
- Sign out and sign back in
- Try accessing directly: https://myaccount.google.com/apppasswords
- Check if you're using a work/school account (these may have restrictions)

### Problem: "Username and Password not accepted"

**Solutions:**
- Double-check the app password (no spaces!)
- Make sure you're using the App Password, not your regular Gmail password
- Verify SMTP_USER matches the email that generated the app password
- Try generating a new app password

### Problem: Email sends but goes to spam

**Solutions:**
- Ask recipient to mark as "Not Spam"
- Consider using a custom domain email (not @gmail.com)
- Add SPF/DKIM records if using custom domain

### Problem: "534-5.7.9 Application-specific password required"

**Solution:**
- You're using your regular password instead of App Password
- Generate a new App Password following Step 2 above

### Problem: "535-5.7.8 Username and Password not accepted"

**Solutions:**
- App Password might be expired or revoked
- Generate a new App Password
- Check that 2-Step Verification is still enabled

---

## 🔒 Security Best Practices

1. **Never commit .env file to Git**
   - The `.gitignore` file should already include `.env`
   - Double-check: `git status` should not show `.env`

2. **Keep App Passwords secure**
   - Don't share them
   - Don't hardcode them in source code
   - Revoke unused App Passwords in Google Account settings

3. **Rotate passwords periodically**
   - Generate new App Passwords every 6-12 months
   - Revoke old ones in Google Account → Security → App passwords

4. **Use environment-specific passwords**
   - Different App Password for development vs production
   - Different App Password for different applications

---

## 📧 Alternative: Using a Dedicated Email Account

For production use, consider creating a dedicated Gmail account for sending emails:

1. Create new Gmail: `noreply@yourdomain.com` or `carhythm.mailer@gmail.com`
2. Enable 2-Step Verification on that account
3. Generate App Password for that account
4. Use that account's credentials in production `.env`

**Benefits:**
- Separates personal email from automated emails
- Easier to manage and monitor
- Better for team environments

---

## 🚀 Production Recommendations

For high-volume email sending (100+ emails/day), consider:

1. **SendGrid** (free tier: 100 emails/day)
   - More reliable than Gmail for bulk sending
   - Better deliverability
   - Setup guide: https://sendgrid.com/docs/

2. **AWS SES** (pay-as-you-go)
   - $0.10 per 1,000 emails
   - Highly scalable
   - Requires AWS account

3. **Mailgun** (free tier: 100 emails/day)
   - Simple API
   - Good documentation

---

## ✅ Configuration Checklist

Before going live, verify:

- [ ] 2-Step Verification enabled on Gmail
- [ ] App Password generated (16 characters)
- [ ] `.env` file updated with correct values
- [ ] No spaces in SMTP_PASSWORD
- [ ] SMTP_USER matches the Gmail account
- [ ] ADMIN_EMAIL set for error notifications
- [ ] Test email sent successfully
- [ ] Test email not in spam folder
- [ ] `.env` file not committed to Git
- [ ] Server logs show no SMTP errors

---

## 📞 Need Help?

If you're still having trouble:

1. Check server logs: `tail -f logs/carhythm.log`
2. Enable debug logging in `config.py`
3. Test SMTP connection manually:
   ```python
   python -c "from app.services.email_service import send_test_email; send_test_email()"
   ```
4. Contact CaRhythm support

---

**Last Updated:** November 2025  
**Version:** 1.0
