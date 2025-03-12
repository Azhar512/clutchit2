import React from "react";
import { useState, useRef, useEffect } from 'react';
import { Card, CardHeader, CardContent, CardTitle } from "../components/ui/card";
import { ShoppingCart, Star, Award, Users, TrendingUp, ChevronRight } from 'lucide-react';
import axios from 'axios'; // Make sure axios is installed

const Marketplace = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const canvasRef = useRef(null);
  const animationFrameRef = useRef(null);
  
  // State for data from backend
  const [featuredPicks, setFeaturedPicks] = useState([]);
  const [clutchPicks, setClutchPicks] = useState([]);
  const [trendingCategories, setTrendingCategories] = useState(['NBA', 'NFL', 'MLB', 'UFC']);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Fetch data from backend
  useEffect(() => {
    const fetchMarketplaceData = async () => {
      try {
        setLoading(true);
        
        // Fetch featured picks
        const featuredResponse = await axios.get('/api/marketplace/featured');
        if (featuredResponse.data.success) {
          setFeaturedPicks(featuredResponse.data.data);
        }
        
        // Fetch clutch picks
        const clutchResponse = await axios.get('/api/marketplace/clutch-picks');
        if (clutchResponse.data.success) {
          setClutchPicks(clutchResponse.data.data);
        }
        
        // Fetch trending categories
        const categoriesResponse = await axios.get('/api/marketplace/trending-categories');
        if (categoriesResponse.data.success && categoriesResponse.data.data.length > 0) {
          setTrendingCategories(categoriesResponse.data.data.map(cat => cat.name));
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching marketplace data:', err);
        setError('Failed to load marketplace data. Please try again later.');
        setLoading(false);
        
        // Use sample data as fallback
        setFeaturedPicks([
          {
            title: "Ultimate Parlay Bundle",
            price: 49.99,
            description: "Get access to our top 5 parlays across all major sports with detailed analysis",
            author: "ProBettingTeam",
            rating: 4.9,
            sales: 287,
            image: "/api/placeholder/400/200"
          },
          {
            title: "Weekend Special",
            price: 34.99,
            description: "Full weekend coverage with our best picks across NFL, NBA, and UFC events",
            author: "ElitePicksDaily",
            rating: 4.8,
            sales: 176,
            image: "/api/placeholder/400/200"
          }
        ]);
        
        setClutchPicks([
          {
            author: "TopBettor",
            title: "NBA Parlay Special",
            description: "3-team parlay with detailed analysis",
            price: 29.99,
            rating: 4.8,
            sales: 156,
            trending: true,
            popularTag: "Top Seller"
          },
          {
            author: "BettingPro",
            title: "MLB Daily Picks",
            description: "Top baseball picks for today",
            price: 19.99,
            rating: 4.6,
            sales: 89,
            trending: false,
            popularTag: "Hot Pick"
          },
          {
            author: "ClutchMaster",
            title: "NFL Week 5 Locks",
            description: "Best football picks of the week",
            price: 24.99,
            rating: 4.7,
            sales: 112,
            trending: true,
            popularTag: "Featured"
          },
          {
            author: "OddsExpert",
            title: "NHL Special",
            description: "Expert hockey analysis and picks",
            price: 17.99,
            rating: 4.5,
            sales: 76,
            trending: false,
            popularTag: "Value Pick"
          }
        ]);
      }
    };
    
    fetchMarketplaceData();
  }, []);
  
  // Handle purchase click
  const handlePurchase = async (pickId) => {
    try {
      // Check if user is logged in
      const token = localStorage.getItem('auth_token');
      if (!token) {
        // Redirect to login or show login modal
        alert('Please log in to purchase picks');
        return;
      }
      
      const response = await axios.post('/api/marketplace/purchase', 
        { pick_id: pickId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        alert('Pick purchased successfully!');
        // Optional: Update UI to show purchase was successful
      } else {
        alert(response.data.message || 'Purchase failed. Please try again.');
      }
    } catch (err) {
      console.error('Error purchasing pick:', err);
      alert('Error processing your purchase. Please try again later.');
    }
  };

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
  
  // Animate light effects
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

  // Show loading state
  if (loading) {
    return (
      <div className="marketplace-container flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="spinner"></div>
          <p className="mt-4 text-white">Loading marketplace...</p>
        </div>
      </div>
    );
  }
  
  // Show error state
  if (error) {
    return (
      <div className="marketplace-container flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="text-red-500 text-2xl mb-4">⚠️</div>
          <p className="text-white">{error}</p>
          <button 
            className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-md"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="marketplace-container">
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
      
      {/* Marketplace Header */}
      <div className="marketplace-header">
        <div className="logo-glow"></div>
        <h1 className="marketplace-title">Clutch Picks Marketplace</h1>
        <p className="marketplace-subtitle">Premium Picks from Elite Bettors</p>
        <div className="header-accent"></div>
      </div>

      {/* Featured Picks */}
      <div className="mb-8 relative z-10">
        <h2 className="text-white text-xl font-bold mb-4 flex items-center">
          <Award className="mr-2 text-purple-400 w-5 h-5" />
          <span className="text-glow">Featured Picks</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {featuredPicks.map((pick, index) => (
            <Card key={index} className="featured-card relative overflow-hidden">
              <div className="card-shine"></div>
              <img 
                src={pick.image} 
                alt={pick.title}
                className="w-full h-48 object-cover" 
              />
              <CardContent className="relative p-6">
                <div className="absolute -top-4 right-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                  Premium
                </div>
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-bold text-lg text-white">{pick.title}</h3>
                    <p className="text-sm text-purple-300">by {pick.author}</p>
                  </div>
                  <span className="text-xl font-bold text-white">${pick.price}</span>
                </div>
                <p className="mt-2 text-sm text-gray-300">{pick.description}</p>
                <div className="mt-4 flex justify-between items-center">
                  <div className="flex items-center">
                    <div className="flex">
                      {[...Array(5)].map((_, i) => (
                        <Star 
                          key={i} 
                          className={`w-4 h-4 ${i < Math.floor(pick.rating) ? 'text-yellow-400' : 'text-gray-600'}`}
                          fill={i < Math.floor(pick.rating) ? 'currentColor' : 'none'}
                        />
                      ))}
                    </div>
                    <span className="ml-1 text-sm text-gray-300">{pick.rating}</span>
                    <span className="ml-2 text-sm text-gray-400">({pick.sales} sales)</span>
                  </div>
                  <button 
                    className="purchase-btn flex items-center"
                    onClick={() => handlePurchase(pick.id)}
                  >
                    <span>Purchase</span>
                    <ShoppingCart className="ml-2 w-4 h-4" />
                  </button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Trending Categories */}
      <div className="categories-section mb-8 relative z-10">
        <h2 className="text-white text-xl font-bold mb-4 flex items-center">
          <TrendingUp className="mr-2 text-cyan-400 w-5 h-5" />
          <span className="text-glow">Trending Categories</span>
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {trendingCategories.map((category, index) => (
            <div key={index} className="category-card floating">
              <div className="category-glow"></div>
              <span>{category}</span>
              <ChevronRight className="w-5 h-5 text-purple-300" />
            </div>
          ))}
        </div>
      </div>

      {/* Clutch Picks */}
      <div className="clutch-picks-section relative z-10">
        <h2 className="text-white text-xl font-bold mb-4 flex items-center">
          <Users className="mr-2 text-indigo-400 w-5 h-5" />
          <span className="text-glow">Premium Picks</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {clutchPicks.map((pick, index) => (
            <Card key={index} className="clutch-pick-card floating-card">
              <CardContent className="p-5">
                {pick.trending && (
                  <div className="trending-badge">
                    <span>{pick.popularTag}</span>
                    <div className="pulse-dot"></div>
                  </div>
                )}
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-white text-glow">{pick.title}</h3>
                    <p className="text-sm text-gray-400">by {pick.author}</p>
                  </div>
                  <span className="text-lg font-bold text-white">${pick.price}</span>
                </div>
                <p className="mt-2 text-sm text-gray-400">{pick.description}</p>
                <div className="mt-4 flex justify-between items-center">
                  <div className="flex items-center">
                    <div className="flex">
                      {[...Array(5)].map((_, i) => (
                        <Star 
                          key={i} 
                          className={`w-3 h-3 ${i < Math.floor(pick.rating) ? 'text-yellow-400' : 'text-gray-600'}`}
                          fill={i < Math.floor(pick.rating) ? 'currentColor' : 'none'}
                        />
                      ))}
                    </div>
                    <span className="ml-1 text-xs text-gray-300">{pick.rating}</span>
                    <span className="ml-2 text-xs text-gray-500">({pick.sales})</span>
                  </div>
                  <button className="small-purchase-btn">
                    Purchase
                  </button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Add enhanced CSS for the beautiful effects */}
      <style jsx>{`
        @keyframes float {
          0% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
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
        
        @keyframes shine {
          0% { left: -100%; opacity: 0; }
          50% { opacity: 0.7; }
          100% { left: 100%; opacity: 0; }
        }
        
        .marketplace-container {
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
        
        .marketplace-header {
          text-align: center;
          margin-bottom: 3rem;
          position: relative;
          z-index: 10;
          padding: 1.5rem 0;
        }
        
        .marketplace-title {
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
        
        .marketplace-subtitle {
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
        
        .clutch-pick-card {
          background-color: rgba(30, 10, 60, 0.5);
          backdrop-filter: blur(12px);
          border: 1px solid rgba(168, 85, 247, 0.1);
          border-radius: 16px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
          overflow: hidden;
          position: relative;
          transition: all 0.3s ease;
        }
        
        .clutch-pick-card:before {
          content: '';
          position: absolute;
          top: -1px;
          left: -1px;
          right: -1px;
          height: 2px;
          background: linear-gradient(90deg, rgba(139, 92, 246, 0), rgba(139, 92, 246, 0.6), rgba(139, 92, 246, 0));
          z-index: 1;
        }
        
        .clutch-pick-card:after {
          content: '';
          position: absolute;
          bottom: 0;
          left: 0;
          width: 100%;
          height: 30%;
          background: linear-gradient(to top, rgba(139, 92, 246, 0.05), transparent);
          z-index: 0;
        }
        
        .featured-card {
          background-color: rgba(40, 15, 75, 0.6);
          backdrop-filter: blur(15px);
          border: 1px solid rgba(168, 85, 247, 0.2);
          border-radius: 16px;
          box-shadow: 0 10px 40px rgba(76, 29, 149, 0.3);
          overflow: hidden;
          transition: all 0.4s ease;
        }
        
        .featured-card:hover {
          transform: translateY(-8px);
          box-shadow: 0 15px 50px rgba(139, 92, 246, 0.4);
        }
        
        .card-shine {
          position: absolute;
          top: 0;
          left: -100%;
          width: 50%;
          height: 100%;
          background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.1),
            transparent
          );
          transform: skewX(-15deg);
          z-index: 2;
          animation: shine 4s infinite;
        }
        
        .purchase-btn {
          background: linear-gradient(90deg, #a855f7, #6366f1);
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 2rem;
          font-weight: 600;
          font-size: 0.875rem;
          transition: all 0.3s ease;
          box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
          display: flex;
          align-items: center;
        }
        
        .purchase-btn:hover {
          box-shadow: 0 6px 15px rgba(139, 92, 246, 0.5);
          transform: translateY(-2px);
        }
        
        .small-purchase-btn {
          background: linear-gradient(90deg, #a855f7, #6366f1);
          color: white;
          border: none;
          padding: 0.25rem 0.75rem;
          border-radius: 2rem;
          font-weight: 600;
          font-size: 0.75rem;
          transition: all 0.3s ease;
          box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
        }
        
        .small-purchase-btn:hover {
          box-shadow: 0 6px 15px rgba(139, 92, 246, 0.5);
          transform: translateY(-2px);
        }
        
        .floating-card {
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .floating-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 12px 40px rgba(76, 29, 149, 0.3);
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
        
       `}</style>
    </div>
  );
};
export default Marketplace;