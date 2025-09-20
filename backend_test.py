#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Automobile Rental System
Tests all authentication, vehicle management, booking, and admin endpoints
"""

import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
from PIL import Image
import io

# Load environment variables
from dotenv import load_dotenv
load_dotenv('/app/frontend/.env')

# Get base URL from environment
REACT_APP_BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL')
if not REACT_APP_BACKEND_URL:
    print("❌ REACT_APP_BACKEND_URL not found in frontend/.env")
    exit(1)

BASE_URL = f"{REACT_APP_BACKEND_URL}/api"
print(f"🔗 Testing API at: {BASE_URL}")

# Test data storage
test_data = {
    'admin_token': None,
    'customer_token': None,
    'admin_user': None,
    'customer_user': None,
    'vehicles': [],
    'bookings': []
}

def print_test_result(test_name, success, details=""):
    status = "✅" if success else "❌"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")
    if not success:
        print()

def test_auth_register():
    """Test user registration for both admin and customer"""
    print("\n🔐 Testing Authentication - Registration")
    
    # Test admin registration
    admin_data = {
        "email": "sarah.admin@rentalcorp.com",
        "name": "Sarah Johnson",
        "phone": "+1-555-0123",
        "password": "SecureAdmin2024!",
        "role": "admin"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
        if response.status_code == 200:
            data = response.json()
            test_data['admin_token'] = data['token']
            test_data['admin_user'] = data['user']
            print_test_result("Admin Registration", True, f"Admin user created: {data['user']['name']}")
        else:
            print_test_result("Admin Registration", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Admin Registration", False, f"Exception: {str(e)}")
        return False
    
    # Test customer registration
    customer_data = {
        "email": "mike.customer@email.com",
        "name": "Mike Rodriguez",
        "phone": "+1-555-0456",
        "password": "CustomerPass123!",
        "role": "customer"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=customer_data)
        if response.status_code == 200:
            data = response.json()
            test_data['customer_token'] = data['token']
            test_data['customer_user'] = data['user']
            print_test_result("Customer Registration", True, f"Customer user created: {data['user']['name']}")
        else:
            print_test_result("Customer Registration", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Customer Registration", False, f"Exception: {str(e)}")
        return False
    
    # Test duplicate email registration
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
        if response.status_code == 400:
            print_test_result("Duplicate Email Validation", True, "Correctly rejected duplicate email")
        else:
            print_test_result("Duplicate Email Validation", False, f"Should have returned 400, got {response.status_code}")
    except Exception as e:
        print_test_result("Duplicate Email Validation", False, f"Exception: {str(e)}")
    
    return True

def test_auth_login():
    """Test user login for both roles"""
    print("\n🔐 Testing Authentication - Login")
    
    # Test admin login
    admin_login = {
        "email": "sarah.admin@rentalcorp.com",
        "password": "SecureAdmin2024!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=admin_login)
        if response.status_code == 200:
            data = response.json()
            print_test_result("Admin Login", True, f"Admin logged in: {data['user']['name']}")
        else:
            print_test_result("Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Admin Login", False, f"Exception: {str(e)}")
        return False
    
    # Test customer login
    customer_login = {
        "email": "mike.customer@email.com",
        "password": "CustomerPass123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=customer_login)
        if response.status_code == 200:
            data = response.json()
            print_test_result("Customer Login", True, f"Customer logged in: {data['user']['name']}")
        else:
            print_test_result("Customer Login", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Customer Login", False, f"Exception: {str(e)}")
        return False
    
    # Test invalid credentials
    try:
        invalid_login = {"email": "sarah.admin@rentalcorp.com", "password": "wrongpassword"}
        response = requests.post(f"{BASE_URL}/auth/login", json=invalid_login)
        if response.status_code == 401:
            print_test_result("Invalid Credentials Validation", True, "Correctly rejected invalid credentials")
        else:
            print_test_result("Invalid Credentials Validation", False, f"Should have returned 401, got {response.status_code}")
    except Exception as e:
        print_test_result("Invalid Credentials Validation", False, f"Exception: {str(e)}")
    
    return True

def test_auth_me():
    """Test authenticated user info retrieval"""
    print("\n🔐 Testing Authentication - User Info")
    
    # Test admin user info
    try:
        headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_test_result("Admin User Info", True, f"Retrieved admin info: {data['name']} ({data['role']})")
        else:
            print_test_result("Admin User Info", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Admin User Info", False, f"Exception: {str(e)}")
        return False
    
    # Test customer user info
    try:
        headers = {"Authorization": f"Bearer {test_data['customer_token']}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_test_result("Customer User Info", True, f"Retrieved customer info: {data['name']} ({data['role']})")
        else:
            print_test_result("Customer User Info", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Customer User Info", False, f"Exception: {str(e)}")
        return False
    
    # Test unauthorized access
    try:
        response = requests.get(f"{BASE_URL}/auth/me")
        if response.status_code == 403:
            print_test_result("Unauthorized Access Validation", True, "Correctly rejected request without token")
        else:
            print_test_result("Unauthorized Access Validation", False, f"Should have returned 403, got {response.status_code}")
    except Exception as e:
        print_test_result("Unauthorized Access Validation", False, f"Exception: {str(e)}")
    
    return True

def test_vehicle_management():
    """Test vehicle CRUD operations"""
    print("\n🚗 Testing Vehicle Management")
    
    # Test creating vehicles (admin only)
    vehicles_to_create = [
        {
            "name": "BMW X5 Premium SUV",
            "type": "car",
            "brand": "BMW",
            "model": "X5",
            "year": 2023,
            "price_per_day": 150.00,
            "description": "Luxury SUV with premium features, perfect for family trips and business travel"
        },
        {
            "name": "Harley Davidson Street 750",
            "type": "motorcycle",
            "brand": "Harley Davidson",
            "model": "Street 750",
            "year": 2022,
            "price_per_day": 85.00,
            "description": "Classic motorcycle for adventure seekers and city cruising"
        },
        {
            "name": "Ford Transit Cargo Van",
            "type": "van",
            "brand": "Ford",
            "model": "Transit",
            "year": 2023,
            "price_per_day": 120.00,
            "description": "Spacious cargo van ideal for moving and delivery services"
        },
        {
            "name": "Chevrolet Silverado 2500HD",
            "type": "truck",
            "brand": "Chevrolet",
            "model": "Silverado 2500HD",
            "year": 2023,
            "price_per_day": 180.00,
            "description": "Heavy-duty pickup truck for construction and hauling needs"
        }
    ]
    
    admin_headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
    
    for vehicle_data in vehicles_to_create:
        try:
            response = requests.post(f"{BASE_URL}/vehicles", json=vehicle_data, headers=admin_headers)
            if response.status_code == 200:
                data = response.json()
                test_data['vehicles'].append(data)
                print_test_result(f"Create {vehicle_data['type'].title()}", True, f"Created: {data['name']}")
            else:
                print_test_result(f"Create {vehicle_data['type'].title()}", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            print_test_result(f"Create {vehicle_data['type'].title()}", False, f"Exception: {str(e)}")
            return False
    
    # Test customer cannot create vehicles
    try:
        customer_headers = {"Authorization": f"Bearer {test_data['customer_token']}"}
        response = requests.post(f"{BASE_URL}/vehicles", json=vehicles_to_create[0], headers=customer_headers)
        if response.status_code == 403:
            print_test_result("Customer Vehicle Creation Blocked", True, "Correctly blocked customer from creating vehicles")
        else:
            print_test_result("Customer Vehicle Creation Blocked", False, f"Should have returned 403, got {response.status_code}")
    except Exception as e:
        print_test_result("Customer Vehicle Creation Blocked", False, f"Exception: {str(e)}")
    
    return True

def test_vehicle_listing():
    """Test vehicle listing endpoints"""
    print("\n🚗 Testing Vehicle Listing")
    
    # Test public vehicle listing
    try:
        response = requests.get(f"{BASE_URL}/vehicles")
        if response.status_code == 200:
            data = response.json()
            print_test_result("Public Vehicle Listing", True, f"Retrieved {len(data)} available vehicles")
        else:
            print_test_result("Public Vehicle Listing", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Public Vehicle Listing", False, f"Exception: {str(e)}")
        return False
    
    # Test admin all vehicles listing
    try:
        admin_headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
        response = requests.get(f"{BASE_URL}/vehicles/all", headers=admin_headers)
        if response.status_code == 200:
            data = response.json()
            print_test_result("Admin All Vehicles Listing", True, f"Retrieved {len(data)} total vehicles")
        else:
            print_test_result("Admin All Vehicles Listing", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Admin All Vehicles Listing", False, f"Exception: {str(e)}")
        return False
    
    # Test customer cannot access admin vehicle listing
    try:
        customer_headers = {"Authorization": f"Bearer {test_data['customer_token']}"}
        response = requests.get(f"{BASE_URL}/vehicles/all", headers=customer_headers)
        if response.status_code == 403:
            print_test_result("Customer Admin Access Blocked", True, "Correctly blocked customer from admin vehicle listing")
        else:
            print_test_result("Customer Admin Access Blocked", False, f"Should have returned 403, got {response.status_code}")
    except Exception as e:
        print_test_result("Customer Admin Access Blocked", False, f"Exception: {str(e)}")
    
    return True

def test_vehicle_image_upload():
    """Test vehicle image upload"""
    print("\n🚗 Testing Vehicle Image Upload")
    
    if not test_data['vehicles']:
        print_test_result("Vehicle Image Upload", False, "No vehicles available for testing")
        return False
    
    # Create a test image
    try:
        img = Image.new('RGB', (300, 200), color='blue')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        
        vehicle_id = test_data['vehicles'][0]['id']
        admin_headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
        
        files = {'file': ('test_vehicle.jpg', img_buffer, 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/vehicles/{vehicle_id}/upload-image", 
                               files=files, headers=admin_headers)
        
        if response.status_code == 200:
            data = response.json()
            print_test_result("Vehicle Image Upload", True, f"Image uploaded: {data['image_url']}")
        else:
            print_test_result("Vehicle Image Upload", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Vehicle Image Upload", False, f"Exception: {str(e)}")
        return False
    
    return True

def test_booking_system():
    """Test booking creation and management"""
    print("\n📅 Testing Booking System")
    
    if not test_data['vehicles']:
        print_test_result("Booking System", False, "No vehicles available for booking")
        return False
    
    # Test booking creation
    vehicle_id = test_data['vehicles'][0]['id']
    start_date = datetime.now() + timedelta(days=7)
    end_date = start_date + timedelta(days=3)
    
    booking_data = {
        "vehicle_id": vehicle_id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    
    try:
        customer_headers = {"Authorization": f"Bearer {test_data['customer_token']}"}
        response = requests.post(f"{BASE_URL}/bookings", json=booking_data, headers=customer_headers)
        if response.status_code == 200:
            data = response.json()
            test_data['bookings'].append(data)
            print_test_result("Booking Creation", True, f"Booking created: {data['id']}, Amount: ${data['total_amount']}")
        else:
            print_test_result("Booking Creation", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Booking Creation", False, f"Exception: {str(e)}")
        return False
    
    # Test booking conflict detection
    try:
        conflicting_booking = {
            "vehicle_id": vehicle_id,
            "start_date": (start_date + timedelta(days=1)).isoformat(),
            "end_date": (end_date + timedelta(days=1)).isoformat()
        }
        response = requests.post(f"{BASE_URL}/bookings", json=conflicting_booking, headers=customer_headers)
        if response.status_code == 400:
            print_test_result("Booking Conflict Detection", True, "Correctly detected booking conflict")
        else:
            print_test_result("Booking Conflict Detection", False, f"Should have returned 400, got {response.status_code}")
    except Exception as e:
        print_test_result("Booking Conflict Detection", False, f"Exception: {str(e)}")
    
    return True

def test_booking_listing():
    """Test booking listing endpoints"""
    print("\n📅 Testing Booking Listing")
    
    # Test customer booking history
    try:
        customer_headers = {"Authorization": f"Bearer {test_data['customer_token']}"}
        response = requests.get(f"{BASE_URL}/bookings", headers=customer_headers)
        if response.status_code == 200:
            data = response.json()
            print_test_result("Customer Booking History", True, f"Retrieved {len(data)} customer bookings")
        else:
            print_test_result("Customer Booking History", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Customer Booking History", False, f"Exception: {str(e)}")
        return False
    
    # Test admin all bookings
    try:
        admin_headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
        response = requests.get(f"{BASE_URL}/bookings/all", headers=admin_headers)
        if response.status_code == 200:
            data = response.json()
            print_test_result("Admin All Bookings", True, f"Retrieved {len(data)} total bookings")
        else:
            print_test_result("Admin All Bookings", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Admin All Bookings", False, f"Exception: {str(e)}")
        return False
    
    return True

def test_booking_status_management():
    """Test booking status updates"""
    print("\n📅 Testing Booking Status Management")
    
    if not test_data['bookings']:
        print_test_result("Booking Status Management", False, "No bookings available for testing")
        return False
    
    booking_id = test_data['bookings'][0]['id']
    admin_headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
    
    # Test status update
    try:
        response = requests.put(f"{BASE_URL}/bookings/{booking_id}/status?status=confirmed&payment_status=paid", 
                              headers=admin_headers)
        if response.status_code == 200:
            print_test_result("Booking Status Update", True, "Successfully updated booking status to confirmed/paid")
        else:
            print_test_result("Booking Status Update", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Booking Status Update", False, f"Exception: {str(e)}")
        return False
    
    # Test customer cannot update booking status
    try:
        customer_headers = {"Authorization": f"Bearer {test_data['customer_token']}"}
        response = requests.put(f"{BASE_URL}/bookings/{booking_id}/status?status=cancelled", 
                              headers=customer_headers)
        if response.status_code == 403:
            print_test_result("Customer Status Update Blocked", True, "Correctly blocked customer from updating booking status")
        else:
            print_test_result("Customer Status Update Blocked", False, f"Should have returned 403, got {response.status_code}")
    except Exception as e:
        print_test_result("Customer Status Update Blocked", False, f"Exception: {str(e)}")
    
    return True

def test_dashboard_stats():
    """Test admin dashboard statistics"""
    print("\n📊 Testing Dashboard Statistics")
    
    try:
        admin_headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
        response = requests.get(f"{BASE_URL}/dashboard/stats", headers=admin_headers)
        if response.status_code == 200:
            data = response.json()
            required_fields = ['total_vehicles', 'available_vehicles', 'total_bookings', 
                             'active_bookings', 'total_customers', 'total_revenue']
            
            missing_fields = [field for field in required_fields if field not in data]
            if not missing_fields:
                print_test_result("Dashboard Statistics", True, 
                                f"Stats: {data['total_vehicles']} vehicles, {data['total_bookings']} bookings, ${data['total_revenue']} revenue")
            else:
                print_test_result("Dashboard Statistics", False, f"Missing fields: {missing_fields}")
                return False
        else:
            print_test_result("Dashboard Statistics", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Dashboard Statistics", False, f"Exception: {str(e)}")
        return False
    
    # Test customer cannot access dashboard
    try:
        customer_headers = {"Authorization": f"Bearer {test_data['customer_token']}"}
        response = requests.get(f"{BASE_URL}/dashboard/stats", headers=customer_headers)
        if response.status_code == 403:
            print_test_result("Customer Dashboard Access Blocked", True, "Correctly blocked customer from dashboard access")
        else:
            print_test_result("Customer Dashboard Access Blocked", False, f"Should have returned 403, got {response.status_code}")
    except Exception as e:
        print_test_result("Customer Dashboard Access Blocked", False, f"Exception: {str(e)}")
    
    return True

def test_vehicle_availability():
    """Test vehicle availability checking"""
    print("\n🚗 Testing Vehicle Availability")
    
    if not test_data['vehicles']:
        print_test_result("Vehicle Availability", False, "No vehicles available for testing")
        return False
    
    vehicle_id = test_data['vehicles'][0]['id']
    
    # Test availability for free dates
    try:
        start_date = (datetime.now() + timedelta(days=30)).isoformat()
        end_date = (datetime.now() + timedelta(days=33)).isoformat()
        
        response = requests.get(f"{BASE_URL}/vehicles/{vehicle_id}/availability?start_date={start_date}&end_date={end_date}")
        if response.status_code == 200:
            data = response.json()
            print_test_result("Vehicle Availability Check", True, f"Availability: {data['available']}")
        else:
            print_test_result("Vehicle Availability Check", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Vehicle Availability Check", False, f"Exception: {str(e)}")
        return False
    
    return True

def test_vehicle_deletion():
    """Test vehicle deletion (admin only)"""
    print("\n🚗 Testing Vehicle Deletion")
    
    if len(test_data['vehicles']) < 2:
        print_test_result("Vehicle Deletion", False, "Need at least 2 vehicles for deletion test")
        return False
    
    # Delete the last vehicle
    vehicle_to_delete = test_data['vehicles'][-1]
    vehicle_id = vehicle_to_delete['id']
    
    try:
        admin_headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
        response = requests.delete(f"{BASE_URL}/vehicles/{vehicle_id}", headers=admin_headers)
        if response.status_code == 200:
            print_test_result("Vehicle Deletion", True, f"Successfully deleted vehicle: {vehicle_to_delete['name']}")
            test_data['vehicles'].pop()  # Remove from our test data
        else:
            print_test_result("Vehicle Deletion", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Vehicle Deletion", False, f"Exception: {str(e)}")
        return False
    
    # Test customer cannot delete vehicles
    try:
        customer_headers = {"Authorization": f"Bearer {test_data['customer_token']}"}
        response = requests.delete(f"{BASE_URL}/vehicles/{test_data['vehicles'][0]['id']}", headers=customer_headers)
        if response.status_code == 403:
            print_test_result("Customer Vehicle Deletion Blocked", True, "Correctly blocked customer from deleting vehicles")
        else:
            print_test_result("Customer Vehicle Deletion Blocked", False, f"Should have returned 403, got {response.status_code}")
    except Exception as e:
        print_test_result("Customer Vehicle Deletion Blocked", False, f"Exception: {str(e)}")
    
    return True

def run_all_tests():
    """Run all backend API tests"""
    print("🚀 Starting Comprehensive Backend API Tests for Automobile Rental System")
    print("=" * 80)
    
    test_results = []
    
    # Authentication Tests
    test_results.append(("User Authentication System - Registration", test_auth_register()))
    test_results.append(("User Authentication System - Login", test_auth_login()))
    test_results.append(("User Authentication System - User Info", test_auth_me()))
    
    # Vehicle Management Tests
    test_results.append(("Vehicle Management API - Creation", test_vehicle_management()))
    test_results.append(("Vehicle Management API - Listing", test_vehicle_listing()))
    test_results.append(("Vehicle Management API - Image Upload", test_vehicle_image_upload()))
    test_results.append(("Vehicle Management API - Availability Check", test_vehicle_availability()))
    test_results.append(("Vehicle Management API - Deletion", test_vehicle_deletion()))
    
    # Booking System Tests
    test_results.append(("Booking System API - Creation", test_booking_system()))
    test_results.append(("Booking System API - Listing", test_booking_listing()))
    test_results.append(("Booking System API - Status Management", test_booking_status_management()))
    
    # Admin Dashboard Tests
    test_results.append(("Admin Dashboard API - Statistics", test_dashboard_stats()))
    
    # Print final results
    print("\n" + "=" * 80)
    print("📋 FINAL TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed_tests = []
    failed_tests = []
    
    for test_name, result in test_results:
        if result:
            passed_tests.append(test_name)
        else:
            failed_tests.append(test_name)
    
    print(f"\n✅ PASSED TESTS ({len(passed_tests)}):")
    for test in passed_tests:
        print(f"   ✅ {test}")
    
    if failed_tests:
        print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"   ❌ {test}")
    
    print(f"\n📊 OVERALL RESULTS: {len(passed_tests)}/{len(test_results)} tests passed")
    
    if len(failed_tests) == 0:
        print("🎉 ALL TESTS PASSED! Backend API is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)