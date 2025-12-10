# Email Delivery Setup Guide

## Overview

CaRhythm v1.1 now sends assessment results as beautiful PDF reports via email instead of displaying them on the web. This guide will help you configure the email delivery system.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `pydantic-settings==2.0.3` - Configuration management
- `aiosmtplib==3.0.1` - Async SMTP email sending
- `email-validator==2.1.0` - Email validation
- `Pillow==10.1.0` - Image processing for PDFs

### 2. Configure Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

### 3. Set Up Gmail App Password

Follow the detailed instructions in `GMAIL_SETUP.md` to:
1. Enable 2-Step Verification on your Google account
2. Generate an App Password
3. Add credentials to your `.env` file

### 4. Update Configuration

Edit your `.env` file with your credentials:

```env
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=CaRhythm Assessment

# Admin Notifications
ADMIN_EMAIL=admin@example.com
ADMIN_NAME=CaRhythm Admin

# Application Settings
APP_URL=http://localhost:8000
ENABLE_EMAIL=true

# Optional Settings
MAX_PDF_SIZE_MB=10
EMAIL_RETRY_ATTEMPTS=3
EMAIL_RETRY_DELAY=5
MAX_RESEND_PER_SESSION=5
```

## Features

### ✨ What Students Get

When a student completes the assessment, they receive a **10-15 page PDF report** containing:

1. **Cover Page** - Branded with CaRhythm logo and date
2. **Welcome Letter** - Personalized greeting
3. **RIASEC Career Interests** (3-4 pages)
   - Theory explanation
   - Radar chart visualization
   - Holland Hexagon diagram
   - Holland Code (e.g., "RIA")
   - Career zone descriptions

4. **Big Five Personality Profile** (2-3 pages)
   - Theory explanation
   - Horizontal bar chart
   - Trait interpretations with strength labels

5. **Behavioral Traits & Flags** (2 pages)
   - Theory explanation
   - Traffic light dashboard for behavioral flags
   - Scores table with growth insights

6. **Comprehensive Strength Heatmap** (1 page)
   - Color-coded grid of all strengths across domains

7. **Ikigai Career Sweet Spot** (2 pages)
   - 4-circle Venn diagram
   - Career zone mapping
   - Intersection analysis

8. **Career Recommendations** (1-2 pages)
   - 5-7 personalized career paths
   - Next steps for exploration

9. **Action Plan** (1 page)
   - Immediate actions (this week)
   - Short-term goals (this month)
   - Long-term vision (6-12 months)

10. **About CaRhythm** (1 page)
    - Platform information
    - Contact details
    - Thank you message

### 📧 Email Features

- **Beautiful HTML emails** with inline styling
- **PDF attachment** (typically 2-5 MB)
- **Automatic retries** (3 attempts with 5-second delay)
- **Admin notifications** on delivery failures
- **Email editing** - Students can update their email
- **Resend functionality** - Students can request resend
- **Rate limiting** - Max 5 resends per session

## User Flow

### Old Flow (v1.0)
```
Submit Info → Redirect → View Results on Web → Print/Screenshot
```

### New Flow (v1.1)
```
Submit Info → Email Sent → Check Inbox → Open PDF → Enjoy!
```

## Frontend Changes

### Complete.jsx Updates

**Before:**
- Showed "Generating Your Profile"
- Redirected to `/results/{sessionId}` after 2 seconds

**After:**
- Shows "Check Your Email!" confirmation
- Displays email address (editable)
- Provides "Resend Email" button
- Shows checklist of what's in the PDF
- No redirect - students stay on success page

### New API Endpoints

1. **POST `/api/v2/student/info`** - Enhanced
   - Calculates scores
   - Generates PDF
   - Sends email
   - Returns: `{success, message, email_sent, session_id}`

2. **POST `/api/v2/resend-results`** - New
   - Request body: `{session_id, new_email?}`
   - Regenerates PDF
   - Resends email
   - Returns: `{success, message, email}`

## PDF Design

### Story-Like Magazine Style

The PDF uses a **story-like** design with:
- **Brand colors**: Purple (#667eea), Deep Purple (#764ba2), Pink (#f093fb)
- **Inspirational quotes** between sections (6 quotes total)
- **Professional typography** (Helvetica family)
- **Page numbers and footers** on every page
- **Decorative elements** (quote boxes, colored headers)
- **High-quality visualizations** (150 DPI, full color)

### Visualizations

All charts are generated with matplotlib:
- **Radar charts** (RIASEC) - 0-15 scale
- **Hexagon diagrams** (Holland)
- **Horizontal bar charts** (Big Five) - 0-25 scale
- **Traffic light dashboards** (Behavioral flags)
- **Venn diagrams** (Ikigai zones)
- **Heatmaps** (Comprehensive strength profile)

## Testing

### 1. Test Email Configuration

```python
from app.config import settings, validate_email_config

# Check if config is valid
is_valid, message = validate_email_config()
print(f"Email config valid: {is_valid}")
print(f"Message: {message}")
```

### 2. Test Email Sending

```python
from app.services.email_service import send_results_email
from app.services.pdf_service import generate_pdf_report
import asyncio

async def test_email():
    # Generate test PDF
    test_response = {
        'student_name': 'Test Student',
        'email': 'test@example.com'
    }
    
    test_scores = {
        'riasec_scores_v1_1': '{"R": 12, "I": 10, "A": 8, "S": 6, "E": 4, "C": 3}',
        'bigfive_scores_v1_1': '{"O": 20, "C": 18, "E": 15, "A": 16, "N": 10}',
        'behavioral_scores_v1_1': '{"motivation": 12, "grit": 11, "self_regulation": 10}',
        'behavioral_flags_v1_1': '{"procrastination_risk": false, "growth_mindset": true}',
        'holland_code_v1_1': 'RIA'
    }
    
    pdf = generate_pdf_report(test_response, test_scores)
    
    # Send email
    success = await send_results_email(
        to_email='test@example.com',
        student_name='Test Student',
        pdf_buffer=pdf,
        session_id='test-session-123'
    )
    
    print(f"Email sent: {success}")

asyncio.run(test_email())
```

### 3. Test Complete Flow

1. Start the backend: `uvicorn app.main:app --reload`
2. Start the frontend: `cd frontend && npm run dev`
3. Complete an assessment
4. Submit student info
5. Check email inbox
6. Open PDF and verify all pages

## Troubleshooting

### Email Not Sending

**Problem:** Email fails to send

**Solutions:**
1. Check `.env` file has correct Gmail credentials
2. Verify Gmail App Password (not regular password)
3. Check `ENABLE_EMAIL=true` in `.env`
4. Review logs: `tail -f app.log`
5. Test SMTP connection manually

### PDF Generation Fails

**Problem:** Error generating PDF

**Solutions:**
1. Check all scores are properly calculated
2. Verify matplotlib and reportlab are installed
3. Check JSON fields are valid
4. Review error in logs

### Admin Notifications Not Working

**Problem:** Admin doesn't receive error notifications

**Solutions:**
1. Verify `ADMIN_EMAIL` in `.env`
2. Check admin email is valid
3. Review admin notification template
4. Test admin notification separately

### Students Don't See Success Page

**Problem:** Frontend errors after submission

**Solutions:**
1. Check API response format matches frontend expectations
2. Verify `session_id` is returned in response
3. Check browser console for errors
4. Test API endpoint with Postman/curl

## Production Deployment

### Security Best Practices

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use environment variables** on production server
3. **Rotate App Passwords** regularly
4. **Monitor failed deliveries** via admin notifications
5. **Set up logging** for email operations
6. **Use rate limiting** to prevent abuse

### Recommended Email Services

For production, consider:
- **Gmail** - Good for small/medium scale (free tier: 500/day)
- **SendGrid** - Scalable (free tier: 100/day)
- **Mailgun** - Developer-friendly (free tier: 5,000/month)
- **AWS SES** - Enterprise scale (pay-as-you-go)

### Scaling Considerations

- **Queue system**: Use Celery for async email processing
- **Background workers**: Separate email sending from API requests
- **CDN for PDFs**: Store PDFs temporarily, send download links
- **Email tracking**: Add open/click tracking for analytics
- **Monitoring**: Set up alerts for failed deliveries

## Support

### Configuration Issues

- Review `GMAIL_SETUP.md` for Gmail setup
- Check `.env.example` for all required variables
- Validate configuration with `validate_email_config()`

### Deployment Issues

- Check server firewall allows SMTP (port 587)
- Verify environment variables are loaded
- Test SMTP connection from server
- Review application logs

### Feature Requests

Contact the development team for:
- Custom email templates
- Additional PDF visualizations
- Alternative email providers
- Webhook integrations

## Changelog

### v1.1 - Email Delivery

**Added:**
- Email delivery system with Gmail SMTP
- Story-like PDF reports (10-15 pages)
- Resend functionality with email editing
- Admin error notifications
- Comprehensive visualizations in PDF

**Removed:**
- Web-based results display
- Auto-redirect to results page

**Changed:**
- Complete.jsx now shows email confirmation
- API responses include email_sent status
- Student info endpoint now triggers email

---

**Need Help?** Email: support@carhythm.com
