import React from "react";

import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { 
  TrendingUp, DollarSign, Award, Users, 
  ArrowUpRight, ArrowDownRight 
} from 'lucide-react';
import { useEffect, useState, useRef } from 'react';
import axios from 'axios'; // Make sure to install axios

const Dashboard = () => {
  // State management for UI effects
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const canvasRef = useRef(null);
  const animationFrameRef = useRef(null);
  
  // State for data from backend
  const [performanceData, setPerformanceData] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch dashboard data from backend
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Get user profile and metrics
        const metricsResponse = await axios.get('/api/user/metrics');
        
        // Format metrics data for UI
        const formattedMetrics = [
          { 
            title: "Win Rate",
            value: `${metricsResponse.data.winRate}%`,
            trend: metricsResponse.data.winRateTrend,
            icon: TrendingUp,
          },
          {
            title: "Total Profit",
            value: `$${metricsResponse.data.totalProfit.toLocaleString()}`,
            trend: metricsResponse.data.profitTrend,
            icon: DollarSign,
          },
          {
            title: "Clutch Picks",
            value: metricsResponse.data.clutchPicks.toString(),
            trend: metricsResponse.data.clutchPicksTrend,
            icon: Award,
          },
          {
            title: "Following",
            value: metricsResponse.data.followers.toString(),
            trend: metricsResponse.data.followersTrend,
            icon: Users,
          }
        ];
        
        setMetrics(formattedMetrics);
        
        // Get performance history data for chart
        const performanceResponse = await axios.get('/api/user/performance');
        setPerformanceData(performanceResponse.data.performanceHistory);
        
        // Get recent activity
        const activityResponse = await axios.get('/api/user/activity');
        setRecentActivity(activityResponse.data.recentActivity);
        
        setLoading(false);
      } catch (err) {
        console.error("Error fetching dashboard data:", err);
        setError("Failed to load dashboard data. Please try again.");
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  // Handle mouse movement for interactive light effects
  useEffect(() => {
    const handleMouseMove = (event) => {
      setMousePosition({
        x: event.clientX,
        y: event.clientY
      });
    };
    
    window.addEventListener('mousemove', handleMouseMove);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);
  
  // Setup particle animation on canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    // Particle class
    class Particle {
      constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 5 + 1;
        this.speedX = Math.random() * 1 - 0.5;
        this.speedY = Math.random() * 1 - 0.5;
        this.color = this.getRandomColor();
        this.opacity = Math.random() * 0.5 + 0.1;
      }
      
      getRandomColor() {
        const colors = [
          'rgba(168, 85, 247, 0.4)',  // Purple
          'rgba(139, 92, 246, 0.3)',  // Indigo
          'rgba(79, 70, 229, 0.3)',   // Indigo darker
          'rgba(191, 219, 254, 0.2)', // Light blue
        ];
        return colors[Math.floor(Math.random() * colors.length)];
      }
      
      update() {
        this.x += this.speedX;
        this.y += this.speedY;
        
        if (this.size > 0.2) this.size -= 0.01;
        
        // Reset particle when it gets too small or goes off screen
        if (this.size <= 0.2 || 
            this.x < 0 || 
            this.x > canvas.width || 
            this.y < 0 || 
            this.y > canvas.height) {
          this.x = Math.random() * canvas.width;
          this.y = Math.random() * canvas.height;
          this.size = Math.random() * 5 + 1;
          this.speedX = Math.random() * 1 - 0.5;
          this.speedY = Math.random() * 1 - 0.5;
        }
      }
      
      draw() {
        ctx.fillStyle = this.color;
        ctx.globalAlpha = this.opacity;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    
    // Create particle array
    const particleArray = [];
    const particleCount = Math.min(100, window.innerWidth / 20);
    
    for (let i = 0; i < particleCount; i++) {
      particleArray.push(new Particle());
    }
    
    // Draw wave background
    function drawWave(yOffset, amplitude, wavelength, color) {
      ctx.beginPath();
      ctx.moveTo(0, yOffset);
      
      for (let x = 0; x < canvas.width; x++) {
        const y = yOffset + Math.sin(x / wavelength) * amplitude;
        ctx.lineTo(x, y);
      }
      
      ctx.lineTo(canvas.width, canvas.height);
      ctx.lineTo(0, canvas.height);
      ctx.closePath();
      ctx.fillStyle = color;
      ctx.fill();
    }
    
    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw animated waves
      const time = Date.now() / 10000;
      drawWave(
        canvas.height * 0.85 + Math.sin(time) * 20, 
        15, 
        120, 
        'rgba(76, 29, 149, 0.1)'
      );
      drawWave(
        canvas.height * 0.8 + Math.sin(time + 1) * 25, 
        20, 
        100, 
        'rgba(109, 40, 217, 0.07)'
      );
      
      // Update and draw particles
      particleArray.forEach(particle => {
        particle.update();
        particle.draw();
      });
      
      // Draw mouse trail if mouse has moved
      if (mousePosition.x > 0 && mousePosition.y > 0) {
        ctx.beginPath();
        ctx.arc(mousePosition.x, mousePosition.y, 60, 0, Math.PI * 2);
        const gradient = ctx.createRadialGradient(
          mousePosition.x, 
          mousePosition.y, 
          0, 
          mousePosition.x, 
          mousePosition.y, 
          60
        );
        gradient.addColorStop(0, 'rgba(139, 92, 246, 0.2)');
        gradient.addColorStop(1, 'rgba(139, 92, 246, 0)');
        ctx.fillStyle = gradient;
        ctx.fill();
      }
      
      animationFrameRef.current = requestAnimationFrame(animate);
    };
    
    animate();
    
    // Handle resize
    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    
    window.addEventListener('resize', handleResize);
    
    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);
  
  // Loading state
  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="flex h-screen w-full items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500 mx-auto"></div>
            <p className="mt-4 text-lg text-gray-200">Loading your dashboard data...</p>
          </div>
        </div>
      </div>
    );
  }
  
  // Error state
  if (error) {
    return (
      <div className="dashboard-container">
        <div className="flex h-screen w-full items-center justify-center">
          <div className="text-center">
            <div className="text-red-500 text-6xl mb-4">⚠️</div>
            <p className="text-lg text-gray-200">{error}</p>
            <button 
              className="mt-4 px-4 py-2 bg-purple-600 rounded-md hover:bg-purple-700 transition-colors"
              onClick={() => window.location.reload()}
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render dashboard with data from backend
  return (
    <div className="dashboard-container">
      {/* Canvas for background animations */}
      <canvas ref={canvasRef} className="animation-canvas"></canvas>
      
      {/* Background Elements */}
      <div className="star-effect star-1"></div>
      <div className="star-effect star-2"></div>
      <div className="star-effect star-3"></div>
      <div className="star-effect star-4"></div>
      <div className="star-effect star-5"></div>
      
      <div className="mouse-follow-light" style={{
        left: `${mousePosition.x}px`,
        top: `${mousePosition.y}px`
      }}></div>
      
      <div className="dot-overlay"></div>
      <div className="glow-circle circle-1 floating"></div>
      <div className="glow-circle circle-2 floating"></div>
      <div className="glow-circle circle-3 floating"></div>
      
      {/* Animated patterns */}
      <div className="grid-pattern"></div>
      <div className="network-lines"></div>
      
      {/* Dashboard Content */}
      <div className="dashboard-header">
        <div className="logo-glow"></div>
        <h1 className="dashboard-title">Performance Dashboard</h1>
        <p className="dashboard-subtitle">We Process, You Win</p>
        <div className="header-accent"></div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 z-10 relative">
        {metrics.map((metric, index) => (
          <Card key={index} className={`dashboard-card card-${index} floating-card`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-300">{metric.title}</p>
                  <p className="text-2xl font-bold mt-1 text-white">{metric.value}</p>
                  <div className={`flex items-center mt-1 ${
                    metric.trend > 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {metric.trend > 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                    <span className="text-sm">{Math.abs(metric.trend)}%</span>
                  </div>
                </div>
                <div className="icon-container">
                  <metric.icon className="w-8 h-8 text-indigo-400" />
                  <div className="icon-glow"></div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Performance Chart */}
      <Card className="dashboard-card chart-card mt-6 z-10 relative">
        <CardHeader className="border-b border-purple-900/30">
          <CardTitle className="text-white flex items-center">
            <span className="text-glow">Performance Overview</span>
            <div className="ml-2 w-2 h-2 bg-cyan-400 rounded-full pulse-animation"></div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={performanceData}>
                <defs>
                  <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#7e22ce" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0.2}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="date" stroke="rgba(255,255,255,0.7)" />
                <YAxis stroke="rgba(255,255,255,0.7)" />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'rgba(30, 10, 60, 0.95)',
                    border: '1px solid rgba(168, 85, 247, 0.4)',
                    borderRadius: '8px',
                    boxShadow: '0 0 15px rgba(168, 85, 247, 0.2)',
                    color: 'white'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="profit" 
                  stroke="url(#colorProfit)" 
                  strokeWidth={3}
                  dot={{ fill: '#a855f7', strokeWidth: 0, r: 5 }}
                  activeDot={{ 
                    r: 8, 
                    fill: '#ffffff',
                    stroke: '#a855f7',
                    strokeWidth: 2
                  }}
                  animationDuration={1500}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card className="dashboard-card activity-card mt-6 z-10 relative">
        <CardHeader className="border-b border-purple-900/30">
          <CardTitle className="text-white">Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivity.map((activity, index) => (
              <div key={index} className="activity-item flex items-center justify-between p-3 hover:bg-opacity-15 hover:bg-white rounded-lg transition-all duration-300">
                <div className="flex items-center space-x-3">
                  <div className={`activity-indicator w-3 h-3 rounded-full ${
                    activity.type === 'win' ? 'activity-win' : 
                    activity.type === 'bet' ? 'activity-bet' : 'activity-purchase'
                  }`} />
                  <p className="text-sm text-gray-100">{activity.description}</p>
                </div>
                <span className="text-xs text-gray-400">{activity.time}</span>
              </div>
            ))}
            {recentActivity.length === 0 && (
              <div className="text-center py-6 text-gray-400">
                <p>No recent activity to display</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* CSS styles remain the same */}
      <style jsx>{`
        @keyframes float {
          0% { transform: translateY(0px); }
          50% { transform: translateY(-15px); }
          100% { transform: translateY(0px); }
        }
        
        @keyframes pulse {
          0% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.8); opacity: 0.4; }
          100% { transform: scale(1); opacity: 1; }
        }
        
        @keyframes glow {
          0% { filter: blur(10px) brightness(1); }
          50% { filter: blur(15px) brightness(1.3); }
          100% { filter: blur(10px) brightness(1); }
        }
        
        @keyframes rotateBackground {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        @keyframes gradientShift {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        
        .dashboard-container {
          position: relative;
          min-height: 100vh;
          padding: 2rem;
          background: linear-gradient(135deg, #2e0068 0%, #1c0050 40%, #10002b 100%);
          color: white;
          overflow: hidden;
        }
        
        .animation-canvas {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          z-index: 1;
          pointer-events: none;
        }
        
        .dashboard-header {
          text-align: center;
          margin-bottom: 3rem;
          position: relative;
          z-index: 10;
          padding: 1.5rem 0;
        }
        
        .dashboard-title {
          font-size: 2.5rem;
          font-weight: bold;
          background: linear-gradient(90deg, #ffffff, #d8b4fe, #a78bfa);
          background-size: 200% auto;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          margin-bottom: 0.5rem;
          position: relative;
          display: inline-block;
          animation: gradientShift 3s ease infinite;
        }
        
        .dashboard-subtitle {
          font-size: 1.2rem;
          color: #c4b5fd;
          margin-bottom: 0.5rem;
          letter-spacing: 1px;
        }
        
        .header-accent {
          width: 80px;
          height: 4px;
          background: linear-gradient(90deg, #a855f7, #2563eb);
          border-radius: 2px;
          margin: 0.5rem auto;
          position: relative;
          overflow: hidden;
        }
        
        .header-accent:before {
          content: '';
          position: absolute;
          top: -2px;
          left: -100%;
          right: 0;
          bottom: -2px;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.8), transparent);
          animation: slide 2s linear infinite;
        }
        
        @keyframes slide {
          100% { left: 100%; }
        }
        
        .logo-glow {
          position: absolute;
          top: -20px;
          left: 50%;
          transform: translateX(-50%);
          width: 100px;
          height: 100px;
          background: radial-gradient(circle, rgba(139, 92, 246, 0.5) 0%, rgba(139, 92, 246, 0) 70%);
          filter: blur(15px);
          z-index: -1;
          animation: glow 3s ease-in-out infinite;
        }
        
        .dashboard-card {
          background-color: rgba(30, 10, 60, 0.5);
          backdrop-filter: blur(12px);
          border: 1px solid rgba(168, 85, 247, 0.1);
          border-radius: 16px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
          overflow: hidden;
          position: relative;
          transition: all 0.3s ease;
        }
        
        .dashboard-card:before {
          content: '';
          position: absolute;
          top: -1px;
          left: -1px;
          right: -1px;
          height: 2px;
          background: linear-gradient(90deg, rgba(139, 92, 246, 0), rgba(139, 92, 246, 0.6), rgba(139, 92, 246, 0));
          z-index: 1;
        }
        
        .dashboard-card:after {
          content: '';
          position: absolute;
          bottom: 0;
          left: 0;
          width: 100%;
          height: 30%;
          background: linear-gradient(to top, rgba(139, 92, 246, 0.05), transparent);
          z-index: 0;
        }
        
        .floating-card {
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .floating-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 12px 40px rgba(76, 29, 149, 0.3);
        }
        
        .icon-container {
          position: relative;
          width: 50px;
          height: 50px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .icon-glow {
          position: absolute;
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: radial-gradient(circle, rgba(139, 92, 246, 0.5) 0%, rgba(139, 92, 246, 0) 70%);
          filter: blur(8px);
          z-index: -1;
          animation: glow 2s ease-in-out infinite;
        }
        
        .chart-card:hover {
          box-shadow: 0 0 25px rgba(168, 85, 247, 0.2);
        }
        
        .activity-card {
          position: relative;
        }
        
        .activity-item {
          position: relative;
          border-left: 0px solid transparent;
          transition: all 0.3s ease;
        }
        
        .activity-item:hover {
          border-left: 4px solid #a855f7;
          padding-left: calc(0.75rem - 4px);
          background-color: rgba(168, 85, 247, 0.1);
        }
        
        .activity-indicator {
          position: relative;
        }
        
        .activity-indicator:after {
          content: '';
          position: absolute;
          top: -4px;
          left: -4px;
          width: 200%;
          height: 200%;
          border-radius: 50%;
          filter: blur(6px);
          z-index: -1;
          opacity: 0.7;
        }
        
        .activity-win {
          background: #10b981;
          box-shadow: 0 0 10px #10b981;
        }
        
        .activity-bet {
          background: #3b82f6;
          box-shadow: 0 0 10px #3b82f6;
        }
        
        .activity-purchase {
          background: #f59e0b;
          box-shadow: 0 0 10px #f59e0b;
        }
        
        .star-effect {
          position: absolute;
          border-radius: 50%;
          filter: blur(15px);
          opacity: 0.7;
          pointer-events: none;
          z-index: 1;
          transition: all 2s ease-in-out;
        }
        
        .star-1 {
          top: 15%;
          right: 15%;
          width: 200px;
          height: 200px;
          background: radial-gradient(circle, rgba(255,255,255,0.8) 0%, rgba(173,216,230,0) 70%);
        }
        
        .star-2 {
          top: 30%;
          left: 10%;
          width: 150px;
          height: 150px;
          background: radial-gradient(circle, rgba(168,85,247,0.6) 0%, rgba(173,216,230,0) 70%);
        }
        
        .star-3 {
          bottom: 25%;
          right: 20%;
          width: 120px;
          height: 120px;
          background: radial-gradient(circle, rgba(76,29,149,0.6) 0%, rgba(173,216,230,0) 70%);
        }
        
        .star-4 {
          top: 15%;
          left: 40%;
          width: 80px;
          height: 80px;
          background: radial-gradient(circle, rgba(139,92,246,0.5) 0%, rgba(173,216,230,0) 70%);
        }
        
        .star-5 {
          bottom: 30%;
          left: 20%;
          width: 100px;
          height: 100px;
          background: radial-gradient(circle, rgba(221,214,254,0.4) 0%, rgba(173,216,230,0) 70%);
        }
        
        .mouse-follow-light {
          position: fixed;
          width: 300px;
          height: 300px;
          border-radius: 50%;
          background: radial-gradient(circle, rgba(139,92,246,0.15) 0%, rgba(139,92,246,0) 70%);
          transform: translate(-50%, -50%);
          pointer-events: none;
          z-index: 3;
          filter: blur(20px);
          transition: opacity 0.3s ease;
          opacity: 0.7;
        }
        
        .glow-circle {
          position: absolute;
          border-radius: 50%;
          background: rgba(139, 92, 246, 0.05);
          filter: blur(60px);
          z-index: 0;
        }
        
        .circle-1 {
          top: -10%;
          right: -5%;
          width: 300px;
          height: 300px;
        }
        
        .circle-2 {
          bottom: 10%;
          left: -5%;
          width: 250px;
          height: 250px;
          background: rgba(76, 29, 149, 0.05);
        }
        
        .circle-3 {
          top: 40%;
          right: 30%;
          width: 200px;
          height: 200px;
          background: rgba(168, 85, 247, 0.03);
        }
        
        .grid-pattern {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-image: 
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
          background-size: 40px 40px;
          z-index: 1;
          opacity: 0.3;
          perspective: 1000px;
          transform-style: preserve-3d;
          animation: rotateBackground 120s linear infinite;
          transform-origin: center center;
          pointer-events: none;
        }
        
        .network-lines {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-image: 
            radial-gradient(circle at 20% 30%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(76, 29, 149, 0.1) 0%, transparent 40%);
          z-index: 1;
          opacity: 0.6;
          pointer-events: none;
        }
        
        .dot-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-image: radial-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px);
          background-size: 30px 30px;
          z-index: 1;
          pointer-events: none;
        }
        
        .text-glow {
          text-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
        }
        
        .pulse-animation {
          animation: pulse 3s infinite;
        }
        
        .floating {
          animation: float 6s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
};

export default Dashboard;