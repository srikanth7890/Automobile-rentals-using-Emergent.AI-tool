#!/usr/bin/env python3
"""
Specific test for booking conflict detection logic
"""

import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv('/app/frontend/.env')
REACT_APP_BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL')
BASE_URL = f"{REACT_APP_BACKEND_URL}/api"

def test_booking_conflict_logic():
    """Test the booking conflict detection in detail"""
    print("🔍 Testing Booking Conflict Detection Logic")
    
    # First, let's get the existing bookings to understand the current state
    admin_data = {
        "email": "sarah.admin@rentalcorp.com",
        "password": "SecureAdmin2024!"
    }
    
    admin_response = requests.post(f"{BASE_URL}/auth/login", json=admin_data)
    admin_token = admin_response.json()['token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get all bookings to see current state
    bookings_response = requests.get(f"{BASE_URL}/bookings/all", headers=admin_headers)
    bookings = bookings_response.json()
    
    print(f"Current bookings in system: {len(bookings)}")
    for booking in bookings:
        print(f"  - Booking {booking['id'][:8]}... Status: {booking['status']}, Vehicle: {booking['vehicle_id'][:8]}...")
        print(f"    Dates: {booking['start_date']} to {booking['end_date']}")
    
    if bookings:
        # Try to update the first booking to 'confirmed' status
        first_booking = bookings[0]
        print(f"\n📝 Updating booking {first_booking['id'][:8]}... to 'confirmed' status")
        
        update_response = requests.put(
            f"{BASE_URL}/bookings/{first_booking['id']}/status?status=confirmed", 
            headers=admin_headers
        )
        
        if update_response.status_code == 200:
            print("✅ Successfully updated booking to confirmed status")
            
            # Now try to create a conflicting booking
            customer_data = {
                "email": "mike.customer@email.com",
                "password": "CustomerPass123!"
            }
            
            customer_response = requests.post(f"{BASE_URL}/auth/login", json=customer_data)
            customer_token = customer_response.json()['token']
            customer_headers = {"Authorization": f"Bearer {customer_token}"}
            
            # Create overlapping booking
            start_date = datetime.fromisoformat(first_booking['start_date'].replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(first_booking['end_date'].replace('Z', '+00:00'))
            
            overlapping_booking = {
                "vehicle_id": first_booking['vehicle_id'],
                "start_date": (start_date + timedelta(days=1)).isoformat(),
                "end_date": (end_date + timedelta(days=1)).isoformat()
            }
            
            print(f"🔄 Attempting to create overlapping booking for same vehicle...")
            conflict_response = requests.post(f"{BASE_URL}/bookings", json=overlapping_booking, headers=customer_headers)
            
            if conflict_response.status_code == 400:
                print("✅ Booking conflict correctly detected and rejected")
                return True
            else:
                print(f"❌ Booking conflict NOT detected. Status: {conflict_response.status_code}")
                print(f"Response: {conflict_response.text}")
                return False
        else:
            print(f"❌ Failed to update booking status: {update_response.status_code}")
            return False
    else:
        print("❌ No bookings found to test conflict detection")
        return False

if __name__ == "__main__":
    success = test_booking_conflict_logic()
    print(f"\n📊 Conflict detection test: {'PASSED' if success else 'FAILED'}")