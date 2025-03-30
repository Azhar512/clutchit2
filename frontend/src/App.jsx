import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, ProtectedRoute } from './components/auth/AuthWrapper';
import Layout from './layouts/Layout';
import Dashboard from './pages/Dashboard';
import UploadBet from './pages/UploadBet';
import Marketplace from './pages/Marketplace';
import Leaderboard from './pages/Leaderboard';
import Profile from './pages/Profile';
import Payments from './pages/Payments';
import Help from './pages/Help';
import BankrollManagement from './pages/BankrollManagement';
import { ToastProvider } from './components/ui/use-toast';
import Login from './pages/Login';
import Signup from './pages/Signup';

function App() {
  return (
    <Router>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />

            {/* Default Route - Redirect to login if not authenticated */}
            <Route path="/" element={<Navigate to="/login" />} />

            {/* Protected Routes */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/upload" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <UploadBet />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/marketplace" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <Marketplace />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/bankroll" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <BankrollManagement />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/leaderboard" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <Leaderboard />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <Profile />
                  </Layout>
                </ProtectedRoute>
              } 
            />
             <Route 
              path="/payments" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <Payments />
                  </Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/help" 
              element={
                <ProtectedRoute>
                  <Layout>
                    <Help />
                  </Layout>
                </ProtectedRoute>
              }
               
            />
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;