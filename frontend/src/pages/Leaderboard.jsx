import React, { useEffect, useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Trophy, Flame, Star, Crown, TrendingUp, ArrowUpRight } from 'lucide-react';
import axios from 'axios';

const Leaderboard = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [leaders, setLeaders] = useState([]);
  const [currentUserStats, setCurrentUserStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const canvasRef = useRef(null);
  const animationFrameRef = useRef(null);

  // Fetch data from backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Get JWT token from localStorage
        const token = localStorage.getItem('auth_token');
        if (!token) {
          throw new Error('Authentication token not found');
        }
        
        const config = {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        };
        
        // Fetch top performers
        const topPerformersResponse = await axios.get(
          `${process.env.REACT_APP_API_URL}/api/leaderboard/top?limit=5`, 
          config
        );
        
        // Fetch current user stats
        const currentUserResponse = await axios.get(
          `${process.env.REACT_APP_API_URL}/api/leaderboard/user/current`, 
          config
        );
        
        // Check if requests were successful
        if (!topPerformersResponse.data.success || !currentUserResponse.data.success) {
          throw new Error('Failed to fetch leaderboard data');
        }
        
        setLeaders(topPerformersResponse.data.data);
        setCurrentUserStats(currentUserResponse.data.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching leaderboard data:', err);
        setError('Failed to load leaderboard data. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchData();
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
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Canvas and particle animation setup
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
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
        
        if (this.size <= 0.2 || this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height) {
          this.x = Math.random() * canvas.width;
          this.y = Math.random() * canvas.height;
          this.size = Math.random() * 5 + 1;
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
      
      // Draw mouse trail
      if (mousePosition.x > 0 && mousePosition.y > 0) {
        ctx.beginPath();
        ctx.arc(mousePosition.x, mousePosition.y, 60, 0, Math.PI * 2);
        const gradient = ctx.createRadialGradient(
          mousePosition.x, mousePosition.y, 0,
          mousePosition.x, mousePosition.y, 60
        );
        gradient.addColorStop(0, 'rgba(139, 92, 246, 0.2)');
        gradient.addColorStop(1, 'rgba(139, 92, 246, 0)');
        ctx.fillStyle = gradient;
        ctx.fill();
      }
      
      animationFrameRef.current = requestAnimationFrame(animate);
    };
    
    animate();
    
    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-red-500 text-center max-w-md p-6 bg-gray-800 rounded-lg">
          <h2 className="text-xl font-bold mb-2">Error</h2>
          <p>{error}</p>
          <button 
            className="mt-4 px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
            onClick={() => window.location.reload()}
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Canvas for background animations */}
      <canvas ref={canvasRef} className="animation-canvas" />
      
      {/* Background Elements */}
      <div className="star-effect star-1" />
      <div className="star-effect star-2" />
      <div className="star-effect star-3" />
      <div className="star-effect star-4" />
      <div className="star-effect star-5" />
      
      <div className="mouse-follow-light" style={{
        left: `${mousePosition.x}px`,
        top: `${mousePosition.y}px`
      }} />
      
      <div className="dot-overlay" />
      <div className="glow-circle circle-1 floating" />
      <div className="glow-circle circle-2 floating" />
      <div className="glow-circle circle-3 floating" />
      
      <div className="grid-pattern" />
      <div className="network-lines" />

      {/* Dashboard Content */}
      <div className="dashboard-header">
        <div className="logo-glow" />
        <h1 className="dashboard-title">Leaderboard Rankings</h1>
        <p className="dashboard-subtitle">Top Performers & Stats</p>
        <div className="header-accent" />
      </div>

      <div className="relative z-10 max-w-4xl mx-auto space-y-6">
        <Card className="dashboard-card floating-card">
          <CardHeader className="border-b border-purple-900/30">
            <CardTitle className="text-white flex items-center">
              <Trophy className="w-6 h-6 mr-2 text-yellow-400" />
              <span className="text-glow">Top Performers</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {leaders.map((leader, index) => (
                <div key={index} 
                     className="activity-item flex items-center justify-between p-4 hover:bg-white/5 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center justify-center w-8 h-8">
                      {index === 0 ? <Crown className="w-6 h-6 text-yellow-400" /> :
                       index === 1 ? <Star className="w-6 h-6 text-gray-300" /> :
                       index === 2 ? <Star className="w-6 h-6 text-orange-400" /> :
                       <span className="text-lg font-bold text-gray-300">#{leader.rank}</span>}
                    </div>
                    <div>
                      <p className="font-medium text-white">{leader.username}</p>
                      <div className="flex items-center space-x-2 text-sm text-gray-300">
                        <span>Win rate: {leader.winRate}</span>
                        <span>•</span>
                        <span className="flex items-center">
                          <Flame className="w-4 h-4 mr-1 text-orange-400" />
                          {leader.streak} wins
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center justify-end text-green-400">
                      <ArrowUpRight className="w-4 h-4 mr-1" />
                      <p className="font-bold">+${leader.profit.toLocaleString()}</p>
                    </div>
                    <button className="mt-1 text-sm text-purple-300 hover:text-purple-200 transition-colors">
                      View Profile
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {currentUserStats && (
          <Card className="dashboard-card floating-card">
            <CardHeader className="border-b border-purple-900/30">
              <CardTitle className="text-white flex items-center">
                <TrendingUp className="w-6 h-6 mr-2 text-blue-400" />
                <span className="text-glow">Your Rankings</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="p-4 rounded-lg bg-blue-900/20 border border-blue-500/20">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <span className="text-lg font-bold text-blue-300">#{currentUserStats.rank}</span>
                    <div>
                      <p className="font-medium text-white">You ({currentUserStats.username})</p>
                      <div className="flex items-center space-x-2 text-sm text-gray-300">
                        <span>Win rate: {currentUserStats.winRate}</span>
                        <span>•</span>
                        <span className="flex items-center">
                          <Flame className="w-4 h-4 mr-1 text-orange-400" />
                          {currentUserStats.streak} wins
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center justify-end text-green-400">
                      <ArrowUpRight className="w-4 h-4 mr-1" />
                      <p className="font-bold">+${currentUserStats.profit.toLocaleString()}</p>
                    </div>
                    <p className="text-sm text-blue-300">{currentUserStats.percentile}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
            )}

      </div>
        
      <style jsx>{`
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

        @keyframes float {
          0% { transform: translateY(0px); }
          50% { transform: translateY(-15px); }
          100% { transform: translateY(0px); }
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

        .star-effect {
          position: absolute;
          border-radius: 50%;
          filter: blur(15px);
          opacity: 0.7;
          pointer-events: none;
z-index: 1;
        }

        .star-1 { top: 15%; left: 10%; background: #a855f7; width: 4px; height: 4px; }
        .star-2 { top: 25%; right: 15%; background: #2563eb; width: 6px; height: 6px; }
        .star-3 { top: 45%; left: 20%; background: #8b5cf6; width: 5px; height: 5px; }
        .star-4 { top: 65%; right: 25%; background: #c4b5fd; width: 4px; height: 4px; }
        .star-5 { top: 85%; left: 30%; background: #a855f7; width: 5px; height: 5px; }

        .mouse-follow-light {
          position: fixed;
          pointer-events: none;
          width: 400px;
          height: 400px;
          background: radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, rgba(139, 92, 246, 0) 70%);
          transform: translate(-50%, -50%);
          z-index: 2;
        }

        .dot-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-image: radial-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px);
          background-size: 30px 30px;
          pointer-events: none;
          z-index: 2;
        }

        .glow-circle {
          position: absolute;
          border-radius: 50%;
          filter: blur(40px);
          opacity: 0.2;
          pointer-events: none;
          z-index: 1;
        }

        .circle-1 {
          top: 20%;
          left: 10%;
          width: 300px;
          height: 300px;
          background: #a855f7;
          animation: float 6s ease-in-out infinite;
        }

        .circle-2 {
          top: 60%;
          right: 15%;
          width: 250px;
          height: 250px;
          background: #2563eb;
          animation: float 8s ease-in-out infinite;
        }

        .circle-3 {
          bottom: 10%;
          left: 20%;
          width: 200px;
          height: 200px;
          background: #8b5cf6;
          animation: float 7s ease-in-out infinite;
        }

        .grid-pattern {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-image: linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
          background-size: 50px 50px;
          pointer-events: none;
          z-index: 2;
        }

        .network-lines {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: 
            linear-gradient(45deg, transparent 48%, rgba(255, 255, 255, 0.03) 50%, transparent 52%),
            linear-gradient(-45deg, transparent 48%, rgba(255, 255, 255, 0.03) 50%, transparent 52%);
          background-size: 60px 60px;
          pointer-events: none;
          z-index: 2;
        }

        .floating-card {
          position: relative;
          animation: float 6s ease-in-out infinite;
          background: rgba(23, 23, 23, 0.8);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .activity-item {
          transition: all 0.3s ease;
        }

        .activity-item:hover {
          transform: translateX(5px);
        }

        .text-glow {
          text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
        }
      `}</style>
    </div>
  );
};

export default Leaderboard;