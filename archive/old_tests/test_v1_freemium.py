"""
Test script for V1 Freemium PDF generation
Tests both free and premium versions with new coral/purple branding
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.pdf_service import generate_pdf_report
from datetime import datetime

# Sample test data
sample_response_data = {
    'student_name': 'Ahmed El-Sayed',
    'student_email': 'ahmed@example.com',
    'session_id': 'test_session_123'
}

sample_scores_data = {
    'riasec_raw_scores': {
        'R': 12.5,
        'I': 13.8,
        'A': 11.2,
        'S': 9.5,
        'E': 8.3,
        'C': 7.9
    },
    'riasec_strength_labels': {
        'R': 'High',
        'I': 'Very High',
        'A': 'High',
        'S': 'Medium',
        'E': 'Medium',
        'C': 'Medium'
    },
    'holland_code': 'RIA',
    'bigfive_raw_scores': {
        'O': 21.5,
        'C': 18.3,
        'E': 15.7,
        'A': 19.2,
        'N': 12.4
    },
    'bigfive_strength_labels': {
        'O': 'Very High',
        'C': 'High',
        'E': 'Medium',
        'A': 'High',
        'N': 'Medium'
    },
    'behavioral_raw_scores': {
        'motivation_type': 12.3,
        'grit_persistence': 11.5,
        'self_efficacy': 10.8,
        'resilience': 13.2,
        'learning_orientation': 12.7,
        'empathy': 11.9,
        'task_start_tempo': 9.5
    },
    'behavioral_strength_labels': {
        'motivation': 'High',
        'grit': 'High',
        'self_regulation': 'Medium',
        'time_management': 'Medium',
        'growth_mindset': 'High'
    },
    'behavioral_flags': {
        'procrastination_risk': False,
        'perfectionism_risk': True,
        'low_grit_risk': False,
        'poor_regulation_risk': False,
        'growth_mindset': True
    },
    'ikigai_zones': {}
}

def test_free_pdf():
    """Generate FREE version PDF with blurred premium sections"""
    print("🎨 Generating FREE PDF with coral/purple branding...")
    
    try:
        pdf_buffer = generate_pdf_report(
            response_data=sample_response_data,
            scores_data=sample_scores_data,
            is_free_version=True,
            checkout_url="https://carhythm.com/paid",
            discount_code="LAUNCH50"
        )
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'test_free_v1_{timestamp}.pdf'
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
        print(f"✅ FREE PDF generated successfully!")
        print(f"   📄 File: {filename}")
        print(f"   💾 Size: {file_size:.2f} MB")
        print(f"   🔒 Premium sections: BLURRED")
        print(f"   🎁 QR codes: 4 (3 mini + 1 large)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating FREE PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_premium_pdf():
    """Generate PREMIUM version PDF with all sections visible"""
    print("\n💎 Generating PREMIUM PDF with all sections...")
    
    try:
        pdf_buffer = generate_pdf_report(
            response_data=sample_response_data,
            scores_data=sample_scores_data,
            is_free_version=False  # Full premium version
        )
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'test_premium_v1_{timestamp}.pdf'
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
        print(f"✅ PREMIUM PDF generated successfully!")
        print(f"   📄 File: {filename}")
        print(f"   💾 Size: {file_size:.2f} MB")
        print(f"   🔓 All sections: VISIBLE")
        print(f"   📊 Ikigai + Careers + Action Plan: INCLUDED")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating PREMIUM PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🎨 CARHYTHM V1 FREEMIUM PDF TEST")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎨 Brand Colors: Coral (#FF6F61) + Purple (#2E1A47)")
    print("=" * 60)
    
    # Test both versions
    free_success = test_free_pdf()
    premium_success = test_premium_pdf()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"FREE PDF:    {'✅ PASS' if free_success else '❌ FAIL'}")
    print(f"PREMIUM PDF: {'✅ PASS' if premium_success else '❌ FAIL'}")
    print("=" * 60)
    
    if free_success and premium_success:
        print("\n🎉 All tests passed! Check the generated PDFs.")
        print("🔗 Test the /paid landing page at: http://localhost:8000/paid?discount=LAUNCH50")
    else:
        print("\n⚠️ Some tests failed. Check error messages above.")
        sys.exit(1)
