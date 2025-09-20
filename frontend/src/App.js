import React, { useState, useEffect, createContext, useContext } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { token, user } = response.data;
      localStorage.setItem('token', token);
      setToken(token);
      setUser(user);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post(`${API}/auth/register`, userData);
      const { token, user } = response.data;
      localStorage.setItem('token', token);
      setToken(token);
      setUser(user);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      return true;
    } catch (error) {
      console.error('Registration failed:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Components
const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-blue-600 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <h1 className="text-2xl font-bold">🚗 AutoRental Hub</h1>
        {user && (
          <div className="flex items-center gap-4">
            <span>Welcome, {user.name}</span>
            <span className="bg-blue-800 px-2 py-1 rounded text-sm">
              {user.role.toUpperCase()}
            </span>
            <button
              onClick={logout}
              className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded transition-colors"
            >
              Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};

const LoginForm = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    phone: '',
    role: 'customer'
  });
  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isLogin) {
      await login(formData.email, formData.password);
    } else {
      await register(formData);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center">
          {isLogin ? 'Login' : 'Register'} - AutoRental Hub
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <>
              <input
                type="text"
                placeholder="Full Name"
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                required
              />
              <input
                type="tel"
                placeholder="Phone Number"
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
                required
              />
              <select
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={formData.role}
                onChange={(e) => setFormData({...formData, role: e.target.value})}
              >
                <option value="customer">Customer</option>
                <option value="admin">Admin</option>
              </select>
            </>
          )}
          
          <input
            type="email"
            placeholder="Email"
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            required
          />
          
          <input
            type="password"
            placeholder="Password"
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            required
          />
          
          <button
            type="submit"
            className="w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            {isLogin ? 'Login' : 'Register'}
          </button>
        </form>
        
        <p className="text-center mt-4">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-blue-600 hover:underline"
          >
            {isLogin ? 'Register' : 'Login'}
          </button>
        </p>
      </div>
    </div>
  );
};

const VehicleCard = ({ vehicle, onBook, isAdmin, onDelete }) => {
  const getCapacityText = (capacity, type) => {
    if (type === 'motorcycle') {
      return capacity === 1 ? '1 rider' : `${capacity} riders`;
    } else if (type === 'truck') {
      return capacity <= 3 ? `${capacity} seats` : `${capacity} seats (crew cab)`;
    } else {
      return `${capacity} seats`;
    }
  };

  const getCapacityIcon = (type) => {
    switch(type) {
      case 'motorcycle': return '🏍️';
      case 'truck': return '🚛';
      case 'van': return '🚐';
      default: return '👥';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="h-48 bg-gray-200 flex items-center justify-center">
        {vehicle.image_url ? (
          <img 
            src={`${BACKEND_URL}${vehicle.image_url}`} 
            alt={vehicle.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="text-gray-500 text-center">
            <div className="text-4xl mb-2">🚗</div>
            <div>No Image</div>
          </div>
        )}
      </div>
      
      <div className="p-4">
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-bold text-lg">{vehicle.name}</h3>
          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
            {vehicle.type.toUpperCase()}
          </span>
        </div>
        
        <p className="text-gray-600 mb-2">{vehicle.brand} {vehicle.model} ({vehicle.year})</p>
        
        {/* Capacity Information */}
        <div className="flex items-center mb-3 text-sm text-gray-700 bg-gray-50 px-3 py-2 rounded">
          <span className="mr-2">{getCapacityIcon(vehicle.type)}</span>
          <span className="font-medium">{getCapacityText(vehicle.capacity, vehicle.type)}</span>
        </div>
        
        <p className="text-gray-700 mb-4">{vehicle.description}</p>
        
        <div className="flex justify-between items-center">
          <span className="text-2xl font-bold text-green-600">
            ${vehicle.price_per_day}/day
          </span>
          
          <div className="flex gap-2">
            {!isAdmin && (
              <button
                onClick={() => onBook(vehicle)}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
                disabled={!vehicle.available}
              >
                {vehicle.available ? 'Book Now' : 'Unavailable'}
              </button>
            )}
            
            {isAdmin && (
              <button
                onClick={() => onDelete(vehicle.id)}
                className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
              >
                Delete
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const BookingModal = ({ vehicle, onClose, onConfirm }) => {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [totalAmount, setTotalAmount] = useState(0);

  useEffect(() => {
    if (startDate && endDate && new Date(endDate) > new Date(startDate)) {
      const days = Math.max(1, Math.ceil((new Date(endDate) - new Date(startDate)) / (1000 * 60 * 60 * 24)));
      setTotalAmount(days * vehicle.price_per_day);
    } else {
      setTotalAmount(0);
    }
  }, [startDate, endDate, vehicle.price_per_day]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onConfirm({
      vehicle_id: vehicle.id,
      start_date: new Date(startDate).toISOString(),
      end_date: new Date(endDate).toISOString()
    });
  };

  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Book {vehicle.name}</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Start Date</label>
            <input
              type="date"
              min={today}
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">End Date</label>
            <input
              type="date"
              min={startDate || today}
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          {totalAmount > 0 && (
            <div className="bg-gray-50 p-3 rounded">
              <div className="flex justify-between">
                <span>Daily Rate:</span>
                <span>${vehicle.price_per_day}</span>
              </div>
              <div className="flex justify-between">
                <span>Total Days:</span>
                <span>{Math.max(1, Math.ceil((new Date(endDate) - new Date(startDate)) / (1000 * 60 * 60 * 24)))}</span>
              </div>
              <div className="flex justify-between font-bold text-lg border-t pt-2 mt-2">
                <span>Total Amount:</span>
                <span>${totalAmount}</span>
              </div>
            </div>
          )}
          
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-500 text-white py-2 rounded hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={totalAmount === 0}
              className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition-colors disabled:bg-gray-300"
            >
              Confirm Booking
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const VehicleForm = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    type: 'car',
    brand: '',
    model: '',
    year: new Date().getFullYear(),
    price_per_day: '',
    capacity: '',
    description: ''
  });
  const [imageFile, setImageFile] = useState(null);

  const getCapacityPlaceholder = (type) => {
    switch(type) {
      case 'motorcycle': return 'Number of riders (1-2)';
      case 'car': return 'Number of seats (2-8)';
      case 'truck': return 'Number of seats (2-6)';
      case 'van': return 'Number of seats (7-15)';
      default: return 'Passenger capacity';
    }
  };

  const getCapacityLimits = (type) => {
    switch(type) {
      case 'motorcycle': return { min: 1, max: 2 };
      case 'car': return { min: 2, max: 8 };
      case 'truck': return { min: 2, max: 6 };
      case 'van': return { min: 7, max: 15 };
      default: return { min: 1, max: 20 };
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const vehicleData = {
      ...formData,
      year: parseInt(formData.year),
      price_per_day: parseFloat(formData.price_per_day),
      capacity: parseInt(formData.capacity)
    };
    
    const vehicleId = await onSubmit(vehicleData);
    
    // Upload image if provided
    if (imageFile && vehicleId) {
      const imageFormData = new FormData();
      imageFormData.append('file', imageFile);
      
      try {
        await axios.post(`${API}/vehicles/${vehicleId}/upload-image`, imageFormData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      } catch (error) {
        console.error('Failed to upload image:', error);
      }
    }
    
    onClose();
  };

  const capacityLimits = getCapacityLimits(formData.type);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg w-full max-w-md max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Add New Vehicle</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Vehicle Name"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          
          <select
            value={formData.type}
            onChange={(e) => setFormData({...formData, type: e.target.value, capacity: ''})}
            className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="car">Car</option>
            <option value="motorcycle">Motorcycle</option>
            <option value="truck">Truck</option>
            <option value="van">Van</option>
          </select>
          
          <input
            type="text"
            placeholder="Brand"
            value={formData.brand}
            onChange={(e) => setFormData({...formData, brand: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          
          <input
            type="text"
            placeholder="Model"
            value={formData.model}
            onChange={(e) => setFormData({...formData, model: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          
          <input
            type="number"
            placeholder="Year"
            min="1900"
            max={new Date().getFullYear() + 1}
            value={formData.year}
            onChange={(e) => setFormData({...formData, year: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          
          <input
            type="number"
            step="0.01"
            placeholder="Price per Day ($)"
            value={formData.price_per_day}
            onChange={(e) => setFormData({...formData, price_per_day: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          
          <div>
            <input
              type="number"
              placeholder={getCapacityPlaceholder(formData.type)}
              min={capacityLimits.min}
              max={capacityLimits.max}
              value={formData.capacity}
              onChange={(e) => setFormData({...formData, capacity: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
            <div className="text-xs text-gray-500 mt-1">
              {formData.type === 'motorcycle' ? 'Typical: 1-2 riders' :
               formData.type === 'car' ? 'Typical: 4-5 seats' :
               formData.type === 'truck' ? 'Typical: 2-3 seats (regular cab), 5-6 seats (crew cab)' :
               'Typical: 8-12 seats'}
            </div>
          </div>
          
          <textarea
            placeholder="Description"
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            rows="3"
            className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          
          <div>
            <label className="block text-sm font-medium mb-1">Vehicle Image</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setImageFile(e.target.files[0])}
              className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-500 text-white py-2 rounded hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition-colors"
            >
              Add Vehicle
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('vehicles');
  const [vehicles, setVehicles] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [stats, setStats] = useState({});
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const [showVehicleForm, setShowVehicleForm] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [activeTab, user]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'vehicles') {
        const endpoint = user.role === 'admin' ? '/vehicles/all' : '/vehicles';
        const response = await axios.get(`${API}${endpoint}`);
        setVehicles(response.data);
      } else if (activeTab === 'bookings') {
        const endpoint = user.role === 'admin' ? '/bookings/all' : '/bookings';
        const response = await axios.get(`${API}${endpoint}`);
        setBookings(response.data);
      } else if (activeTab === 'dashboard' && user.role === 'admin') {
        const response = await axios.get(`${API}/dashboard/stats`);
        setStats(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBookVehicle = async (bookingData) => {
    try {
      await axios.post(`${API}/bookings`, bookingData);
      setSelectedVehicle(null);
      if (activeTab === 'bookings') {
        fetchData();
      }
      alert('Booking created successfully!');
    } catch (error) {
      console.error('Booking failed:', error);
      alert('Booking failed. Please try again.');
    }
  };

  const handleAddVehicle = async (vehicleData) => {
    try {
      const response = await axios.post(`${API}/vehicles`, vehicleData);
      fetchData();
      return response.data.id;
    } catch (error) {
      console.error('Failed to add vehicle:', error);
      alert('Failed to add vehicle. Please try again.');
      return null;
    }
  };

  const handleDeleteVehicle = async (vehicleId) => {
    if (window.confirm('Are you sure you want to delete this vehicle?')) {
      try {
        await axios.delete(`${API}/vehicles/${vehicleId}`);
        fetchData();
        alert('Vehicle deleted successfully!');
      } catch (error) {
        console.error('Failed to delete vehicle:', error);
        alert('Failed to delete vehicle. Please try again.');
      }
    }
  };

  const handleUpdateBookingStatus = async (bookingId, status, paymentStatus) => {
    try {
      await axios.put(`${API}/bookings/${bookingId}/status`, { status, payment_status: paymentStatus });
      fetchData();
      alert('Booking status updated successfully!');
    } catch (error) {
      console.error('Failed to update booking status:', error);
      alert('Failed to update booking status. Please try again.');
    }
  };

  const tabs = user.role === 'admin' 
    ? [
        { id: 'dashboard', label: '📊 Dashboard', icon: '📊' },
        { id: 'vehicles', label: '🚗 Vehicles', icon: '🚗' },
        { id: 'bookings', label: '📅 All Bookings', icon: '📅' }
      ]
    : [
        { id: 'vehicles', label: '🚗 Browse Vehicles', icon: '🚗' },
        { id: 'bookings', label: '📅 My Bookings', icon: '📅' }
      ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <div className="flex items-center justify-center h-64">
          <div className="text-xl">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      
      <div className="container mx-auto px-4 py-6">
        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-white rounded-lg p-1 mb-6 shadow-sm">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-3 px-4 rounded-md font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && user.role === 'admin' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Vehicles</h3>
              <p className="text-3xl font-bold text-blue-600">{stats.total_vehicles}</p>
              <p className="text-sm text-gray-500">{stats.available_vehicles} available</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Bookings</h3>
              <p className="text-3xl font-bold text-green-600">{stats.total_bookings}</p>
              <p className="text-sm text-gray-500">{stats.active_bookings} active</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Revenue</h3>
              <p className="text-3xl font-bold text-purple-600">${stats.total_revenue}</p>
              <p className="text-sm text-gray-500">From paid bookings</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Customers</h3>
              <p className="text-3xl font-bold text-orange-600">{stats.total_customers}</p>
            </div>
          </div>
        )}

        {/* Vehicles Tab */}
        {activeTab === 'vehicles' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">
                {user.role === 'admin' ? 'Manage Vehicles' : 'Available Vehicles'}
              </h2>
              {user.role === 'admin' && (
                <button
                  onClick={() => setShowVehicleForm(true)}
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
                >
                  Add New Vehicle
                </button>
              )}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {vehicles.map((vehicle) => (
                <VehicleCard
                  key={vehicle.id}
                  vehicle={vehicle}
                  onBook={setSelectedVehicle}
                  isAdmin={user.role === 'admin'}
                  onDelete={handleDeleteVehicle}
                />
              ))}
            </div>
            
            {vehicles.length === 0 && (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🚗</div>
                <p className="text-xl text-gray-600">No vehicles available</p>
              </div>
            )}
          </div>
        )}

        {/* Bookings Tab */}
        {activeTab === 'bookings' && (
          <div>
            <h2 className="text-2xl font-bold mb-6">
              {user.role === 'admin' ? 'All Bookings' : 'My Bookings'}
            </h2>
            
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Vehicle
                      </th>
                      {user.role === 'admin' && (
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Customer
                        </th>
                      )}
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Dates
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      {user.role === 'admin' && (
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      )}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {bookings.map((booking) => (
                      <tr key={booking.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="font-medium text-gray-900">{booking.vehicle_name}</div>
                            <div className="text-sm text-gray-500">{booking.vehicle_type.toUpperCase()}</div>
                          </div>
                        </td>
                        {user.role === 'admin' && (
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="font-medium text-gray-900">{booking.user_name}</div>
                              <div className="text-sm text-gray-500">{booking.user_email}</div>
                            </div>
                          </td>
                        )}
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <div>{new Date(booking.start_date).toLocaleDateString()}</div>
                          <div>to {new Date(booking.end_date).toLocaleDateString()}</div>
                          <div className="text-gray-500">({booking.total_days} days)</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                          ${booking.total_amount}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex flex-col space-y-1">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              booking.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                              booking.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                              booking.status === 'active' ? 'bg-blue-100 text-blue-800' :
                              booking.status === 'completed' ? 'bg-gray-100 text-gray-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {booking.status.toUpperCase()}
                            </span>
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              booking.payment_status === 'paid' ? 'bg-green-100 text-green-800' :
                              booking.payment_status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {booking.payment_status.toUpperCase()}
                            </span>
                          </div>
                        </td>
                        {user.role === 'admin' && (
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-y-1">
                            <select
                              value={booking.status}
                              onChange={(e) => handleUpdateBookingStatus(booking.id, e.target.value, booking.payment_status)}
                              className="block w-full text-xs border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                            >
                              <option value="pending">Pending</option>
                              <option value="confirmed">Confirmed</option>
                              <option value="active">Active</option>
                              <option value="completed">Completed</option>
                              <option value="cancelled">Cancelled</option>
                            </select>
                            <select
                              value={booking.payment_status}
                              onChange={(e) => handleUpdateBookingStatus(booking.id, booking.status, e.target.value)}
                              className="block w-full text-xs border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                            >
                              <option value="pending">Payment Pending</option>
                              <option value="paid">Paid</option>
                              <option value="failed">Failed</option>
                              <option value="refunded">Refunded</option>
                            </select>
                          </td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {bookings.length === 0 && (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📅</div>
                  <p className="text-xl text-gray-600">No bookings found</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      {selectedVehicle && (
        <BookingModal
          vehicle={selectedVehicle}
          onClose={() => setSelectedVehicle(null)}
          onConfirm={handleBookVehicle}
        />
      )}

      {showVehicleForm && (
        <VehicleForm
          onClose={() => setShowVehicleForm(false)}
          onSubmit={handleAddVehicle}
        />
      )}
    </div>
  );
};

const App = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return user ? <Dashboard /> : <LoginForm />;
};

const AppWithAuth = () => {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
};

export default AppWithAuth;