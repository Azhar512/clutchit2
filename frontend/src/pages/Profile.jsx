import React, { useEffect, useState, useRef } from 'react';
import { Bell, Settings, CreditCard, LogOut, Save, X, Edit } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Switch } from "../components/ui/switch";
import { useToast } from "../components/ui/use-toast";
import axios from 'axios';

const Profile = () => {
  const { toast } = useToast();
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const canvasRef = useRef(null);
  const animationFrameRef = useRef(null);
  
  const [userProfile, setUserProfile] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [editedProfile, setEditedProfile] = useState({});
  const [currentView, setCurrentView] = useState('general'); // general, notifications, billing, etc.

  // API URL
  const API_URL = 'http://localhost:5000/api';

  useEffect(() => {
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    try {
      // Get token from localStorage
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        throw new Error("Not authenticated");
      }
      
      // Make request to backend
      const response = await axios.get(`${API_URL}/profile/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setUserProfile(response.data);
      setEditedProfile(response.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching profile:", err);
      setError("Failed to load profile data");
      setLoading(false);
      
      // Handle token refresh or redirect to login if needed
      if (err.response && err.response.status === 401) {
        // Redirect to login
        window.location.href = '/login';
      }
      
      toast({
        title: "Error",
        description: "Failed to load profile data. Please try again.",
        variant: "destructive"
      });
    }
  };

  const updateProfile = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        throw new Error("Not authenticated");
      }
      
      // Make PUT request to update profile
      await axios.put(`${API_URL}/profile/`, editedProfile, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setUserProfile(editedProfile);
      setEditMode(false);
      
      toast({
        title: "Success",
        description: "Profile updated successfully",
        variant: "success"
      });
    } catch (err) {
      console.error("Error updating profile:", err);
      
      toast({
        title: "Error",
        description: "Failed to update profile. Please try again.",
        variant: "destructive"
      });
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setEditedProfile({
      ...editedProfile,
      [name]: value
    });
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  };

  // Mouse movement and animations
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

  // Canvas animation setup code (same as before)
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
      
      // Draw mouse trail
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
  }, [mousePosition]);

  // Setup animation effects
  useEffect(() => {
    const animateStars = () => {
      const stars = document.querySelectorAll('.star-effect');
      stars.forEach((star, index) => {
        setInterval(() => {
          const opacity = 0.6 + Math.random() * 0.4;
          const scale = 0.9 + Math.random() * 0.3;
          star.style.opacity = opacity.toString();
          star.style.transform = `scale(${scale})`;
        }, 2000 + (index * 500));
      });
    };
    
    const floatingElements = () => {
      const elements = document.querySelectorAll('.floating');
      elements.forEach((el, index) => {
        const delay = index * 0.5;
        el.style.animation = `float 8s ease-in-out ${delay}s infinite`;
      });
    };
    
    animateStars();
    floatingElements();
  }, []);

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-900">
        <div className="text-red-500 text-xl">{error}</div>
        <button 
          onClick={fetchUserProfile}
          className="mt-4 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-md text-white"
        >
          Retry
        </button>
      </div>
    );
  }

  // Render account settings based on current view
  const renderSettingsContent = () => {
    switch(currentView) {
      case 'general':
        return (
          <div className="space-y-4">
            {editMode ? (
              <>
                <div className="space-y-3">
                  <label className="text-gray-300 block">Full Name</label>
                  <Input 
                    name="name"
                    value={editedProfile.name || ''}
                    onChange={handleInputChange}
                    className="bg-white/5 border-purple-900/30 text-white"
                  />
                </div>
                <div className="space-y-3">
                  <label className="text-gray-300 block">Username</label>
                  <Input 
                    name="username"
                    value={editedProfile.username || ''}
                    onChange={handleInputChange}
                    className="bg-white/5 border-purple-900/30 text-white"
                  />
                </div>
                <div className="space-y-3">
                  <label className="text-gray-300 block">Email</label>
                  <Input 
                    name="email"
                    value={editedProfile.email || ''}
                    onChange={handleInputChange}
                    className="bg-white/5 border-purple-900/30 text-white"
                  />
                </div>
                <div className="flex justify-end space-x-2 mt-4">
                  <Button 
                    variant="outline" 
                    className="border-red-500/30 text-red-300 hover:bg-red-900/20"
                    onClick={() => {
                      setEditedProfile(userProfile);
                      setEditMode(false);
                    }}
                  >
                    <X className="w-4 h-4 mr-2" /> Cancel
                  </Button>
                  <Button 
                    className="bg-purple-700 hover:bg-purple-600" 
                    onClick={updateProfile}
                  >
                    <Save className="w-4 h-4 mr-2" /> Save Changes
                  </Button>
                </div>
              </>
            ) : (
              <>
                <div className="flex justify-between items-center p-2 hover:bg-white/5 rounded transition-all duration-300">
                  <span className="text-gray-300">Full Name</span>
                  <span className="text-white">{userProfile.name}</span>
                </div>
                <div className="flex justify-between items-center p-2 hover:bg-white/5 rounded transition-all duration-300">
                  <span className="text-gray-300">Username</span>
                  <span className="text-white">@{userProfile.username}</span>
                </div>
                <div className="flex justify-between items-center p-2 hover:bg-white/5 rounded transition-all duration-300">
                  <span className="text-gray-300">Email</span>
                  <span className="text-white">{userProfile.email || "Not set"}</span>
                </div>
                <div className="flex justify-between items-center p-2 hover:bg-white/5 rounded transition-all duration-300">
                  <span className="text-gray-300">Member Since</span>
                  <span className="text-white">{userProfile.joinDate}</span>
                </div>
                <Button 
                  className="mt-4 w-full bg-white/5 hover:bg-white/10 text-white border border-purple-500/20" 
                  onClick={() => setEditMode(true)}
                >
                  <Edit className="w-4 h-4 mr-2" /> Edit Profile
                </Button>
              </>
            )}
          </div>
        );
      case 'notifications':
        return (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-2 hover:bg-white/5 rounded transition-all duration-300">
              <div>
                <span className="text-white block">Betting Notifications</span>
                <span className="text-gray-400 text-sm">Receive alerts about odds changes and bet results</span>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between p-2 hover:bg-white/5 rounded transition-all duration-300">
              <div>
                <span className="text-white block">Email Notifications</span>
                <span className="text-gray-400 text-sm">Receive our newsletter and important updates</span>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between p-2 hover:bg-white/5 rounded transition-all duration-300">
              <div>
                <span className="text-white block">Picks Marketplace</span>
                <span className="text-gray-400 text-sm">Notifications when your picks are purchased</span>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between p-2 hover:bg-white/5 rounded transition-all duration-300">
              <div>
                <span className="text-white block">Game Start Reminders</span>
                <span className="text-gray-400 text-sm">Get notifications when games with your bets start</span>
              </div>
              <Switch defaultChecked />
            </div>
          </div>
        );
      case 'billing':
        return (
          <div className="space-y-4">
            <div className="p-4 border border-purple-500/20 rounded-lg bg-white/5">
              <h3 className="text-white font-medium">Current Plan</h3>
              <div className="mt-2 flex justify-between">
                <span className="text-gray-300">{userProfile.subscription || "Free"}</span>
                <span className="text-purple-400 font-medium">
                  {userProfile.subscription === "Free" ? "$0/month" : 
                   userProfile.subscription === "Pro" ? "$19.99/month" : 
                   userProfile.subscription === "Elite" ? "$49.99/month" : ""}
                </span>
              </div>
            </div>
            <div className="space-y-2">
              <h3 className="text-white font-medium">Available Plans</h3>
              <div className="grid gap-3">
                <div className={`p-3 border rounded-lg ${userProfile.subscription === "Free" ? "border-green-500/50 bg-green-900/10" : "border-purple-500/20 bg-white/5"}`}>
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="text-white">Free</h4>
                      <p className="text-gray-400 text-sm">Basic predictions and general statistics</p>
                    </div>
                    <span className="text-white font-medium">$0/month</span>
                  </div>
                </div>
                <div className={`p-3 border rounded-lg ${userProfile.subscription === "Pro" ? "border-green-500/50 bg-green-900/10" : "border-purple-500/20 bg-white/5"}`}>
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="text-white">Pro</h4>
                      <p className="text-gray-400 text-sm">Advanced predictions and detailed analytics</p>
                    </div>
                    <span className="text-white font-medium">$19.99/month</span>
                  </div>
                </div>
                <div className={`p-3 border rounded-lg ${userProfile.subscription === "Elite" ? "border-green-500/50 bg-green-900/10" : "border-purple-500/20 bg-white/5"}`}>
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="text-white">Elite</h4>
                      <p className="text-gray-400 text-sm">Premium predictions with edge insights and early picks</p>
                    </div>
                    <span className="text-white font-medium">$49.99/month</span>
                  </div>
                </div>
              </div>
            </div>
            <Button className="w-full bg-purple-700 hover:bg-purple-600">
              Upgrade My Subscription
            </Button>
          </div>
        );
      case 'logout':
        handleLogout();
        return null;
      default:
        return null;
    }
  };

  // Main render
  return (
    <div className="dashboard-container min-h-screen bg-gray-900 py-8">
      {/* Canvas for background animations */}
      <canvas ref={canvasRef} className="animation-canvas fixed top-0 left-0 w-full h-full z-0"></canvas>
      
      {/* Background Elements */}
      <div className="star-effect star-1 fixed"></div>
      <div className="star-effect star-2 fixed"></div>
      <div className="star-effect star-3 fixed"></div>
      <div className="star-effect star-4 fixed"></div>
      <div className="star-effect star-5 fixed"></div>
      
      <div className="mouse-follow-light fixed pointer-events-none" style={{
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

      <div className="space-y-6 max-w-3xl mx-auto relative z-10">
        <Card className="dashboard-card floating-card">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row items-center space-y-4 md:space-y-0 md:space-x-6">
              <div className="w-24 h-24 relative overflow-hidden rounded-full bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center">
                <span className="text-3xl font-bold text-white">JD</span>
                <div className="icon-glow"></div>
              </div>
              <div className="text-center md:text-left">
                <h2 className="text-2xl font-bold text-white">{userProfile.name}</h2>
                <p className="text-gray-300">@{userProfile.username}</p>
                <p className="text-sm text-gray-300 mt-1">Member since {userProfile.joinDate}</p>
                <div className="mt-4 flex flex-wrap justify-center md:justify-start gap-2">
                  <span className="px-3 py-1 bg-purple-900/30 text-purple-300 rounded-full text-sm font-medium border border-purple-500/20">
                    {userProfile.subscription}
                  </span>
                  <span className="px-3 py-1 bg-indigo-900/30 text-indigo-300 rounded-full text-sm font-medium border border-indigo-500/20">
                    {userProfile.totalBets} Bets
                  </span>
                  <span className="px-3 py-1 bg-green-900/30 text-green-300 rounded-full text-sm font-medium border border-green-500/20">
                    {userProfile.winRate} Win Rate
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="dashboard-card floating-card">
            <CardHeader className="border-b border-purple-900/30">
              <CardTitle className="text-white">Account Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { icon: Settings, label: 'General Settings' },
                  { icon: Bell, label: 'Notifications' },
                  { icon: CreditCard, label: 'Subscription & Billing' },
                  { icon: LogOut, label: 'Sign Out' }
                ].map((item, index) => (
                  <button key={index} className="w-full flex items-center justify-between p-2 hover:bg-white/5 rounded transition-all duration-300">
                    <div className="flex items-center">
                      <item.icon className="w-5 h-5 mr-3 text-indigo-400" />
                      <span className="text-gray-300">{item.label}</span>
                    </div>
                    <span className="text-gray-400">→</span>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
          
          <Card className="dashboard-card floating-card">
            <CardHeader className="border-b border-purple-900/30">
              <CardTitle className="text-white">Statistics Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { label: 'Win Rate', value: userProfile.winRate },
                  { label: 'Average Odds', value: userProfile.avgOdds },
                  { label: 'Total Bets', value: userProfile.totalBets },
                  { label: 'Profit (YTD)', value: '+$3,250', className: 'text-green-400' },
                  { label: 'Clutch Picks Bought', value: '23' },
                  { label: 'Clutch Picks Sold', value: '8' }
                ].map((stat, index) => (
                  <div key={index} className="flex justify-between items-center p-2 hover:bg-white/5 rounded transition-all duration-300">
                    <span className="text-gray-300">{stat.label}</span>
                    <span className={`font-medium ${stat.className || 'text-white'}`}>{stat.value}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
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

export default Profile;