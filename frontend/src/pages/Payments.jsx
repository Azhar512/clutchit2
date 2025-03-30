import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { CreditCard, Zap, Users, Trophy } from 'lucide-react';

const DEFAULT_SUBSCRIPTION_PLANS = [
    {
      id: 'basic_plan',
      name: 'Basic',
      price: 10,
      totalCredits: 600,
      aiPredictionCredits: 300,
      betUploadCredits: 300,
      features: [
        'Limited AI picks & bet uploads',
        'Basic Vault Access'
      ],
      stripePriceId: 'price_basic'
    },
    {
      id: 'premium_plan',
      name: 'Premium',
      price: 20,
      totalCredits: 1200,
      aiPredictionCredits: 600,
      betUploadCredits: 600,
      features: [
        'Vault access',
        'Hedge alerts',
        'More bet uploads'
      ],
      stripePriceId: 'price_premium'
    },
    {
      id: 'unlimited_plan',
      name: 'Unlimited',
      price: 40,
      totalCredits: 'Unlimited',
      aiPredictionCredits: 'Unlimited',
      betUploadCredits: 'Unlimited',
      features: [
        'Full AI insights',
        'Bankroll tracking',
        'VIP access'
      ],
      stripePriceId: 'price_unlimited'
    }
  ];
  
  const DEFAULT_CREDIT_PACKAGES = [
    { 
      id: 'credits_10', 
      credits: 10, 
      price: 4.99, 
      stripePriceId: 'price_10credits' 
    },
    { 
      id: 'credits_50', 
      credits: 50, 
      price: 19.99, 
      stripePriceId: 'price_50credits' 
    },
    { 
      id: 'credits_100', 
      credits: 100, 
      price: 39.99, 
      stripePriceId: 'price_100credits' 
    }
  ];
const Payments = ({ 
  user = { id: 'user_test_123' }, 
  currentSubscription = null,
  currentCredits = 0,
  onSubscriptionChange = () => {},
  onCreditPurchase = () => {},
  subscriptionPlans = DEFAULT_SUBSCRIPTION_PLANS,
  creditPackages = DEFAULT_CREDIT_PACKAGES
}) => {
  const [selectedSubscription, setSelectedSubscription] = useState(null);
  const [selectedCreditPackage, setSelectedCreditPackage] = useState(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const canvasRef = useRef(null);
  const animationFrameRef = useRef(null);
  const navigate = useNavigate();

  // Stripe checkout and account connection methods (unchanged)
  const handleStripeCheckout = async (type, item) => {
    try {
      const checkoutResponse = await fetch('/api/create-checkout-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type,
          itemId: item.id,
          userId: user.id,
          stripePriceId: item.stripePriceId
        })
      });

      const { sessionUrl } = await checkoutResponse.json();
      
      if (sessionUrl) {
        window.location.href = sessionUrl;
      }
    } catch (error) {
      console.error('Checkout error:', error);
    }
  };

  const connectStripeAccount = async () => {
    try {
      const response = await fetch('/api/stripe/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId: user.id })
      });

      const { accountLink } = await response.json();
      
      if (accountLink) {
        window.location.href = accountLink;
      }
    } catch (error) {
      console.error('Stripe Connect Error:', error);
    }
  };

  // Particle and Canvas Animation Setup (similar to login page)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    // Particle class (same as login page)
    class Particle {
      constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 3 + 1;
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
          this.size = Math.random() * 3 + 1;
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
    
    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Update and draw particles
      particleArray.forEach(particle => {
        particle.update();
        particle.draw();
      });
      
      animationFrameRef.current = requestAnimationFrame(animate);
    };
    
    animate();
    
    // Handle resize
    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    
    window.addEventListener('resize', handleResize);
    
    // Mouse movement tracking
    const handleMouseMove = (event) => {
      setMousePosition({
        x: event.clientX,
        y: event.clientY
      });
    };
    
    window.addEventListener('mousemove', handleMouseMove);
    
    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  // Plan icon selector (unchanged)
  const getPlanIcon = (planName) => {
    const iconClasses = "w-8 h-8";
    switch(planName) {
      case 'Basic': return <Users className={`${iconClasses} text-blue-500`} />;
      case 'Premium': return <Trophy className={`${iconClasses} text-purple-500`} />;
      case 'Unlimited': return <Zap className={`${iconClasses} text-green-500`} />;
      default: return <CreditCard className={`${iconClasses} text-gray-500`} />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden bg-gradient-to-br from-[#2e0068] to-[#10002b]">
      {/* Animated Canvas Background */}
      <canvas ref={canvasRef} className="absolute inset-0 z-0 pointer-events-none"></canvas>
      
      {/* Mouse Follow Light */}
      <div 
        className="mouse-follow-light" 
        style={{
          left: `${mousePosition.x}px`,
          top: `${mousePosition.y}px`
        }}
      ></div>

      {/* Decorative Elements */}
      <div className="absolute top-10 left-10 z-10">
        <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-500 to-indigo-500 animate-pulse">
          ClutchIt Vault
        </h1>
      </div>

      <div className="relative z-10 w-full max-w-6xl p-6">
        {/* User Status */}
        <div className="bg-black/30 backdrop-blur-lg rounded-xl shadow-2xl p-6 mb-8 text-center">
          <h2 className="text-xl font-semibold text-white">Your Current Plan</h2>
          <div className="mt-4 text-gray-300">
            <p>Current Subscription: {currentSubscription?.name || 'No Active Subscription'}</p>
            <p>Available Credits: {currentCredits || 0}</p>
          </div>
        </div>

        {/* Subscription Plans */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-6 text-white text-center">Subscription Plans</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {subscriptionPlans.map((plan) => (
              <div 
                key={plan.id} 
                className={`bg-black/30 backdrop-blur-lg rounded-xl shadow-2xl p-6 hover:shadow-xl transition-all ${
                  currentSubscription?.id === plan.id ? 'border-2 border-green-500' : ''
                }`}
              >
                <div className="flex items-center mb-4">
                  {getPlanIcon(plan.name)}
                  <h3 className="ml-4 text-xl font-semibold text-white">{plan.name}</h3>
                </div>
                <p className="text-3xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-purple-500 to-indigo-500">${plan.price}/month</p>
                <div className="mb-4 text-gray-300">
                  <p className="font-medium">Total Monthly Credits: {plan.totalCredits}</p>
                  <p className="text-sm text-gray-400">
                    AI Prediction Credits: {plan.aiPredictionCredits}
                  </p>
                  <p className="text-sm text-gray-400">
                    Bet Upload Credits: {plan.betUploadCredits}
                  </p>
                </div>
                <ul className="mb-6 space-y-2">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center text-gray-300">
                      <CreditCard className="w-4 h-4 mr-2 text-green-500" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <button 
                  onClick={() => handleStripeCheckout('subscription', plan)}
                  disabled={currentSubscription?.id === plan.id}
                  className={`w-full py-2 rounded-lg transition-all bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white ${
                    currentSubscription?.id === plan.id
                      ? 'opacity-50 cursor-not-allowed'
                      : 'hover:scale-105'
                  }`}
                >
                  {currentSubscription?.id === plan.id ? 'Current Plan' : `Choose ${plan.name} Plan`}
                </button>
              </div>
            ))}
          </div>
          <p className="text-center text-sm text-gray-400 mt-4">
            Credits expire at the end of the billing cycle. Track remaining credits in your dashboard.
          </p>
        </section>

        {/* Buy Credits Section */}
        <section>
          <h2 className="text-2xl font-semibold mb-6 text-white text-center">Buy AI Prediction Credits</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {creditPackages.map((pkg) => (
              <div 
                key={pkg.id} 
                className="bg-black/30 backdrop-blur-lg rounded-xl shadow-2xl p-6 hover:shadow-xl transition-all"
              >
                <div className="flex items-center justify-center mb-4">
                  <Zap className="w-10 h-10 text-yellow-500" />
                  <span className="ml-4 text-2xl font-bold text-white">{pkg.credits} Credits</span>
                </div>
                <p className="text-center text-3xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-purple-500 to-indigo-500">${pkg.price}</p>
                <button 
                  onClick={() => handleStripeCheckout('credits', pkg)}
                  className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white py-2 rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all hover:scale-105"
                >
                  Purchase Credits
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* Seller Payout Section */}
        <section className="mt-12 bg-black/30 backdrop-blur-lg rounded-xl shadow-2xl p-8">
          <h2 className="text-2xl font-semibold mb-4 text-white">Seller Payouts</h2>
          <div className="flex items-center">
            <div className="w-full">
              <p className="mb-4 text-gray-300">
                As a Vault Marketplace seller, you'll receive <strong className="text-green-400">90% of each sale</strong>, 
                with <strong className="text-red-400">10% platform fee</strong> retained.
              </p>
              <button 
                onClick={connectStripeAccount}
                className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-2 px-6 rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all hover:scale-105"
              >
                Connect Stripe Account
              </button>
            </div>
          </div>
        </section>
      </div>

      {/* Background Decoration */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl"></div>
      </div>

      {/* Mouse Follow Light Style */}
      <style jsx>{`
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
      `}</style>
    </div>
  );
};

export default Payments;