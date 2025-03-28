import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './layouts/Layout';
import Dashboard from './pages/Dashboard';
import UploadBet from './pages/UploadBet';
import Marketplace from './pages/Marketplace';
import Leaderboard from './pages/Leaderboard';
import Profile from './pages/Profile';
import Help from './pages/Help';
import PaymentMethodsPage from './pages/Payments';
import BankrollManagement from './pages/BankrollManagement';
import { ToastProvider } from './components/ui/use-toast';
import Login from './pages/Login';
import Signup from './pages/Signup';

function App() {
  return (
    <Router>
      <ToastProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Default Route */}
          <Route path="/" element={<Dashboard />} />

          {/* All Routes Now Accessible */}
          <Route 
            path="/dashboard" 
            element={
              <Layout>
                <Dashboard />
              </Layout>
            } 
          />
          <Route 
            path="/upload" 
            element={
              <Layout>
                <UploadBet />
              </Layout>
            } 
          />
          <Route 
            path="/marketplace" 
            element={
              <Layout>
                <Marketplace />
              </Layout>
            } 
          />
          <Route 
            path="/Payments" 
            element={
              <Layout>
                <PaymentMethodsPage />
              </Layout>
            } 
          />
          <Route 
            path="/bankroll" 
            element={
              <Layout>
                <BankrollManagement />
              </Layout>
            } 
          />
          <Route 
            path="/leaderboard" 
            element={
              <Layout>
                <Leaderboard />
              </Layout>
            } 
          />
          <Route 
            path="/profile" 
            element={
              <Layout>
                <Profile />
              </Layout>
            } 
          />
          <Route 
            path="/help" 
            element={
              <Layout>
                <Help />
              </Layout>
            } 
          />
        </Routes>
      </ToastProvider>
    </Router>
  );
}

export default App;