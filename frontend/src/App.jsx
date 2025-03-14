import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './layouts/Layout';
import Dashboard from './pages/Dashboard';
import UploadBet from './pages/UploadBet';
import Marketplace from './pages/Marketplace';
import Leaderboard from './pages/Leaderboard';
import Profile from './pages/Profile';
import Help from './pages/Help';
import BankrollManagement from './pages/BankrollManagement';
import { ToastProvider } from './components/ui/use-toast';

function App() {
  return (
    <ToastProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<UploadBet />} />
            <Route path="/marketplace" element={<Marketplace />} />
            <Route path="/bankroll" element={<BankrollManagement/>} />
            <Route path="/leaderboard" element={<Leaderboard />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/help" element={<Help />} />
          </Routes>
        </Layout>
      </Router>
    </ToastProvider>
  );
}

export default App;