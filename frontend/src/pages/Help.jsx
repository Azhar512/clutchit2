import React from "react";
import { Search, FileQuestion, MessageCircle, ExternalLink, HelpCircle, Book, CreditCard, Upload, ShoppingBag, Zap } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Help = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const canvasRef = useRef(null);
  const animationFrameRef = useRef(null);
  const navigate = useNavigate();
  
  // State for data from API
  const [faqCategories, setFaqCategories] = useState([]);
  const [popularQuestions, setPopularQuestions] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState({
    categories: false,
    questions: false
  });
  const [error, setError] = useState({
    categories: null,
    questions: null
  });

  // Define icons map for category icons
  const categoryIconMap = {
    'account': HelpCircle,
    'billing': CreditCard,
    'bets': ShoppingBag,
    'predictions': Zap,
    'technical': FileQuestion,
    'general': Book,
    'uploads': Upload,
    'support': MessageCircle
  };

  // Fetch FAQ categories and popular questions from API
  useEffect(() => {
    const fetchFaqCategories = async () => {
      setLoading(prev => ({ ...prev, categories: true }));
      try {
        // Updated to use your Flask backend endpoint
        const response = await axios.get('/api/help/categories');
        setFaqCategories(response.data.categories.map(category => ({
          ...category,
          icon: categoryIconMap[category.slug] || HelpCircle
        })));
      } catch (err) {
        console.error("Error fetching FAQ categories:", err);
        setError(prev => ({ ...prev, categories: err.message || 'Failed to fetch categories' }));
      } finally {
        setLoading(prev => ({ ...prev, categories: false }));
      }
    };

    const fetchPopularQuestions = async () => {
      setLoading(prev => ({ ...prev, questions: true }));
      try {
        // Updated to use your Flask backend endpoint
        const response = await axios.get('/api/help/popular-questions');
        setPopularQuestions(response.data.questions);
      } catch (err) {
        console.error("Error fetching popular questions:", err);
        setError(prev => ({ ...prev, questions: err.message || 'Failed to fetch popular questions' }));
      } finally {
        setLoading(prev => ({ ...prev, questions: false }));
      }
    };

    fetchFaqCategories();
    fetchPopularQuestions();
  }, []);

  // Handle search input change
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  // Handle search submission
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim().length >= 3) {
      navigate(`/help/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  // Handle category click
  const handleCategoryClick = (categorySlug) => {
    navigate(`/help/category/${categorySlug}`);
  };

  // Handle question click
  const handleQuestionClick = (questionId) => {
    navigate(`/help/faq/${questionId}`);
  };

  // Handle contact support
  const handleContactSupport = () => {
    navigate('/help/contact');
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
          'rgba(168, 85, 247, 0.4)',  
          'rgba(139, 92, 246, 0.3)',  
          'rgba(79, 70, 229, 0.3)',  
          'rgba(191, 219, 254, 0.2)', 
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
    
    const particleArray = [];
    const particleCount = Math.min(100, window.innerWidth / 20);
    
    for (let i = 0; i < particleCount; i++) {
      particleArray.push(new Particle());
    }
    
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
    
    
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
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
        <h1 className="dashboard-title">Help Center</h1>
        <p className="dashboard-subtitle">Find answers to all your questions</p>
        <div className="header-accent"></div>
      </div>

      {/* Main Content Area */}
      <div className="space-y-6 max-w-3xl mx-auto z-10 relative">
        <Card className="dashboard-card search-card floating-card">
          <CardContent className="p-6">
            <h2 className="text-2xl font-bold text-center mb-6 text-white">How can we help you?</h2>
            <form onSubmit={handleSearchSubmit} className="relative">
              <input
                type="text"
                placeholder="Search for answers..."
                className="w-full p-3 pl-10 bg-purple-900/30 text-white border border-purple-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 placeholder-purple-300"
                value={searchQuery}
                onChange={handleSearchChange}
                minLength={3}
              />
              <Search className="w-5 h-5 text-purple-300 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <button 
                type="submit"
                className="absolute right-3 top-1/2 transform -translate-y-1/2 bg-indigo-600 text-white px-3 py-1 rounded-md text-sm hover:bg-indigo-500 transition-colors duration-200"
                disabled={searchQuery.trim().length < 3}
              >
                Search
              </button>
              <div className="search-glow"></div>
            </form>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="dashboard-card faq-card floating-card">
            <CardHeader className="border-b border-purple-900/30">
              <CardTitle className="text-white flex items-center">
                <span className="text-glow">FAQ Categories</span>
                <div className="ml-2 w-2 h-2 bg-cyan-400 rounded-full pulse-animation"></div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading.categories ? (
                <div className="flex justify-center items-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-indigo-400"></div>
                </div>
              ) : error.categories ? (
                <div className="text-center py-8 text-red-400">
                  <p>Unable to load categories. Please try again later.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {faqCategories.length > 0 ? faqCategories.map((category) => (
                    <button 
                      key={category.id || category.slug} 
                      className="w-full flex items-center justify-between p-3 hover:bg-purple-800/20 rounded-lg transition-all duration-300"
                      onClick={() => handleCategoryClick(category.slug)}
                    >
                      <div className="flex items-center">
                        <div className="icon-container">
                          {React.createElement(category.icon, { className: "w-5 h-5 text-indigo-400" })}
                          <div className="icon-glow"></div>
                        </div>
                        <span className="ml-3 text-purple-100">{category.title}</span>
                      </div>
                      <span className="text-sm text-purple-300">{category.count} articles</span>
                    </button>
                  )) : (
                    <div className="text-center py-4 text-purple-300">
                      <p>No categories available</p>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
          
          <Card className="dashboard-card popular-card floating-card">
            <CardHeader className="border-b border-purple-900/30">
              <CardTitle className="text-white flex items-center">
                <span className="text-glow">Popular Questions</span>
                <div className="ml-2 w-2 h-2 bg-cyan-400 rounded-full pulse-animation"></div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading.questions ? (
                <div className="flex justify-center items-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-indigo-400"></div>
                </div>
              ) : error.questions ? (
                <div className="text-center py-8 text-red-400">
                  <p>Unable to load popular questions. Please try again later.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {popularQuestions.length > 0 ? popularQuestions.map((question) => (
                    <button 
                      key={question.id} 
                      className="w-full text-left flex items-center p-3 hover:bg-purple-800/20 rounded-lg transition-all duration-300"
                      onClick={() => handleQuestionClick(question.id)}
                    >
                      <div className="activity-indicator activity-question mr-3"></div>
                      <span className="text-sm text-purple-100">{question.title}</span>
                    </button>
                  )) : (
                    <div className="text-center py-4 text-purple-300">
                      <p>No popular questions available</p>
                    </div>
                  )}
                  <button 
                    className="w-full flex items-center justify-center p-3 text-indigo-400 hover:bg-purple-800/20 rounded-lg mt-4 transition-all duration-300"
                    onClick={() => navigate('/help/all-faqs')}
                  >
                    <span>View all FAQs</span>
                    <ExternalLink className="w-4 h-4 ml-1" />
                  </button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <Card className="dashboard-card contact-card floating-card">
          <CardHeader className="border-b border-purple-900/30">
            <CardTitle className="text-white flex items-center">
              <span className="text-glow">Contact Support</span>
              <div className="ml-2 w-2 h-2 bg-cyan-400 rounded-full pulse-animation"></div>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row items-center space-y-4 md:space-y-0 md:space-x-6">
              <div className="w-16 h-16 bg-indigo-900/50 rounded-full flex items-center justify-center relative">
                <MessageCircle className="w-8 h-8 text-indigo-400" />
                <div className="absolute inset-0 rounded-full bg-indigo-500/20 pulse-border"></div>
              </div>
              <div>
                <h3 className="text-lg font-medium text-white">Need more help?</h3>
                <p className="text-purple-300 mb-4">Our support team is ready to assist you with any questions or issues.</p>
                <button className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-500 hover:to-purple-500 transition-all duration-300 relative overflow-hidden">
                  <span className="relative z-10">Contact Support</span>
                  <div className="absolute inset-0 bg-white opacity-0 hover:opacity-20 transition-opacity duration-300"></div>
                </button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

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
        
        @keyframes pulseBorder {
          0% { transform: scale(1); opacity: 0.6; }
          100% { transform: scale(1.5); opacity: 0; }
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
          width: 30px;
          height: 30px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .icon-glow {
          position: absolute;
          width: 25px;
          height: 25px;
          border-radius: 50%;
          background: radial-gradient(circle, rgba(139, 92, 246, 0.5) 0%, rgba(139, 92, 246, 0) 70%);
          filter: blur(5px);
          z-index: -1;
          animation: glow 2s ease-in-out infinite;
        }
        
        .activity-indicator {
          position: relative;
          width: 6px;
          height: 6px;
          border-radius: 50%;
        }
        
        .activity-indicator:after {
          content: '';
          position: absolute;
          top: -4px;
          left: -4px;
          width: 14px;
          height: 14px;
          border-radius: 50%;
          filter: blur(6px);
          z-index: -1;
          opacity: 0.7;
        }
        
        .activity-question {
          background: #a855f7;
          box-shadow: 0 0 10px #a855f7;
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
        
        .pulse-border {
          animation: pulseBorder 2s infinite;
        }
        
        .floating {
          animation: float 6s ease-in-out infinite;
        }
        
        .search-glow {
          position: absolute;
          bottom: -10px;
          left: 50%;
          transform: translateX(-50%);
          width: 80%;
          height: 10px;
          background: radial-gradient(ellipse at center, rgba(168, 85, 247, 0.3) 0%, rgba(168, 85, 247, 0) 70%);
          filter: blur(4px);
        }
      `}</style>
    </div>
  );
};

export default Help;
