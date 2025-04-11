import React, { useState, useCallback } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';

// Icons (assuming you're using a library like react-icons)
import { FaUpload, FaFileImage, FaFileAlt, FaCheck, FaExclamationTriangle } from 'react-icons/fa';

const BetUploadPage = () => {
  const navigate = useNavigate();
  
  // Form state
  const [uploadType, setUploadType] = useState('image'); // 'image' or 'text'
  const [text, setText] = useState('');
  const [redditUsername, setRedditUsername] = useState('');
  const [subscriptionUsername, setSubscriptionUsername] = useState('');
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [extractedData, setExtractedData] = useState(null);
  const [integrityScore, setIntegrityScore] = useState(null);
  const [betId, setBetId] = useState(null);
  const [step, setStep] = useState(1); // 1: Upload, 2: Review, 3: Success
  
  // For image uploads
  const [previewImage, setPreviewImage] = useState(null);
  
  // File upload handling with dropzone
  const onDrop = useCallback(acceptedFiles => {
    // Reset states
    setError('');
    setExtractedData(null);
    
    const file = acceptedFiles[0];
    if (file) {
      // Validate file type
      const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
      if (!validTypes.includes(file.type)) {
        setError('Please upload a valid image file (JPEG or PNG)');
        return;
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('File size should be less than 5MB');
        return;
      }
      
      // Create preview
      const reader = new FileReader();
      reader.onload = () => {
        setPreviewImage(reader.result);
      };
      reader.readAsDataURL(file);
      
      // Store file for upload
      setFile(file);
    }
  }, []);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png']
    },
    maxFiles: 1
  });
  
  const [file, setFile] = useState(null);
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      let response;
      
      if (uploadType === 'image') {
        if (!file) {
          setError('Please select an image to upload');
          setLoading(false);
          return;
        }
        
        // Create form data for file upload
        const formData = new FormData();
        formData.append('image', file);
        
        if (redditUsername) {
          formData.append('reddit_username', redditUsername);
        }
        
        if (subscriptionUsername) {
          formData.append('subscription_username', subscriptionUsername);
        }
        
        // Send request to upload endpoint
        response = await axios.post('/api/bets/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      } else {
        // Text upload
        if (!text.trim()) {
          setError('Please enter the bet details');
          setLoading(false);
          return;
        }
        
        // Send request to upload endpoint with text
        response = await axios.post('/api/bets/upload', {
          text: text,
          reddit_username: redditUsername || undefined,
          subscription_username: subscriptionUsername || undefined
        });
      }
      
      // Handle successful response
      if (response.data.success) {
        setExtractedData(response.data.bet_data);
        setIntegrityScore(response.data.integrity_score);
        setBetId(response.data.bet_id);
        setSuccess(true);
        setStep(2); // Move to review step
      }
      
    } catch (err) {
      console.error('Error uploading bet:', err);
      setError(err.response?.data?.error || 'Failed to upload bet. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // Handle confirming the extracted data and proceeding
  const handleConfirmBet = async () => {
    setLoading(true);
    
    try {
      // Update bet with any corrected information
      await axios.patch(`/api/bets/${betId}/update-category`, {
        bet_type: extractedData.bet_type,
        sport: extractedData.sport
      });
      
      setStep(3); // Move to success step
    } catch (err) {
      setError('Failed to confirm bet. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // Handle viewing all bets
  const handleViewMyBets = () => {
    navigate('/my-bets');
  };
  
  // Update bet data when user makes corrections
  const handleDataUpdate = (field, value) => {
    setExtractedData(prev => ({
      ...prev,
      [field]: value
    }));
  };
  
  // Render dropzone for image upload
  const renderDropzone = () => (
    <div className="mb-6">
      <div 
        {...getRootProps()} 
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors
                    ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}`}
      >
        <input {...getInputProps()} />
        {previewImage ? (
          <div className="flex flex-col items-center">
            <img src={previewImage} alt="Preview" className="max-h-64 mb-4 rounded" />
            <p className="text-sm text-gray-500">Click or drag to change image</p>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <FaFileImage className="text-4xl mb-2 text-gray-400" />
            <p className="text-gray-500 mb-1">
              {isDragActive ? 'Drop the file here' : 'Drag & drop your bet slip image, or click to select'}
            </p>
            <p className="text-xs text-gray-400">JPG, PNG up to 5MB</p>
          </div>
        )}
      </div>
    </div>
  );
  
  // Render text input area
  const renderTextInput = () => (
    <div className="mb-6">
      <label htmlFor="bet-text" className="block text-sm font-medium text-gray-700 mb-1">
        Bet Details
      </label>
      <textarea
        id="bet-text"
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="Enter your bet details (e.g., Lakers -5.5 vs Knicks, -110, $50)"
        className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 min-h-32"
        disabled={loading}
      />
    </div>
  );
  
  // Render the upload form (step 1)
  const renderUploadForm = () => (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Upload Betting Content</h2>
      
      <div className="mb-4">
        <div className="flex border border-gray-300 rounded-md overflow-hidden">
          <button
            type="button"
            className={`flex-1 py-2 px-4 focus:outline-none ${
              uploadType === 'image' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-700'
            }`}
            onClick={() => setUploadType('image')}
          >
            <FaFileImage className="inline mr-2" /> Image Upload
          </button>
          <button
            type="button"
            className={`flex-1 py-2 px-4 focus:outline-none ${
              uploadType === 'text' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-700'
            }`}
            onClick={() => setUploadType('text')}
          >
            <FaFileAlt className="inline mr-2" /> Text Upload
          </button>
        </div>
      </div>
      
      <form onSubmit={handleSubmit}>
        {uploadType === 'image' ? renderDropzone() : renderTextInput()}
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label htmlFor="reddit-username" className="block text-sm font-medium text-gray-700 mb-1">
              Reddit Username (Optional)
            </label>
            <input
              type="text"
              id="reddit-username"
              value={redditUsername}
              onChange={e => setRedditUsername(e.target.value)}
              placeholder="Your Reddit username"
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              disabled={loading}
            />
          </div>
          
          <div>
            <label htmlFor="subscription-username" className="block text-sm font-medium text-gray-700 mb-1">
              Subscription Username (Optional)
            </label>
            <input
              type="text"
              id="subscription-username"
              value={subscriptionUsername}
              onChange={e => setSubscriptionUsername(e.target.value)}
              placeholder="Your subscription username"
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              disabled={loading}
            />
          </div>
        </div>
        
        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md flex items-center">
            <FaExclamationTriangle className="mr-2" /> {error}
          </div>
        )}
        
        <button
          type="submit"
          className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-md transition-colors flex items-center justify-center"
          disabled={loading}
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </>
          ) : (
            <>
              <FaUpload className="mr-2" /> Upload Bet
            </>
          )}
        </button>
      </form>
    </div>
  );
  
  // Render the review screen (step 2)
  const renderReviewScreen = () => {
    const sportOptions = [
      'Basketball', 'Football', 'Baseball', 'Soccer', 'Hockey', 'Golf', 'Tennis', 
      'MMA/UFC', 'Boxing', 'Cricket', 'Rugby', 'Auto Racing', 'eSports', 'Other'
    ];
    
    const betTypeOptions = [
      'Moneyline', 'Spread', 'Over/Under', 'Parlay', 'Prop', 'Futures',
      'Teaser', 'Pleaser', 'Round Robin', 'If Bet', 'Reverse', 'Lotto'
    ];
    
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Review Betting Details</h2>
        
        {integrityScore !== null && (
          <div className={`mb-4 p-3 rounded-md ${
            integrityScore > 80 ? 'bg-green-50 text-green-700' :
            integrityScore > 50 ? 'bg-yellow-50 text-yellow-700' :
            'bg-red-50 text-red-700'
          }`}>
            <div className="flex items-center justify-between">
              <span className="font-medium">Extraction Confidence:</span>
              <span className="font-bold">{integrityScore}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                className={`h-2 rounded-full ${
                  integrityScore > 80 ? 'bg-green-500' :
                  integrityScore > 50 ? 'bg-yellow-500' :
                  'bg-red-500'
                }`} 
                style={{ width: `${integrityScore}%` }}
              ></div>
            </div>
          </div>
        )}
        
        <div className="space-y-4 mb-6">
          {previewImage && uploadType === 'image' && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Uploaded Image
              </label>
              <img src={previewImage} alt="Bet slip" className="max-h-48 rounded border" />
            </div>
          )}
          
          <div>
            <label htmlFor="bet-type" className="block text-sm font-medium text-gray-700 mb-1">
              Bet Type
            </label>
            <select
              id="bet-type"
              value={extractedData?.bet_type || ''}
              onChange={e => handleDataUpdate('bet_type', e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select bet type</option>
              {betTypeOptions.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label htmlFor="sport" className="block text-sm font-medium text-gray-700 mb-1">
              Sport
            </label>
            <select
              id="sport"
              value={extractedData?.sport || ''}
              onChange={e => handleDataUpdate('sport', e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select sport</option>
              {sportOptions.map(sport => (
                <option key={sport} value={sport}>{sport}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Teams/Selection
            </label>
            <div className="p-2 border border-gray-300 rounded-md bg-gray-50">
              {extractedData?.teams && extractedData.teams.length > 0 ? (
                <ul className="list-disc list-inside">
                  {extractedData.teams.map((team, index) => (
                    <li key={index} className="text-gray-800">{team}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 italic">No teams detected</p>
              )}
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Odds
            </label>
            <div className="p-2 border border-gray-300 rounded-md bg-gray-50">
              {extractedData?.odds && extractedData.odds.length > 0 ? (
                <ul className="list-disc list-inside">
                  {extractedData.odds.map((odd, index) => (
                    <li key={index} className="text-gray-800">{odd}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 italic">No odds detected</p>
              )}
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Amount
            </label>
            <div className="p-2 border border-gray-300 rounded-md bg-gray-50">
              {extractedData?.amount ? (
                <span className="text-gray-800">{extractedData.amount}</span>
              ) : (
                <p className="text-gray-500 italic">No amount detected</p>
              )}
            </div>
          </div>
        </div>
        
        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md flex items-center">
            <FaExclamationTriangle className="mr-2" /> {error}
          </div>
        )}
        
        <div className="flex space-x-3">
          <button
            type="button"
            onClick={() => setStep(1)}
            className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium py-2 px-4 rounded-md transition-colors"
            disabled={loading}
          >
            Back
          </button>
          <button
            type="button"
            onClick={handleConfirmBet}
            className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-md transition-colors flex items-center justify-center"
            disabled={loading}
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Saving...
              </>
            ) : (
              <>
                <FaCheck className="mr-2" /> Confirm Bet
              </>
            )}
          </button>
        </div>
      </div>
    );
  };
  
  // Render success screen (step 3)
  const renderSuccessScreen = () => (
    <div className="bg-white p-6 rounded-lg shadow-md text-center">
      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <FaCheck className="text-green-500 text-2xl" />
      </div>
      <h2 className="text-xl font-semibold mb-2">Bet Successfully Saved!</h2>
      <p className="text-gray-600 mb-6">
        Your bet has been processed and saved to your account.
      </p>
      
      <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3">
        <button
          type="button"
          onClick={() => {
            // Reset all states and go back to step 1
            setFile(null);
            setPreviewImage(null);
            setText('');
            setRedditUsername('');
            setSubscriptionUsername('');
            setExtractedData(null);
            setIntegrityScore(null);
            setBetId(null);
            setStep(1);
          }}
          className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-md transition-colors"
        >
          Upload Another Bet
        </button>
        <button
          type="button"
          onClick={handleViewMyBets}
          className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium py-2 px-4 rounded-md transition-colors"
        >
          View My Bets
        </button>
      </div>
    </div>
  );
  
  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      {step === 1 && renderUploadForm()}
      {step === 2 && renderReviewScreen()}
      {step === 3 && renderSuccessScreen()}
    </div>
  );
};

export default BetUploadPage;