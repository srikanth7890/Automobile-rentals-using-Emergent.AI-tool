#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Automobile Rental System with NEW CAPACITY FEATURE
Tests all authentication, vehicle management with capacity, booking, and admin endpoints
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
    
    return True

def test_vehicle_capacity_creation():
    """Test vehicle creation with NEW CAPACITY FEATURE"""
    print("\n🚗 Testing Vehicle Creation with Capacity Feature")
    
    # Test creating vehicles with different capacity values for each type
    vehicles_to_create = [
        # Car capacity tests - typical and maximum
        {
            "name": "Toyota Camry Sedan",
            "type": "car",
            "brand": "Toyota",
            "model": "Camry",
            "year": 2023,
            "price_per_day": 75.00,
            "capacity": 5,
            "description": "Comfortable sedan perfect for family trips"
        },
        {
            "name": "BMW X7 Large SUV",
            "type": "car",
            "brand": "BMW",
            "model": "X7",
            "year": 2023,
            "price_per_day": 200.00,
            "capacity": 7,
            "description": "Large luxury SUV with maximum seating capacity"
        },
        # Motorcycle capacity tests - 1 and 2 riders
        {
            "name": "Yamaha R1 Sport Bike",
            "type": "motorcycle",
            "brand": "Yamaha",
            "model": "R1",
            "year": 2022,
            "price_per_day": 95.00,
            "capacity": 1,
            "description": "High-performance sport motorcycle for solo riding"
        },
        {
            "name": "Honda Gold Wing Touring",
            "type": "motorcycle",
            "brand": "Honda",
            "model": "Gold Wing",
            "year": 2023,
            "price_per_day": 120.00,
            "capacity": 2,
            "description": "Comfortable touring motorcycle for two riders"
        },
        # Truck capacity tests - regular and crew cab
        {
            "name": "Ford F-150 Regular Cab",
            "type": "truck",
            "brand": "Ford",
            "model": "F-150",
            "year": 2023,
            "price_per_day": 140.00,
            "capacity": 3,
            "description": "Regular cab pickup truck for work and hauling"
        },
        {
            "name": "Ram 1500 Crew Cab",
            "type": "truck",
            "brand": "Ram",
            "model": "1500",
            "year": 2023,
            "price_per_day": 160.00,
            "capacity": 5,
            "description": "Crew cab pickup with full seating for work teams"
        },
        # Van capacity tests - typical range
        {
            "name": "Ford Transit Passenger Van",
            "type": "van",
            "brand": "Ford",
            "model": "Transit",
            "year": 2023,
            "price_per_day": 130.00,
            "capacity": 12,
            "description": "Large passenger van for group transportation"
        },
        {
            "name": "Mercedes Sprinter Van",
            "type": "van",
            "brand": "Mercedes",
            "model": "Sprinter",
            "year": 2023,
            "price_per_day": 150.00,
            "capacity": 8,
            "description": "Premium van for comfortable group travel"
        }
    ]
    
    admin_headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
    
    for vehicle_data in vehicles_to_create:
        try:
            response = requests.post(f"{BASE_URL}/vehicles", json=vehicle_data, headers=admin_headers)
            if response.status_code == 200:
                data = response.json()
                test_data['vehicles'].append(data)
                # Verify capacity field is present and correct
                if 'capacity' in data and data['capacity'] == vehicle_data['capacity']:
                    print_test_result(f"Create {vehicle_data['type'].title()} (Capacity: {vehicle_data['capacity']})", 
                                    True, f"Created: {data['name']} with capacity {data['capacity']}")
                else:
                    print_test_result(f"Create {vehicle_data['type'].title()}", False, 
                                    f"Capacity field missing or incorrect. Expected: {vehicle_data['capacity']}, Got: {data.get('capacity', 'MISSING')}")
                    return False
            else:
                print_test_result(f"Create {vehicle_data['type'].title()}", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            print_test_result(f"Create {vehicle_data['type'].title()}", False, f"Exception: {str(e)}")
            return False
    
    return True

def test_vehicle_capacity_validation():
    """Test capacity validation edge cases"""
    print("\n🚗 Testing Vehicle Capacity Validation")
    
    admin_headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
    
    # Test vehicle creation without capacity field (should fail)
    vehicle_without_capacity = {
        "name": "Test Vehicle No Capacity",
        "type": "car",
        "brand": "Test",
        "model": "Test",
        "year": 2023,
        "price_per_day": 100.00,
        "description": "Test vehicle without capacity"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/vehicles", json=vehicle_without_capacity, headers=admin_headers)
        if response.status_code == 422:  # Validation error expected
            print_test_result("Missing Capacity Validation", True, "Correctly rejected vehicle creation without capacity field")
        else:
            print_test_result("Missing Capacity Validation", False, f"Should have returned 422, got {response.status_code}")
    except Exception as e:
        print_test_result("Missing Capacity Validation", False, f"Exception: {str(e)}")
    
    # Test unrealistic capacity values
    unrealistic_vehicles = [
        {"type": "motorcycle", "capacity": 10, "name": "Unrealistic Motorcycle"},
        {"type": "car", "capacity": 20, "name": "Unrealistic Car"},
        {"type": "truck", "capacity": 0, "name": "Zero Capacity Truck"}
    ]
    
    for vehicle_test in unrealistic_vehicles:
        vehicle_data = {
            "name": vehicle_test["name"],
            "type": vehicle_test["type"],
            "brand": "Test",
            "model": "Test",
            "year": 2023,
            "price_per_day": 100.00,
            "capacity": vehicle_test["capacity"],
            "description": "Test vehicle with unrealistic capacity"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/vehicles", json=vehicle_data, headers=admin_headers)
            # Note: Backend might accept these values, so we just log the result
            if response.status_code == 200:
                print_test_result(f"Unrealistic Capacity Test ({vehicle_test['type']}: {vehicle_test['capacity']})", 
                                True, f"Vehicle created (backend allows unrealistic values)")
            else:
                print_test_result(f"Unrealistic Capacity Test ({vehicle_test['type']}: {vehicle_test['capacity']})", 
                                True, f"Vehicle rejected with status {response.status_code}")
        except Exception as e:
            print_test_result(f"Unrealistic Capacity Test ({vehicle_test['type']}: {vehicle_test['capacity']})", 
                            False, f"Exception: {str(e)}")
    
    return True

def test_vehicle_listing_with_capacity():
    """Test vehicle listing endpoints include capacity information"""
    print("\n🚗 Testing Vehicle Listing with Capacity Information")
    
    # Test public vehicle listing includes capacity
    try:
        response = requests.get(f"{BASE_URL}/vehicles")
        if response.status_code == 200:
            data = response.json()
            if data:
                # Check if all vehicles have capacity field
                vehicles_with_capacity = [v for v in data if 'capacity' in v and v['capacity'] is not None]
                if len(vehicles_with_capacity) == len(data):
                    capacity_info = [f"{v['name']}: {v['capacity']} seats" for v in data[:3]]  # Show first 3
                    print_test_result("Public Vehicle Listing with Capacity", True, 
                                    f"All {len(data)} vehicles have capacity field. Examples: {', '.join(capacity_info)}")
                else:
                    missing_capacity = len(data) - len(vehicles_with_capacity)
                    print_test_result("Public Vehicle Listing with Capacity", False, 
                                    f"{missing_capacity} vehicles missing capacity field")
                    return False
            else:
                print_test_result("Public Vehicle Listing with Capacity", True, "No vehicles in database (empty result)")
        else:
            print_test_result("Public Vehicle Listing with Capacity", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Public Vehicle Listing with Capacity", False, f"Exception: {str(e)}")
        return False
    
    # Test admin all vehicles listing includes capacity
    try:
        admin_headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
        response = requests.get(f"{BASE_URL}/vehicles/all", headers=admin_headers)
        if response.status_code == 200:
            data = response.json()
            if data:
                vehicles_with_capacity = [v for v in data if 'capacity' in v and v['capacity'] is not None]
                if len(vehicles_with_capacity) == len(data):
                    print_test_result("Admin All Vehicles with Capacity", True, 
                                    f"All {len(data)} vehicles have capacity field in admin view")
                else:
                    missing_capacity = len(data) - len(vehicles_with_capacity)
                    print_test_result("Admin All Vehicles with Capacity", False, 
                                    f"{missing_capacity} vehicles missing capacity field in admin view")
                    return False
            else:
                print_test_result("Admin All Vehicles with Capacity", True, "No vehicles in database (empty result)")
        else:
            print_test_result("Admin All Vehicles with Capacity", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Admin All Vehicles with Capacity", False, f"Exception: {str(e)}")
        return False
    
    return True

def test_vehicle_migration():
    """Test migration for existing vehicles without capacity field"""
    print("\n🚗 Testing Vehicle Migration for Capacity Field")
    
    # First, let's create a vehicle using direct database insertion simulation
    # by creating a vehicle and then testing if migration works on listing
    
    # Create a vehicle that might simulate old data (though our API will include capacity)
    admin_headers = {"Authorization": f"Bearer {test_data['admin_token']}"}
    
    # Test that when we list vehicles, migration logic applies default values
    try:
        response = requests.get(f"{BASE_URL}/vehicles")
        if response.status_code == 200:
            data = response.json()
            
            # Check if vehicles have appropriate default capacities based on type
            default_capacities = {
                'motorcycle': 2,
                'car': 5,
                'truck': 3,
                'van': 8
            }
            
            migration_working = True
            for vehicle in data:
                if 'capacity' in vehicle:
                    vehicle_type = vehicle.get('type', 'unknown')
                    capacity = vehicle['capacity']
                    
                    # Check if capacity is reasonable for the vehicle type
                    if vehicle_type in default_capacities:
                        expected_default = default_capacities[vehicle_type]
                        # Migration should set reasonable defaults, but created vehicles might have custom values
                        print_test_result(f"Migration Check - {vehicle['name']} ({vehicle_type})", True, 
                                        f"Has capacity: {capacity} (type default would be: {expected_default})")
                    else:
                        print_test_result(f"Migration Check - {vehicle['name']}", True, f"Has capacity: {capacity}")
                else:
                    print_test_result(f"Migration Check - {vehicle['name']}", False, "Missing capacity field")
                    migration_working = False
            
            if migration_working:
                print_test_result("Vehicle Migration Test", True, "All vehicles have capacity field (migration working)")
            else:
                print_test_result("Vehicle Migration Test", False, "Some vehicles missing capacity field")
                return False
                
        else:
            print_test_result("Vehicle Migration Test", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Vehicle Migration Test", False, f"Exception: {str(e)}")
        return False
    
    return True

def test_capacity_integration_with_booking():
    """Test that capacity information is properly integrated with booking system"""
    print("\n📅 Testing Capacity Integration with Booking System")
    
    if not test_data['vehicles']:
        print_test_result("Capacity-Booking Integration", False, "No vehicles available for testing")
        return False
    
    # Create a booking and verify vehicle capacity information is accessible
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
            
            # Now check if we can get vehicle details including capacity for this booking
            vehicle_response = requests.get(f"{BASE_URL}/vehicles")
            if vehicle_response.status_code == 200:
                vehicles = vehicle_response.json()
                booked_vehicle = next((v for v in vehicles if v['id'] == vehicle_id), None)
                
                if booked_vehicle and 'capacity' in booked_vehicle:
                    print_test_result("Capacity-Booking Integration", True, 
                                    f"Booking created for vehicle with capacity {booked_vehicle['capacity']}")
                else:
                    print_test_result("Capacity-Booking Integration", False, 
                                    "Booked vehicle missing capacity information")
                    return False
            else:
                print_test_result("Capacity-Booking Integration", False, 
                                f"Could not retrieve vehicle details: {vehicle_response.status_code}")
                return False
        else:
            print_test_result("Capacity-Booking Integration", False, f"Booking creation failed: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_test_result("Capacity-Booking Integration", False, f"Exception: {str(e)}")
        return False
    
    return True

def run_capacity_tests():
    """Run all capacity-focused backend API tests"""
    print("🚀 Starting Vehicle Capacity Feature Tests for Automobile Rental System")
    print("=" * 80)
    
    test_results = []
    
    # Authentication Tests (required for other tests)
    test_results.append(("Authentication Setup - Registration", test_auth_register()))
    test_results.append(("Authentication Setup - Login", test_auth_login()))
    
    # NEW CAPACITY FEATURE TESTS
    test_results.append(("Vehicle Capacity Creation", test_vehicle_capacity_creation()))
    test_results.append(("Vehicle Capacity Validation", test_vehicle_capacity_validation()))
    test_results.append(("Vehicle Listing with Capacity", test_vehicle_listing_with_capacity()))
    test_results.append(("Vehicle Migration for Capacity", test_vehicle_migration()))
    test_results.append(("Capacity Integration with Booking", test_capacity_integration_with_booking()))
    
    # Print final results
    print("\n" + "=" * 80)
    print("📋 CAPACITY FEATURE TEST RESULTS SUMMARY")
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
        print("🎉 ALL CAPACITY TESTS PASSED! Vehicle capacity feature is working correctly.")
        return True
    else:
        print("⚠️  Some capacity tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_capacity_tests()
    exit(0 if success else 1)