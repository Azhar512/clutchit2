import React, { useState, useRef, useEffect } from 'react';
import { 
  BarChart3, Upload, ShoppingBag, Wallet, 
  Trophy, User, HelpCircle, Menu, X 
} from 'lucide-react';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const canvasRef = useRef(null);
  const animationFrameRef = useRef(null);
  
  const menuItems = [
    { icon: BarChart3, label: 'Dashboard', path: '/' },
    { icon: Upload, label: 'Upload Bet', path: '/upload' },
    { icon: ShoppingBag, label: 'Marketplace', path: '/marketplace' },
    { icon: Wallet, label: 'Bankroll', path: '/bankroll' },
    { icon: Trophy, label: 'Leaderboard', path: '/leaderboard' },
    { icon: User, label: 'Profile', path: '/profile' },
    { icon: HelpCircle, label: 'Help', path: '/help' },
  ];

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
    <div className="app-container min-h-screen">
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
      
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 sidebar-background backdrop-blur-lg transform ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } lg:translate-x-0 transition-transform duration-200 ease-in-out overflow-hidden`}>
        <div className="relative z-10">
          <div className="flex items-center justify-between h-16 px-4 border-b border-purple-900/30">
            <span className="text-2xl font-bold text-glow text-white">Clutch It</span>
            <button onClick={() => setSidebarOpen(false)} className="lg:hidden text-white hover:text-purple-300 transition-colors">
              <X className="w-6 h-6" />
            </button>
          </div>
          <nav className="p-4">
            {menuItems.map((item, index) => (
              <a 
                key={index} 
                href={item.path} 
                className="flex items-center px-4 py-3 my-1 text-gray-200 rounded-lg hover:bg-white/10 transition-all duration-200 hover:text-white group"
              >
                <div className="relative">
                  <item.icon className="w-5 h-5 mr-3 group-hover:text-purple-300 transition-colors" />
                  <div className="absolute inset-0 bg-purple-500/20 rounded-full scale-0 group-hover:scale-150 opacity-0 group-hover:opacity-100 blur-md transition-all duration-300"></div>
                </div>
                <span>{item.label}</span>
              </a>
            ))}
          </nav>
          <div className="glow-circle sidebar-glow"></div>
        </div>
      </div>

      {/* Main Content */}
      <div className="lg:pl-64 relative z-10">
        <header className="fixed top-0 right-0 left-0 lg:left-64 h-16 header-background backdrop-blur-md z-40">
          <div className="flex items-center justify-between h-full px-4 relative z-10">
            <button onClick={() => setSidebarOpen(true)} className="lg:hidden text-white hover:text-purple-300 transition-colors">
              <Menu className="w-6 h-6" />
            </button>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-white">John Doe</span>
              <div className="w-8 h-8 bg-purple-600/30 rounded-full border border-purple-500/50 backdrop-blur-sm glow-effect"></div>
            </div>
          </div>
        </header>
        <main className="pt-16 p-4 relative z-10">{children}</main>
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
        
        .app-container {
          position: relative;
          background: linear-gradient(135deg, #2e0068 0%, #1c0050 40%, #10002b 100%);
          color: white;
          overflow: hidden;
        }
        
        .animation-canvas {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          z-index: 1;
          pointer-events: none;
        }
        
        .sidebar-background {
          background-color: rgba(30, 10, 60, 0.5);
          border-right: 1px solid rgba(168, 85, 247, 0.1);
          box-shadow: 5px 0 20px rgba(0, 0, 0, 0.2);
        }
        
        .header-background {
          background-color: rgba(30, 10, 60, 0.4);
          border-bottom: 1px solid rgba(168, 85, 247, 0.1);
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        
        .text-glow {
          text-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
        }
        
        .star-effect {
          position: fixed;
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
          position: fixed;
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
        
        .sidebar-glow {
          bottom: 10%;
          left: 10%;
          width: 150px;
          height: 150px;
          background: rgba(168, 85, 247, 0.1);
          z-index: -1;
        }
        
        .grid-pattern {
          position: fixed;
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
          position: fixed;
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
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-image: radial-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px);
          background-size: 30px 30px;
          z-index: 1;
          pointer-events: none;
        }
        
        .glow-effect {
          position: relative;
        }
        
        .glow-effect:after {
          content: '';
          position: absolute;
          top: -4px;
          left: -4px;
          right: -4px;
          bottom: -4px;
          background: rgba(139, 92, 246, 0.3);
          border-radius: 50%;
          z-index: -1;
          filter: blur(8px);
        }
        
        .floating {
          animation: float 6s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
};

export default Layout;