import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './layouts/Layout';
import Dashboard from './pages/Dashboard';
import UploadBet from './pages/UploadBet';
import Marketplace from './pages/Marketplace';
import Leaderboard from './pages/Leaderboard';
import Profile from './pages/Profile';
import PaymentMethodsPage from './pages/Payments';
import Help from './pages/Help';
import BankrollManagement from './pages/BankrollManagement';
import { ToastProvider } from './components/ui/use-toast';

function App() {
  return (
    <Router>
        <ToastProvider>
          <Routes>
            {/* Default Route - Directly to Dashboard */}
            <Route 
              path="/" 
              element={
                
                  <Layout>
                    <Dashboard />
                  </Layout>
                
              } 
            />
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
                    <PaymentMethodsPage />
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