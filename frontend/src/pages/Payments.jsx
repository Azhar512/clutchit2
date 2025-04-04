import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { CreditCard, Zap, Users, Trophy, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import axios from 'axios';

const DEFAULT_SUBSCRIPTION_PLANS = [
  {
    id: 'basic',
    name: 'Basic',
    price: 10,
    totalCredits: 600,
    aiPredictionCredits: 300,
    betUploadCredits: 300,
    features: [
      'Limited AI picks & bet uploads',
      'Basic Vault Access'
    ],
    stripePriceId: 'price_basic_id'
  },
  {
    id: 'premium',
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
    stripePriceId: 'price_premium_id'
  },
  {
    id: 'unlimited',
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
    stripePriceId: 'price_unlimited_id'
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
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState({ show: false, message: '', type: '' });
  const [userSubscription, setUserSubscription] = useState(currentSubscription);
  const [expandedSection, setExpandedSection] = useState('subscription'); // 'subscription' or 'credits'
  const navigate = useNavigate();

  // Fetch current subscription on component mount
  useEffect(() => {
    const fetchSubscription = async () => {
      try {
        const token = localStorage.getItem('token'); // Assuming JWT stored in localStorage
        if (!token) return;

        const response = await axios.get('/subscription/', {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.data) {
          setUserSubscription(response.data);
          onSubscriptionChange(response.data);
        }
      } catch (error) {
        // 404 is expected if user has no subscription
        if (error.response && error.response.status !== 404) {
          showNotification('Failed to fetch subscription information', 'error');
        }
      }
    };

    fetchSubscription();
  }, []);

  const showNotification = (message, type = 'success') => {
    setNotification({ show: true, message, type });
    setTimeout(() => {
      setNotification({ show: false, message: '', type: '' });
    }, 5000);
  };

  // Create subscription
  const createSubscription = async (subscriptionType) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('/subscription/create', 
        { subscription_type: subscriptionType },
        { headers: { Authorization: `Bearer ${token}` }}
      );

      if (response.data && response.data.subscription) {
        setUserSubscription(response.data.subscription);
        onSubscriptionChange(response.data.subscription);
        showNotification('Subscription created successfully!');
      }
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Failed to create subscription';
      showNotification(errorMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Upgrade subscription
  const upgradeSubscription = async (subscriptionType) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('/subscription/upgrade', 
        { subscription_type: subscriptionType },
        { headers: { Authorization: `Bearer ${token}` }}
      );

      if (response.data && response.data.subscription) {
        setUserSubscription(response.data.subscription);
        onSubscriptionChange(response.data.subscription);
        showNotification('Subscription upgraded successfully!');
      }
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Failed to upgrade subscription';
      showNotification(errorMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Cancel subscription
  const cancelSubscription = async () => {
    if (!window.confirm('Are you sure you want to cancel your subscription?')) return;
    
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('/subscription/cancel', 
        {},
        { headers: { Authorization: `Bearer ${token}` }}
      );

      if (response.data) {
        setUserSubscription(null);
        onSubscriptionChange(null);
        showNotification('Subscription cancelled successfully');
      }
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Failed to cancel subscription';
      showNotification(errorMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Create Stripe Checkout session
  const createCheckoutSession = async (subscriptionType) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('/subscription/checkout-session', 
        { subscription_type: subscriptionType },
        { headers: { Authorization: `Bearer ${token}` }}
      );

      if (response.data && response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Failed to create checkout session';
      showNotification(errorMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Credit package checkout
  const handleCreditPackageCheckout = async (creditPackage) => {
    // This would need to be implemented on your backend
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('/credits/checkout-session', 
        { 
          package_id: creditPackage.id,
          amount: creditPackage.credits,
          price: creditPackage.price
        },
        { headers: { Authorization: `Bearer ${token}` }}
      );

      if (response.data && response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
    } catch (error) {
      showNotification('Failed to process credit purchase', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Handle subscription selection
  const handleSubscriptionSelect = (plan) => {
    setSelectedSubscription(plan);
    
    if (!userSubscription) {
      // Create new subscription
      createCheckoutSession(plan.id);
    } else if (plan.id !== userSubscription.subscription_type.toLowerCase()) {
      // Upgrade subscription
      upgradeSubscription(plan.id);
    } else {
      showNotification('You already have this subscription', 'info');
    }
  };

  // Handle credit package selection
  const handleCreditPackageSelect = (creditPackage) => {
    setSelectedCreditPackage(creditPackage);
    handleCreditPackageCheckout(creditPackage);
  };

  // Connect Stripe account for sellers
  const connectStripeAccount = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('/stripe/connect-account', 
        { userId: user.id },
        { headers: { Authorization: `Bearer ${token}` }}
      );

      if (response.data && response.data.onboarding_url) {
        window.location.href = response.data.onboarding_url;
      }
    } catch (error) {
      showNotification('Failed to connect Stripe account', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-4">
      {/* Notification */}
      {notification.show && (
        <div className={`fixed top-4 right-4 p-4 rounded-md shadow-lg flex items-center ${
          notification.type === 'error' ? 'bg-red-100 border-red-400' : 
          notification.type === 'info' ? 'bg-blue-100 border-blue-400' : 
          'bg-green-100 border-green-400'
        }`}>
          {notification.type === 'error' ? 
            <AlertCircle className="mr-2 h-5 w-5 text-red-500" /> : 
            <CheckCircle className="mr-2 h-5 w-5 text-green-500" />
          }
          <span>{notification.message}</span>
        </div>
      )}

      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Payment & Subscription</h1>
        <p className="text-gray-600">Manage your subscription and credits</p>
      </div>

      {/* Current Subscription Status */}
      {userSubscription && (
        <div className="mb-6 p-4 border rounded-lg bg-blue-50">
          <h2 className="text-xl font-semibold mb-2">Current Subscription</h2>
          <div className="flex flex-wrap items-center justify-between">
            <div>
              <p>Plan: <span className="font-semibold">{userSubscription.subscription_type}</span></p>
              <p>Status: <span className={`font-semibold ${userSubscription.is_active ? 'text-green-600' : 'text-red-600'}`}>
                {userSubscription.is_active ? 'Active' : 'Inactive'}
              </span></p>
              {userSubscription.is_trial && <p className="text-purple-600 font-medium">Trial Period</p>}
            </div>
            <div className="mt-2 md:mt-0">
              <p>Credits: <span className="font-semibold">{userSubscription.credits}</span></p>
              <p>Expires: <span className="font-semibold">
                {new Date(userSubscription.end_date).toLocaleDateString()}
              </span></p>
            </div>
            <button 
              onClick={cancelSubscription}
              className="mt-2 md:mt-0 px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
              disabled={loading}
            >
              {loading ? <Loader className="h-4 w-4 animate-spin" /> : 'Cancel Subscription'}
            </button>
          </div>
        </div>
      )}

      {/* Section Tabs */}
      <div className="flex mb-6 border-b">
        <button 
          onClick={() => setExpandedSection('subscription')}
          className={`py-2 px-4 ${expandedSection === 'subscription' ? 'border-b-2 border-blue-500 font-medium' : 'text-gray-500'}`}
        >
          Subscription Plans
        </button>
        <button 
          onClick={() => setExpandedSection('credits')}
          className={`py-2 px-4 ${expandedSection === 'credits' ? 'border-b-2 border-blue-500 font-medium' : 'text-gray-500'}`}
        >
          Buy Credits
        </button>
      </div>

      {/* Subscription Plans */}
      {expandedSection === 'subscription' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {subscriptionPlans.map((plan) => (
            <div 
              key={plan.id}
              className={`border rounded-lg p-6 transition-all ${
                userSubscription && userSubscription.subscription_type.toLowerCase() === plan.id 
                  ? 'border-green-500 bg-green-50' 
                  : 'hover:shadow-md'
              }`}
            >
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold">{plan.name}</h3>
                {userSubscription && userSubscription.subscription_type.toLowerCase() === plan.id && (
                  <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">Current</span>
                )}
              </div>
              <p className="text-2xl font-bold mb-4">{formatCurrency(plan.price)}<span className="text-sm text-gray-500">/month</span></p>
              
              <div className="mb-4">
                <div className="flex items-center mb-2">
                  <Zap className="h-5 w-5 text-yellow-500 mr-2" />
                  <p>{typeof plan.totalCredits === 'string' ? plan.totalCredits : plan.totalCredits.toLocaleString()} Total Credits</p>
                </div>
                <div className="flex items-center mb-2">
                  <Trophy className="h-5 w-5 text-purple-500 mr-2" />
                  <p>{typeof plan.aiPredictionCredits === 'string' ? plan.aiPredictionCredits : plan.aiPredictionCredits.toLocaleString()} AI Prediction Credits</p>
                </div>
                <div className="flex items-center">
                  <Users className="h-5 w-5 text-blue-500 mr-2" />
                  <p>{typeof plan.betUploadCredits === 'string' ? plan.betUploadCredits : plan.betUploadCredits.toLocaleString()} Bet Upload Credits</p>
                </div>
              </div>
              
              <ul className="mb-6 text-sm">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-center mb-1">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                    {feature}
                  </li>
                ))}
              </ul>
              
              <button
                onClick={() => handleSubscriptionSelect(plan)}
                disabled={loading || (userSubscription && userSubscription.subscription_type.toLowerCase() === plan.id)}
                className={`w-full py-2 px-4 rounded-md transition-colors ${
                  userSubscription && userSubscription.subscription_type.toLowerCase() === plan.id
                    ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                {loading ? 
                  <Loader className="h-5 w-5 animate-spin mx-auto" /> : 
                  userSubscription && userSubscription.subscription_type.toLowerCase() === plan.id ? 
                    'Current Plan' : 
                    userSubscription ? 'Upgrade Plan' : 'Subscribe'
                }
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Credit Packages */}
      {expandedSection === 'credits' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {creditPackages.map((pkg) => (
            <div 
              key={pkg.id}
              className="border rounded-lg p-6 hover:shadow-md transition-all"
            >
              <h3 className="text-xl font-bold mb-2">{pkg.credits} Credits</h3>
              <p className="text-2xl font-bold mb-4">{formatCurrency(pkg.price)}</p>
              <p className="text-sm text-gray-500 mb-6">
                ${(pkg.price / pkg.credits).toFixed(2)} per credit
              </p>
              <button
                onClick={() => handleCreditPackageSelect(pkg)}
                disabled={loading}
                className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
              >
                {loading ? <Loader className="h-5 w-5 animate-spin mx-auto" /> : 'Buy Now'}
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Seller Account Link Section */}
      <div className="mt-12 border-t pt-6">
        <h2 className="text-xl font-bold mb-4">Become a Seller</h2>
        <p className="mb-4">Want to sell your own sports predictions? Connect your Stripe account to get started.</p>
        <button
          onClick={connectStripeAccount}
          disabled={loading}
          className="py-2 px-6 bg-purple-600 hover:bg-purple-700 text-white rounded-md transition-colors flex items-center"
        >
          {loading ? <Loader className="h-5 w-5 animate-spin mr-2" /> : <CreditCard className="h-5 w-5 mr-2" />}
          Connect Stripe Account
        </button>
      </div>
    </div>
  );
};

export default Payments;