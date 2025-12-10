#!/usr/bin/env python3
"""
Quick test script for email delivery system
Tests configuration, PDF generation, and email sending
"""

import sys
import os
import asyncio
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_1_configuration():
    """Test 1: Configuration validation"""
    print("\n" + "="*60)
    print("TEST 1: Configuration Validation")
    print("="*60)
    
    try:
        from app.config import settings, validate_email_config
        
        print(f"✓ Settings loaded successfully")
        print(f"  - SMTP Host: {settings.SMTP_HOST}")
        print(f"  - SMTP Port: {settings.SMTP_PORT}")
        print(f"  - From Email: {settings.SMTP_FROM_EMAIL}")
        print(f"  - Email Enabled: {settings.ENABLE_EMAIL}")
        
        is_valid, message = validate_email_config()
        if is_valid:
            print(f"✓ Email configuration is valid")
            return True
        else:
            print(f"✗ Email configuration invalid: {message}")
            return False
            
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_2_pdf_generation():
    """Test 2: PDF generation"""
    print("\n" + "="*60)
    print("TEST 2: PDF Generation")
    print("="*60)
    
    try:
        from app.services.pdf_service import generate_pdf_report
        import json
        
        # Test data
        test_response = {
            'student_name': 'Test Student',
            'email': 'test@example.com',
            'age_group': '18-25',
            'country': 'USA',
            'origin_country': 'USA'
        }
        
        test_scores = {
            'riasec_scores_v1_1': json.dumps({
                'R': 12.5, 'I': 10.0, 'A': 8.5, 
                'S': 6.0, 'E': 4.5, 'C': 3.0
            }),
            'bigfive_scores_v1_1': json.dumps({
                'O': 20.0, 'C': 18.0, 'E': 15.0, 
                'A': 16.0, 'N': 10.0
            }),
            'behavioral_scores_v1_1': json.dumps({
                'motivation': 12.0,
                'grit': 11.0,
                'self_regulation': 10.0,
                'time_management': 9.0,
                'growth_mindset': 13.0,
                'perfectionism': 7.0,
                'procrastination': 5.0
            }),
            'behavioral_flags_v1_1': json.dumps({
                'procrastination_risk': False,
                'perfectionism_risk': False,
                'low_grit_risk': False,
                'poor_regulation_risk': False,
                'growth_mindset': True
            }),
            'holland_code_v1_1': 'RIA'
        }
        
        print("Generating PDF report...")
        pdf_buffer = generate_pdf_report(test_response, test_scores)
        
        if isinstance(pdf_buffer, BytesIO):
            pdf_size = len(pdf_buffer.getvalue())
            pdf_size_mb = pdf_size / (1024 * 1024)
            print(f"✓ PDF generated successfully")
            print(f"  - Size: {pdf_size_mb:.2f} MB")
            print(f"  - Pages: ~10-15 (estimated)")
            
            # Save test PDF
            with open('test_report.pdf', 'wb') as f:
                f.write(pdf_buffer.getvalue())
            print(f"  - Saved to: test_report.pdf")
            
            return True
        else:
            print(f"✗ PDF generation failed: Invalid buffer type")
            return False
            
    except Exception as e:
        print(f"✗ PDF generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_3_email_sending():
    """Test 3: Email sending (async)"""
    print("\n" + "="*60)
    print("TEST 3: Email Sending")
    print("="*60)
    
    try:
        from app.services.email_service import send_results_email
        from app.services.pdf_service import generate_pdf_report
        from app.config import settings
        import json
        
        if not settings.ENABLE_EMAIL:
            print("⚠ Email is disabled in settings (ENABLE_EMAIL=false)")
            print("  To test email sending, set ENABLE_EMAIL=true in .env")
            return None  # Skip test
        
        # Get test email from user
        print("\nEnter test email address (or press Enter to skip):")
        test_email = input("> ").strip()
        
        if not test_email:
            print("⚠ Skipping email test (no email provided)")
            return None
        
        # Generate test PDF
        print(f"\nGenerating PDF for {test_email}...")
        test_response = {
            'student_name': 'Test Student',
            'email': test_email,
            'age_group': '18-25',
            'country': 'USA',
            'origin_country': 'USA'
        }
        
        test_scores = {
            'riasec_scores_v1_1': json.dumps({'R': 12, 'I': 10, 'A': 8, 'S': 6, 'E': 4, 'C': 3}),
            'bigfive_scores_v1_1': json.dumps({'O': 20, 'C': 18, 'E': 15, 'A': 16, 'N': 10}),
            'behavioral_scores_v1_1': json.dumps({
                'motivation': 12, 'grit': 11, 'self_regulation': 10,
                'time_management': 9, 'growth_mindset': 13
            }),
            'behavioral_flags_v1_1': json.dumps({
                'procrastination_risk': False, 'growth_mindset': True
            }),
            'holland_code_v1_1': 'RIA'
        }
        
        pdf_buffer = generate_pdf_report(test_response, test_scores)
        
        # Send email
        print(f"Sending email to {test_email}...")
        success = await send_results_email(
            to_email=test_email,
            student_name='Test Student',
            pdf_buffer=pdf_buffer,
            session_id='test-session-123'
        )
        
        if success:
            print(f"✓ Email sent successfully to {test_email}")
            print(f"  - Check your inbox (and spam folder)")
            print(f"  - PDF should be attached")
            return True
        else:
            print(f"✗ Email sending failed")
            return False
            
    except Exception as e:
        print(f"✗ Email sending test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("CaRhythm Email Delivery System - Test Suite")
    print("="*60)
    
    results = {
        'Configuration': None,
        'PDF Generation': None,
        'Email Sending': None
    }
    
    # Test 1: Configuration
    results['Configuration'] = test_1_configuration()
    
    # Test 2: PDF Generation
    if results['Configuration']:
        results['PDF Generation'] = test_2_pdf_generation()
    else:
        print("\n⚠ Skipping PDF test (configuration invalid)")
    
    # Test 3: Email Sending (async)
    if results['Configuration'] and results['PDF Generation']:
        results['Email Sending'] = asyncio.run(test_3_email_sending())
    else:
        print("\n⚠ Skipping email test (previous tests failed)")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⊘ SKIP"
        print(f"{test_name:<20} {status}")
    
    # Overall result
    print("\n" + "="*60)
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    total = len(results)
    
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed > 0:
        print("\n⚠ Some tests failed. Please check the errors above.")
        sys.exit(1)
    elif passed == 0:
        print("\n⚠ No tests passed. Please configure your .env file.")
        sys.exit(1)
    else:
        print("\n✓ All tests passed successfully!")
        sys.exit(0)


if __name__ == '__main__':
    main()
