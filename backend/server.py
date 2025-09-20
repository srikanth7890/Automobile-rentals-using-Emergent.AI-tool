from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import base64
import aiofiles
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"

class VehicleType(str, Enum):
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    TRUCK = "truck"
    VAN = "van"

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    phone: str
    role: UserRole
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: str
    name: str
    phone: str
    password: str
    role: UserRole = UserRole.CUSTOMER

class UserLogin(BaseModel):
    email: str
    password: str

class Vehicle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: VehicleType
    brand: str
    model: str
    year: int
    price_per_day: float
    capacity: int
    image_url: Optional[str] = None
    description: str
    available: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class VehicleCreate(BaseModel):
    name: str
    type: VehicleType
    brand: str
    model: str
    year: int
    price_per_day: float
    capacity: int
    description: str

class Booking(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    vehicle_id: str
    start_date: datetime
    end_date: datetime
    total_days: int
    total_amount: float
    status: BookingStatus = BookingStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BookingCreate(BaseModel):
    vehicle_id: str
    start_date: datetime
    end_date: datetime

class BookingWithDetails(BaseModel):
    id: str
    user_id: str
    user_name: str
    user_email: str
    vehicle_id: str
    vehicle_name: str
    vehicle_type: str
    start_date: datetime
    end_date: datetime
    total_days: int
    total_amount: float
    status: BookingStatus
    payment_status: PaymentStatus
    created_at: datetime

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str, role: str) -> str:
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.now(timezone.utc) + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_jwt_token(credentials.credentials)
    user = await db.users.find_one({"id": payload["user_id"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def calculate_days(start_date: datetime, end_date: datetime) -> int:
    delta = end_date.date() - start_date.date()
    return max(1, delta.days)

# Routes
@api_router.post("/auth/register", response_model=dict)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    user_dict = user_data.dict()
    del user_dict['password']
    user = User(**user_dict)
    
    # Store in database
    user_doc = user.dict()
    user_doc['password'] = hashed_password
    await db.users.insert_one(user_doc)
    
    # Create JWT token
    token = create_jwt_token(user.id, user.role.value)
    
    return {
        "message": "User registered successfully",
        "token": token,
        "user": user.dict()
    }

@api_router.post("/auth/login", response_model=dict)
async def login(login_data: UserLogin):
    # Find user
    user_doc = await db.users.find_one({"email": login_data.email})
    if not user_doc or not verify_password(login_data.password, user_doc['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create JWT token
    token = create_jwt_token(user_doc['id'], user_doc['role'])
    
    # Remove password from user data
    del user_doc['password']
    user = User(**user_doc)
    
    return {
        "message": "Login successful",
        "token": token,
        "user": user.dict()
    }

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# Vehicle routes
@api_router.get("/vehicles", response_model=List[Vehicle])
async def get_vehicles():
    vehicles = await db.vehicles.find({"available": True}).to_list(length=None)
    return [Vehicle(**vehicle) for vehicle in vehicles]

@api_router.get("/vehicles/all", response_model=List[Vehicle])
async def get_all_vehicles(current_user: User = Depends(get_admin_user)):
    vehicles = await db.vehicles.find().to_list(length=None)
    return [Vehicle(**vehicle) for vehicle in vehicles]

@api_router.post("/vehicles", response_model=Vehicle)
async def create_vehicle(vehicle_data: VehicleCreate, current_user: User = Depends(get_admin_user)):
    vehicle = Vehicle(**vehicle_data.dict())
    await db.vehicles.insert_one(vehicle.dict())
    return vehicle

@api_router.post("/vehicles/{vehicle_id}/upload-image")
async def upload_vehicle_image(vehicle_id: str, file: UploadFile = File(...), current_user: User = Depends(get_admin_user)):
    # Check if vehicle exists
    vehicle = await db.vehicles.find_one({"id": vehicle_id})
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1]
    filename = f"{vehicle_id}_{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Update vehicle with image URL
    image_url = f"/uploads/{filename}"
    await db.vehicles.update_one(
        {"id": vehicle_id},
        {"$set": {"image_url": image_url}}
    )
    
    return {"message": "Image uploaded successfully", "image_url": image_url}

@api_router.delete("/vehicles/{vehicle_id}")
async def delete_vehicle(vehicle_id: str, current_user: User = Depends(get_admin_user)):
    result = await db.vehicles.delete_one({"id": vehicle_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"message": "Vehicle deleted successfully"}

# Booking routes
@api_router.post("/bookings", response_model=Booking)
async def create_booking(booking_data: BookingCreate, current_user: User = Depends(get_current_user)):
    # Check if vehicle exists and is available
    vehicle = await db.vehicles.find_one({"id": booking_data.vehicle_id, "available": True})
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found or not available")
    
    # Check for conflicting bookings
    existing_booking = await db.bookings.find_one({
        "vehicle_id": booking_data.vehicle_id,
        "status": {"$in": ["confirmed", "active"]},
        "$or": [
            {"start_date": {"$lte": booking_data.end_date}, "end_date": {"$gte": booking_data.start_date}}
        ]
    })
    
    if existing_booking:
        raise HTTPException(status_code=400, detail="Vehicle is not available for selected dates")
    
    # Calculate total days and amount
    total_days = calculate_days(booking_data.start_date, booking_data.end_date)
    total_amount = total_days * vehicle['price_per_day']
    
    # Create booking
    booking = Booking(
        user_id=current_user.id,
        vehicle_id=booking_data.vehicle_id,
        start_date=booking_data.start_date,
        end_date=booking_data.end_date,
        total_days=total_days,
        total_amount=total_amount
    )
    
    await db.bookings.insert_one(booking.dict())
    return booking

@api_router.get("/bookings", response_model=List[BookingWithDetails])
async def get_user_bookings(current_user: User = Depends(get_current_user)):
    # Aggregate pipeline to join booking with user and vehicle data
    pipeline = [
        {"$match": {"user_id": current_user.id}},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "id",
            "as": "user"
        }},
        {"$lookup": {
            "from": "vehicles",
            "localField": "vehicle_id",
            "foreignField": "id",
            "as": "vehicle"
        }},
        {"$unwind": "$user"},
        {"$unwind": "$vehicle"},
        {"$project": {
            "id": 1,
            "user_id": 1,
            "user_name": "$user.name",
            "user_email": "$user.email",
            "vehicle_id": 1,
            "vehicle_name": "$vehicle.name",
            "vehicle_type": "$vehicle.type",
            "start_date": 1,
            "end_date": 1,
            "total_days": 1,
            "total_amount": 1,
            "status": 1,
            "payment_status": 1,
            "created_at": 1
        }}
    ]
    
    bookings = await db.bookings.aggregate(pipeline).to_list(length=None)
    return [BookingWithDetails(**booking) for booking in bookings]

@api_router.get("/bookings/all", response_model=List[BookingWithDetails])
async def get_all_bookings(current_user: User = Depends(get_admin_user)):
    # Aggregate pipeline to join booking with user and vehicle data
    pipeline = [
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "id",
            "as": "user"
        }},
        {"$lookup": {
            "from": "vehicles",
            "localField": "vehicle_id",
            "foreignField": "id",
            "as": "vehicle"
        }},
        {"$unwind": "$user"},
        {"$unwind": "$vehicle"},
        {"$project": {
            "id": 1,
            "user_id": 1,
            "user_name": "$user.name",
            "user_email": "$user.email",
            "vehicle_id": 1,
            "vehicle_name": "$vehicle.name",
            "vehicle_type": "$vehicle.type",
            "start_date": 1,
            "end_date": 1,
            "total_days": 1,
            "total_amount": 1,
            "status": 1,
            "payment_status": 1,
            "created_at": 1
        }},
        {"$sort": {"created_at": -1}}
    ]
    
    bookings = await db.bookings.aggregate(pipeline).to_list(length=None)
    return [BookingWithDetails(**booking) for booking in bookings]

@api_router.put("/bookings/{booking_id}/status")
async def update_booking_status(
    booking_id: str, 
    status: BookingStatus,
    payment_status: Optional[PaymentStatus] = None,
    current_user: User = Depends(get_admin_user)
):
    update_data = {"status": status}
    if payment_status:
        update_data["payment_status"] = payment_status
    
    result = await db.bookings.update_one(
        {"id": booking_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return {"message": "Booking status updated successfully"}

# Dashboard routes
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_admin_user)):
    # Get counts
    total_vehicles = await db.vehicles.count_documents({})
    available_vehicles = await db.vehicles.count_documents({"available": True})
    total_bookings = await db.bookings.count_documents({})
    active_bookings = await db.bookings.count_documents({"status": "active"})
    total_customers = await db.users.count_documents({"role": "customer"})
    
    # Get revenue (from completed bookings)
    revenue_pipeline = [
        {"$match": {"payment_status": "paid"}},
        {"$group": {"_id": None, "total_revenue": {"$sum": "$total_amount"}}}
    ]
    revenue_result = await db.bookings.aggregate(revenue_pipeline).to_list(1)
    total_revenue = revenue_result[0]["total_revenue"] if revenue_result else 0
    
    return {
        "total_vehicles": total_vehicles,
        "available_vehicles": available_vehicles,
        "total_bookings": total_bookings,
        "active_bookings": active_bookings,
        "total_customers": total_customers,
        "total_revenue": total_revenue
    }

# Vehicle availability check
@api_router.get("/vehicles/{vehicle_id}/availability")
async def check_vehicle_availability(vehicle_id: str, start_date: str, end_date: str):
    from datetime import datetime
    
    # Parse dates
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    # Check for conflicting bookings
    conflicting_booking = await db.bookings.find_one({
        "vehicle_id": vehicle_id,
        "status": {"$in": ["confirmed", "active"]},
        "$or": [
            {"start_date": {"$lte": end}, "end_date": {"$gte": start}}
        ]
    })
    
    return {"available": conflicting_booking is None}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()