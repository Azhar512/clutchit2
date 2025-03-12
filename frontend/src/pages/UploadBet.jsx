import React from "react";
import { Upload, Image, FileText } from 'lucide-react';
import { Card, CardHeader, CardContent, CardTitle } from '../components/ui/card';
import { useEffect, useState, useRef } from 'react';
import axios from 'axios'; 

const UploadBet = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);
  const canvasRef = useRef(null);
  const animationFrameRef = useRef(null);
  
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

  // File validation function
  const validateFile = (file) => {
    // Check file type
    const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
      setUploadStatus({
        type: 'error',
        message: 'Invalid file type. Please upload JPG, PNG, or PDF files only.'
      });
      return false;
    }
    
    // Check file size (10MB limit)
    const maxSize = 10 * 1024 * 1024; // 10MB in bytes
    if (file.size > maxSize) {
      setUploadStatus({
        type: 'error',
        message: 'File too large. Maximum size is 10MB.'
      });
      return false;
    }
    
    return true;
  };

  // Handle file selection
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    if (validateFile(file)) {
      setSelectedFile(file);
      setUploadStatus({
        type: 'info',
        message: `File "${file.name}" selected. Click Upload to submit.`
      });
    }
  };

  // Handle click on upload button
  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  // Handle manual entry button click
  const handleManualEntryClick = () => {
    // Navigate to manual entry form
    // This depends on your routing implementation
    // Example: history.push('/manual-bet-entry');
    console.log('Navigate to manual entry form');
  };

  // Handle drag and drop events
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files[0];
    if (!file) return;
    
    if (validateFile(file)) {
      setSelectedFile(file);
      setUploadStatus({
        type: 'info',
        message: `File "${file.name}" selected. Click Upload to submit.`
      });
    }
  };

  // Submit file to backend
  const handleSubmit = async () => {
    if (!selectedFile) {
      setUploadStatus({
        type: 'error',
        message: 'Please select a file first.'
      });
      return;
    }
    
    setIsUploading(true);
    setUploadStatus({
      type: 'info',
      message: 'Uploading bet slip...'
    });
    
    // Create form data
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
      // Get auth token from localStorage (adjust based on your auth implementation)
      const token = localStorage.getItem('token');
      
      // Send file to backend
      const response = await axios.post('/api/bets/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        }
      });
      
      // Handle successful upload
      setUploadStatus({
        type: 'success',
        message: 'Bet slip uploaded successfully! Analyzing your bet...'
      });
      
      // Redirect to bet analysis page after short delay
      setTimeout(() => {
        // Navigate to bet analysis page with the bet ID
        // This depends on your routing implementation
        // Example: history.push(`/bet/${response.data.bet_id}`);
        console.log('Navigate to bet analysis page', response.data.bet_id);
      }, 2000);
      
    } catch (error) {
      console.error('Error uploading bet slip:', error);
      setUploadStatus({
        type: 'error',
        message: error.response?.data?.error || 'Failed to upload bet slip. Please try again.'
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="upload-container">
      {/* Canvas for background animations */}
      <canvas ref={canvasRef} className="animation-canvas"></canvas>
      
      {/* Background Elements */}
      <div className="star-effect star-1"></div>
      <div className="star-effect star-2"></div>
      <div className="star-effect star-3"></div>
      
      <div className="mouse-follow-light" style={{
        left: `${mousePosition.x}px`,
        top: `${mousePosition.y}px`
      }}></div>
      
      <div className="dot-overlay"></div>
      <div className="glow-circle circle-1 floating"></div>
      <div className="glow-circle circle-2 floating"></div>
      
      {/* Upload Content */}
      <div className="page-content">
        <div className="upload-header">
          <h1 className="upload-title">Upload Your Bet</h1>
          <p className="upload-subtitle">Share your winning strategy</p>
          <div className="header-accent"></div>
        </div>

        <Card className="upload-card floating-card z-10 relative">
          <CardHeader className="border-b border-purple-900/30">
            <CardTitle className="text-white flex items-center">
              <span className="text-glow">Bet Slip Upload</span>
              <div className="ml-2 w-2 h-2 bg-cyan-400 rounded-full pulse-animation"></div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div 
              className={`dropzone ${isDragging ? 'active-drag' : ''} ${isUploading ? 'uploading' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                style={{ display: 'none' }} 
                accept=".jpg,.jpeg,.png,.pdf" 
                onChange={handleFileSelect} 
              />
              
              <div className="icon-container upload-icon">
                <Upload className="w-12 h-12 text-indigo-400" />
                <div className="icon-glow upload-glow"></div>
              </div>
              
              {selectedFile ? (
                <p className="mt-4 text-lg text-indigo-200">
                  Selected: {selectedFile.name}
                </p>
              ) : (
                <p className="mt-4 text-lg text-indigo-200">
                  Drag and drop your bet slip here, or click to browse
                </p>
              )}
              
              {uploadStatus && (
                <div className={`mt-3 text-sm ${
                  uploadStatus.type === 'error' ? 'text-red-400' : 
                  uploadStatus.type === 'success' ? 'text-green-400' : 
                  'text-indigo-300'
                }`}>
                  {uploadStatus.message}
                </div>
              )}
              
              <div className="mt-6 flex justify-center space-x-4">
                {selectedFile ? (
                  <button 
                    className="btn-primary" 
                    onClick={handleSubmit}
                    disabled={isUploading}
                  >
                    {isUploading ? 'Uploading...' : 'Submit Bet'}
                  </button>
                ) : (
                  <button className="btn-primary" onClick={handleUploadClick}>
                    <Image className="w-5 h-5 mr-2" />
                    Upload Image
                  </button>
                )}
                <button className="btn-secondary" onClick={handleManualEntryClick}>
                  <FileText className="w-5 h-5 mr-2" />
                  Enter Manually
                </button>
              </div>
              <div className="upload-hint">
                <p className="text-sm text-indigo-300 mt-4">
                  Supported formats: JPG, PNG, PDF • Max size: 10MB
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Add enhanced CSS for the beautiful effects */}
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
        
        @keyframes gradientShift {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        
        .upload-container {
          position: relative;
          min-height: 100vh;
          padding: 2rem;
          background: linear-gradient(135deg, #2e0068 0%, #1c0050 40%, #10002b 100%);
          color: white;
          overflow: hidden;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
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
        
        .page-content {
          position: relative;
          z-index: 10;
          width: 100%;
          max-width: 640px;
          margin: 0 auto;
        }
        
        .upload-header {
          text-align: center;
          margin-bottom: 2rem;
          position: relative;
          z-index: 10;
        }
        
        .upload-title {
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
        
        .upload-subtitle {
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
        
        .upload-card {
          background-color: rgba(30, 10, 60, 0.5);
          backdrop-filter: blur(12px);
          border: 1px solid rgba(168, 85, 247, 0.1);
          border-radius: 16px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
          overflow: hidden;
          position: relative;
          transition: all 0.3s ease;
          width: 100%;
        }
        
        .upload-card:before {
          content: '';
          position: absolute;
          top: -1px;
          left: -1px;
          right: -1px;
          height: 2px;
          background: linear-gradient(90deg, rgba(139, 92, 246, 0), rgba(139, 92, 246, 0.6), rgba(139, 92, 246, 0));
          z-index: 1;
        }
        
        .upload-card:after {
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
        
        .dropzone {
          border: 2px dashed rgba(168, 85, 247, 0.3);
          border-radius: 12px;
          padding: 2.5rem 1.5rem;
          text-align: center;
          background-color: rgba(76, 29, 149, 0.1);
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
        }
        
        .dropzone:before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(135deg, 
            rgba(139, 92, 246, 0.05) 0%, 
            rgba(139, 92, 246, 0) 50%,
            rgba(139, 92, 246, 0.05) 100%);
          z-index: -1;
          opacity: 0.5;
        }
        
        .active-drag {
          background-color: rgba(76, 29, 149, 0.2);
          border-color: rgba(168, 85, 247, 0.8);
          transform: scale(1.02);
          box-shadow: 0 0 20px rgba(168, 85, 247, 0.2);
        }
        
        .uploading {
          background-color: rgba(76, 29, 149, 0.15);
          border-color: rgba(168, 85, 247, 0.6);
        }
        
        .icon-container {
          position: relative;
          width: 80px;
          height: 80px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto;
        }
        
        .upload-icon {
          animation: float 6s ease-in-out infinite;
        }
        
        .icon-glow {
          position: absolute;
          width: 60px;
          height: 60px;
          border-radius: 50%;
          background: radial-gradient(circle, rgba(139, 92, 246, 0.5) 0%, rgba(139, 92, 246, 0) 70%);
          filter: blur(8px);
          z-index: -1;
          animation: glow 2s ease-in-out infinite;
        }
        
        .upload-glow {
          width: 80px;
          height: 80px;
        }
        
        .btn-primary {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0.75rem 1.25rem;
          background: linear-gradient(135deg, #a855f7 0%, #7c3aed 100%);
          color: white;
          font-weight: 500;
          border-radius: 8px;
          transition: all 0.3s ease;
          border: none;
          box-shadow: 0 4px 10px rgba(124, 58, 237, 0.3);
          position: relative;
          overflow: hidden;
        }
        
        .btn-primary:before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
          transition: all 0.5s ease;
        }
        
        .btn-primary:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 15px rgba(124, 58, 237, 0.4);
        }
        
        .btn-primary:hover:before {
          left: 100%;
        }
        
        .btn-primary:disabled {
          opacity: 0.7;
          cursor: not-allowed;
          transform: none;
        }
        
        .btn-secondary {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0.75rem 1.25rem;
          background: rgba(139, 92, 246, 0.1);
          border: 1px solid rgba(139, 92, 246, 0.3);
          color: #d8b4fe;
          font-weight: 500;
          border-radius: 8px;
          transition: all 0.3s ease;
          box-shadow: 0 4px 10px rgba(139, 92, 246, 0.1);
        }
        
        .btn-secondary:hover {
          background: rgba(139, 92, 246, 0.2);
          transform: translateY(-2px);
          box-shadow: 0 6px 15px rgba(139, 92, 246, 0.2);
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
          background: radial-gradient(circle, rgba(168,85,247,0.6) 0%, rgba(173,216,230,0) 70%);
        }
        
        .star-2 {
          bottom: 25%;
          left: 10%;
          width: 150px;
          height: 150px;
          background: radial-gradient(circle, rgba(76,29,149,0.6) 0%, rgba(173,216,230,0) 70%);
        }
        
        .star-3 {
          top: 35%;
          left: 30%;
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
        
        .upload-hint {
          position: relative;
          margin-top: 1rem;
        }
        
        .upload-hint:before {
          content: '';
          position: absolute;
          top: -10px;
          left: 50%;
          transform: translateX(-50%);
          width: 40px;
          height: 2px;
          background: rgba(139, 92, 246, 0.3);
          border-radius: 2px;
        }
      `}</style>
    </div>
  );
};

export default UploadBet;