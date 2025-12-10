"""
CaRhythm Email Service
Handles sending emails with PDF attachments via Gmail SMTP
"""

import smtplib
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.utils import formataddr
from typing import Optional, Dict, Any
import logging
from datetime import datetime
from io import BytesIO
import os
import base64

from ..config import settings, validate_email_config

# Setup logging
logger = logging.getLogger(__name__)

# Logo path
LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                         'frontend', 'public', 'CaRhythm updated logo.png')


def create_results_email_html(student_name: str, holland_code: str, top_strength: str, logo_cid: str = None) -> str:
    """
    Create HTML email template for results delivery
    """
    # Logo section - use embedded image if available, otherwise show text logo
    if logo_cid:
        logo_html = f'<img src="cid:{logo_cid}" alt="CaRhythm Logo" style="width: 120px; height: 120px; margin: 0 auto; display: block;"/>'
    else:
        # Fallback to text-based logo if image embedding fails
        logo_html = '<div class="logo-text-fallback" style="font-size: 48px; font-weight: bold; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">CaRhythm</div>'
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background: linear-gradient(135deg, #FF6F61 0%, #2E1A47 100%);
                border-radius: 16px;
                padding: 40px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .logo {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo-icon {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
            .logo-text {{
                font-size: 32px;
                font-weight: bold;
                color: white;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }}
            .tagline {{
                color: rgba(255,255,255,0.9);
                font-size: 14px;
                font-style: italic;
                margin-top: 5px;
            }}
            .content {{
                background: white;
                border-radius: 12px;
                padding: 30px;
                margin-top: 20px;
            }}
            h1 {{
                color: #FF6F61;
                font-size: 24px;
                margin-bottom: 20px;
            }}
            .highlight-box {{
                background: linear-gradient(135deg, #FFF5F4 0%, #FFE5E2 100%);
                border-left: 4px solid #FF6F61;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
            }}
            .highlight-box strong {{
                color: #2E1A47;
                font-size: 18px;
            }}
            .cta-button {{
                display: inline-block;
                background: linear-gradient(135deg, #FF6F61 0%, #2E1A47 100%);
                color: white;
                padding: 15px 30px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: bold;
                margin: 20px 0;
                text-align: center;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                color: #666;
                font-size: 14px;
            }}
            .emoji {{
                font-size: 24px;
                margin-right: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                {logo_html}
                <div class="logo-text">CaRhythm</div>
                <div class="tagline">Career Compass with a Heartbeat</div>
            </div>
            
            <div class="content">
                <h1>Your Career DNA Results Are Ready!</h1>
                
                <p>Dear {student_name},</p>
                
                <p>Congratulations on completing the CaRhythm Career Assessment! Your personalized Career DNA Report is now ready.</p>
                
                <div class="highlight-box">
                    <p><strong>Your Holland Code:</strong> {holland_code}</p>
                    <p><strong>Top Strength:</strong> {top_strength}</p>
                </div>
                
                <p><strong>Your comprehensive report includes:</strong></p>
                <ul>
                    <li>Complete RIASEC Career Interest Profile</li>
                    <li>Big Five Personality Analysis</li>
                    <li>Behavioral Insights & Action Items</li>
                    <li>Career Pathways & Recommendations</li>
                    <li>Visual Charts & Analysis</li>
                    <li>Personalized Action Plan</li>
                </ul>
                
                <p><strong>Your report is attached to this email as a PDF.</strong></p>
                
                <p style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 20px;">
                    <strong>💡 Next Steps:</strong><br>
                    • Review your results carefully and identify patterns in your profile<br>
                    • Share with career counselors, mentors, or family members<br>
                    • Reflect on how your strengths align with your career goals<br>
                    • Use the insights to explore career paths that match your DNA
                </p>
                
                <p style="background: linear-gradient(135deg, #FFF5F4 0%, #FFE5E2 100%); padding: 15px; border-radius: 8px; border-left: 4px solid #FF6F61;">
                    <strong>🚀 Exciting Updates Coming Soon!</strong><br>
                    We're developing enhanced assessments and premium features to help you dive deeper into your career journey. Stay tuned for more comprehensive tests, personalized coaching insights, and advanced career matching tools. Follow us to be the first to know!
                </p>
                
                <div class="footer">
                    <p><strong>Find Greater Career Fulfillment</strong></p>
                    <p>CaRhythm Team</p>
                    <p style="font-size: 12px; color: #999;">
                        Questions? Reply to this email or contact us at support@carhythm.com
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def create_admin_notification_html(student_name: str, student_email: str, 
                                   session_id: str, error_message: str, 
                                   response_id: int) -> str:
    """
    Create HTML email for admin error notifications
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Courier New', monospace;
                background-color: #f5f5f5;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-left: 4px solid #f44336;
                padding: 30px;
                max-width: 600px;
                margin: 0 auto;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #f44336;
                font-size: 20px;
            }}
            .error-box {{
                background: #ffebee;
                padding: 15px;
                border-radius: 4px;
                margin: 15px 0;
                font-family: monospace;
                color: #c62828;
            }}
            .info-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            .info-table td {{
                padding: 10px;
                border-bottom: 1px solid #e0e0e0;
            }}
            .info-table td:first-child {{
                font-weight: bold;
                width: 150px;
                color: #666;
            }}
            .timestamp {{
                color: #999;
                font-size: 12px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚠️ CaRhythm Alert: PDF/Email Error</h1>
            
            <p>An error occurred while processing results for a student.</p>
            
            <table class="info-table">
                <tr>
                    <td>Student Name:</td>
                    <td>{student_name}</td>
                </tr>
                <tr>
                    <td>Email:</td>
                    <td>{student_email}</td>
                </tr>
                <tr>
                    <td>Session ID:</td>
                    <td><code>{session_id}</code></td>
                </tr>
                <tr>
                    <td>Response ID:</td>
                    <td>{response_id}</td>
                </tr>
            </table>
            
            <div class="error-box">
                <strong>Error Message:</strong><br>
                {error_message}
            </div>
            
            <p><strong>Recommended Action:</strong></p>
            <ul>
                <li>Check server logs for detailed error trace</li>
                <li>Verify SMTP configuration is correct</li>
                <li>Check PDF generation service</li>
                <li>Manually resend results if needed</li>
            </ul>
            
            <div class="timestamp">
                Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
            </div>
        </div>
    </body>
    </html>
    """
    return html


async def send_results_email(
    to_email: str,
    student_name: str,
    holland_code: str,
    top_strength: str,
    pdf_buffer: BytesIO,
    pdf_filename: str = "CaRhythm_Career_DNA_Report.pdf"
) -> Dict[str, Any]:
    """
    Send results email with PDF attachment via Gmail SMTP
    
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'error': Optional[str]
        }
    """
    # Validate configuration
    is_valid, message = validate_email_config()
    if not is_valid:
        logger.error(f"Email configuration invalid: {message}")
        return {
            'success': False,
            'message': 'Email service not configured',
            'error': message
        }
    
    if not settings.ENABLE_EMAIL:
        logger.info("Email sending disabled in configuration")
        return {
            'success': False,
            'message': 'Email sending is disabled',
            'error': 'ENABLE_EMAIL=false'
        }
    
    try:
        # Create message with related parts for embedded images
        msg = MIMEMultipart('mixed')
        msg['From'] = formataddr((settings.SMTP_FROM_NAME, settings.SMTP_FROM_EMAIL))
        msg['To'] = to_email
        msg['Subject'] = f"Your CaRhythm Career DNA Results Are Ready!"
        
        # Create multipart/related for HTML + embedded images
        msg_related = MIMEMultipart('related')
        
        # Try to embed logo
        logo_cid = None
        if os.path.exists(LOGO_PATH):
            try:
                with open(LOGO_PATH, 'rb') as f:
                    logo_data = f.read()
                logo_img = MIMEImage(logo_data)
                logo_cid = 'carhythm_logo'
                logo_img.add_header('Content-ID', f'<{logo_cid}>')
            except Exception as e:
                logger.warning(f"Could not embed logo: {e}")
        
        # Create HTML body with logo CID
        html_content = create_results_email_html(student_name, holland_code, top_strength, logo_cid)
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg_related.attach(html_part)
        
        # Attach logo image after HTML
        if logo_cid and os.path.exists(LOGO_PATH):
            try:
                with open(LOGO_PATH, 'rb') as f:
                    logo_data = f.read()
                logo_img = MIMEImage(logo_data)
                logo_img.add_header('Content-ID', f'<{logo_cid}>')
                msg_related.attach(logo_img)
            except Exception as e:
                logger.warning(f"Could not attach logo: {e}")
        
        msg.attach(msg_related)
        
        # Attach PDF
        pdf_buffer.seek(0)
        pdf_attachment = MIMEApplication(pdf_buffer.read(), _subtype='pdf')
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
        msg.attach(pdf_attachment)
        
        # Send email with retry logic
        for attempt in range(settings.EMAIL_RETRY_ATTEMPTS):
            try:
                await aiosmtplib.send(
                    msg,
                    hostname=settings.SMTP_HOST,
                    port=settings.SMTP_PORT,
                    username=settings.SMTP_USER,
                    password=settings.SMTP_PASSWORD,
                    start_tls=True,
                    timeout=30
                )
                
                logger.info(f"✅ Email sent successfully to {to_email}")
                return {
                    'success': True,
                    'message': f'Results sent to {to_email}',
                    'error': None
                }
                
            except Exception as e:
                logger.warning(f"Email attempt {attempt + 1} failed: {str(e)}")
                if attempt < settings.EMAIL_RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(settings.EMAIL_RETRY_DELAY)
                else:
                    raise
        
    except Exception as e:
        import traceback
        error_msg = f"Failed to send email: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'message': 'Failed to send email',
            'error': error_msg
        }


async def send_admin_notification(
    student_name: str,
    student_email: str,
    session_id: str,
    error_message: str,
    response_id: int
) -> bool:
    """
    Send error notification to admin
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    if not settings.ADMIN_EMAIL or not settings.ENABLE_EMAIL:
        logger.warning("Admin notifications disabled or admin email not configured")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr((settings.SMTP_FROM_NAME, settings.SMTP_FROM_EMAIL))
        msg['To'] = settings.ADMIN_EMAIL
        msg['Subject'] = f"[CaRhythm Alert] PDF/Email Error for {student_name}"
        
        # Create HTML body
        html_content = create_admin_notification_html(
            student_name, student_email, session_id, error_message, response_id
        )
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
            timeout=20
        )
        
        logger.info(f"✅ Admin notification sent to {settings.ADMIN_EMAIL}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send admin notification: {str(e)}")
        return False


import asyncio

# Synchronous wrapper for backward compatibility
def send_results_email_sync(*args, **kwargs) -> Dict[str, Any]:
    """Synchronous wrapper for send_results_email"""
    return asyncio.run(send_results_email(*args, **kwargs))


def send_admin_notification_sync(*args, **kwargs) -> bool:
    """Synchronous wrapper for send_admin_notification"""
    return asyncio.run(send_admin_notification(*args, **kwargs))
