#!/usr/bin/env python3
"""
Test V2 PDF Template Generation
Tests the new archetype-focused design with QR codes, blurred upsell, and RTL support
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.pdf_service import generate_pdf_report

# Sample data for testing
def get_sample_english_data():
    """English test data"""
    response_data = {
        'student_name': 'Ahmed Hassan',
        'student_email': 'ahmed@example.com',
        'session_id': 'test_session_001'
    }
    
    scores_data = {
        'riasec_raw_scores': {
            'R': 12.5,
            'I': 14.2,
            'A': 8.3,
            'S': 6.5,
            'E': 9.0,
            'C': 11.5
        },
        'holland_code': 'IRC',  # I (14.2) > R (12.5) > C (11.5)
        'riasec_strength_labels': {
            'R': 'High',
            'I': 'Very High',
            'A': 'Medium',
            'S': 'Low',
            'E': 'Medium',
            'C': 'High'
        },
        'bigfive_raw_scores': {
            'O': 21.5,
            'C': 19.0,
            'E': 12.5,
            'A': 16.0,
            'N': 8.5
        },
        'bigfive_strength_labels': {
            'O': 'Very High',
            'C': 'High',
            'E': 'Medium',
            'A': 'High',
            'N': 'Low'
        },
        'behavioral_raw_scores': {
            'motivation_type': 12.5,
            'grit_persistence': 11.0,
            'self_efficacy': 9.5,
            'resilience': 10.0,
            'learning_orientation': 13.0,
            'empathy': 11.5,
            'task_start_tempo': 8.5
        },
        'behavioral_strength_labels': {
            'motivation': 'High',
            'grit': 'High',
            'self_regulation': 'Medium',
            'time_management': 'Medium',
            'growth_mindset': 'Very High'
        },
        'behavioral_flags': {
            'procrastination_risk': False,
            'perfectionism_risk': False,
            'low_grit_risk': False,
            'poor_regulation_risk': False,
            'growth_mindset': True
        },
        'ikigai_zones': {}
    }
    
    return response_data, scores_data


def get_sample_arabic_data():
    """Arabic test data with RTL name"""
    response_data = {
        'student_name': 'محمد رمضان',  # Mohamed Ramadan in Arabic
        'student_email': 'mohamed@example.com',
        'session_id': 'test_session_002'
    }
    
    scores_data = {
        'riasec_raw_scores': {
            'R': 10.0,
            'I': 13.5,
            'A': 11.0,
            'S': 9.5,
            'E': 7.0,
            'C': 8.5
        },
        'holland_code': 'IAS',
        'riasec_strength_labels': {
            'R': 'Medium',
            'I': 'Very High',
            'A': 'High',
            'S': 'Medium',
            'E': 'Low',
            'C': 'Medium'
        },
        'bigfive_raw_scores': {
            'O': 22.0,
            'C': 18.5,
            'E': 10.0,
            'A': 19.0,
            'N': 7.0
        },
        'bigfive_strength_labels': {
            'O': 'Very High',
            'C': 'High',
            'E': 'Medium',
            'A': 'Very High',
            'N': 'Low'
        },
        'behavioral_raw_scores': {
            'motivation_type': 13.5,
            'grit_persistence': 12.0,
            'self_efficacy': 11.0,
            'resilience': 12.5,
            'learning_orientation': 14.0,
            'empathy': 13.0,
            'task_start_tempo': 10.5
        },
        'behavioral_strength_labels': {
            'motivation': 'Very High',
            'grit': 'High',
            'self_regulation': 'High',
            'time_management': 'High',
            'growth_mindset': 'Very High'
        },
        'behavioral_flags': {
            'procrastination_risk': False,
            'perfectionism_risk': False,
            'low_grit_risk': False,
            'poor_regulation_risk': False,
            'growth_mindset': True
        },
        'ikigai_zones': {}
    }
    
    return response_data, scores_data


def test_v2_template():
    """Test V1 PDF generation with freemium model"""
    print("🧪 Testing V1 PDF Generation (Freemium Model)...")
    print("=" * 60)
    
    # Test 1: English version (Premium)
    print("\n📄 Test 1: Generating English Premium PDF...")
    response_data, scores_data = get_sample_english_data()
    
    try:
        pdf_buffer = generate_pdf_report(
            response_data=response_data,
            scores_data=scores_data,
            is_free_version=False,
            checkout_url='https://carhythm.com/paid',
            discount_code='LAUNCH50'
        )
        
        # Save to file
        output_file = f'test_v1_english_premium_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        with open(output_file, 'wb') as f:
            f.write(pdf_buffer.read())
        
        file_size = os.path.getsize(output_file)
        print(f"✅ English PDF generated successfully!")
        print(f"   📦 File: {output_file}")
        print(f"   📊 Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
        
        # Check for key content
        with open(output_file, 'rb') as f:
            content = f.read()
            checks = {
                'QR Code': b'/Type /XObject' in content,
                'Fonts embedded': b'FontFile' in content,
                'Multiple pages': content.count(b'/Type /Page') >= 4,
            }
            
            print("   🔍 Content checks:")
            for check, result in checks.items():
                status = "✓" if result else "✗"
                print(f"      {status} {check}")
        
    except Exception as e:
        print(f"❌ Error generating English PDF: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Arabic version (Premium with RTL name)
    print("\n📄 Test 2: Generating Arabic Premium PDF (RTL name)...")
    response_data, scores_data = get_sample_arabic_data()
    
    try:
        pdf_buffer = generate_pdf_report(
            response_data=response_data,
            scores_data=scores_data,
            is_free_version=False,
            checkout_url='https://carhythm.com/paid',
            discount_code='LAUNCH50'
        )
        
        # Save to file
        output_file = f'test_v1_arabic_premium_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        with open(output_file, 'wb') as f:
            f.write(pdf_buffer.read())
        
        file_size = os.path.getsize(output_file)
        print(f"✅ Arabic PDF generated successfully!")
        print(f"   📦 File: {output_file}")
        print(f"   📊 Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
        
        # Check for RTL content
        with open(output_file, 'rb') as f:
            content = f.read()
            has_arabic = any(0x0600 <= b <= 0x06FF for b in content if b < 256)
            print(f"   🔍 RTL check: {'✓ Arabic characters detected' if has_arabic else '✗ No Arabic detected'}")
        
    except Exception as e:
        print(f"❌ Error generating Arabic PDF: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Free version with blurred sections
    print("\n📄 Test 3: Generating Free Version PDF (with blur + QR codes)...")
    response_data, scores_data = get_sample_english_data()
    
    try:
        pdf_buffer = generate_pdf_report(
            response_data=response_data,
            scores_data=scores_data,
            is_free_version=True,  # Free version with blurred sections
            checkout_url='https://carhythm.com/paid',
            discount_code='LAUNCH50'
        )
        
        output_file = f'test_v1_free_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        with open(output_file, 'wb') as f:
            f.write(pdf_buffer.read())
        
        file_size = os.path.getsize(output_file)
        print(f"✅ Free version PDF generated successfully!")
        print(f"   📦 File: {output_file}")
        print(f"   📊 Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
        
    except Exception as e:
        print(f"❌ Error generating V1 PDF: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("\n📝 Next steps:")
    print("   1. Open generated PDFs to verify Holland Code is correct")
    print("   2. Check that I (14.2) > R (12.5) > C (11.5) shows as 'IRC'")
    print("   3. Verify free version has 4 blurred sections + QR codes")
    print("   4. Check Arabic RTL name rendering")
    print("   5. Compare premium vs free layouts")


if __name__ == '__main__':
    test_v2_template()
