import React, { createContext, useState, useEffect, useContext } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import axios from 'axios';

// Create authentication context
export const AuthContext = createContext();

// Provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  
  // Initialize auth state from localStorage on first load
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    const token = localStorage.getItem('accessToken');
    
    if (storedUser && token) {
      setUser(JSON.parse(storedUser));
      
      // Setup axios interceptors for token handling
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
    
    setLoading(false);
  }, []);
  
  // Handle token refresh
  const refreshToken = async () => {
    try {
      const refreshTokenValue = localStorage.getItem('refreshToken');
      
      if (!refreshTokenValue) {
        logout();
        return;
      }
      
      const response = await axios.post('/api/auth/refresh', {}, {
        headers: {
          'Authorization': `Bearer ${refreshTokenValue}`
        }
      });
      
      localStorage.setItem('accessToken', response.data.access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
      
      return response.data.access_token;
    } catch (error) {
      logout();
      return null;
    }
  };
  
  // Setup axios interceptor for handling 401 errors (expired tokens)
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      response => response,
      async error => {
        if (error.response && error.response.status === 401) {
          const originalRequest = error.config;
          
          // Prevent infinite loops
          if (!originalRequest._retry) {
            originalRequest._retry = true;
            const token = await refreshToken();
            
            if (token) {
              originalRequest.headers['Authorization'] = `Bearer ${token}`;
              return axios(originalRequest);
            }
          }
        }
        
        return Promise.reject(error);
      }
    );
    
    // Clean up interceptor on unmount
    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, []);
  
  // Login function
  const login = (userData, tokens) => {
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('accessToken', tokens.access_token);
    localStorage.setItem('refreshToken', tokens.refresh_token);
    
    axios.defaults.headers.common['Authorization'] = `Bearer ${tokens.access_token}`;
    setUser(userData);
    
    navigate('/dashboard');
  };
  
  // Logout function
  const logout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    
    navigate('/login');
  };
  
  // Check if user is authenticated
  const isAuthenticated = () => {
    return !!user && !!localStorage.getItem('accessToken');
  };
  
  return (
    <AuthContext.Provider value={{ 
      user, 
      login, 
      logout, 
      isAuthenticated,
      loading
    }}>
      {children}
    </AuthContext.Provider>
  );
};

// Create a hook for using the auth context
export const useAuth = () => useContext(AuthContext);

// Protected route component
export const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!isAuthenticated()) {
    return <Navigate to="/login" />;
  }
  
  return children;
};