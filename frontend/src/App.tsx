import { useState } from 'react';
import axios from 'axios';

export default function FraudDetectionApp() {
  // State for form inputs and results
  const [inputs, setInputs] = useState({
    email: '',
    ipAddress: '',
    transactionId: '',
    customerId: '',
    amount: ''
  });
  const [activeTab, setActiveTab] = useState<'email' | 'transaction'>('email');
  const [result, setResult] = useState<{outcome?: string; error?: string}>({});
  const [isLoading, setIsLoading] = useState(false);

  const checkFraud = async () => {
    setIsLoading(true);
    setResult({});
    
    try {
      let payload = {};
      if (activeTab === 'email') {
        payload = { 
          email: inputs.email, 
          ipAddress: inputs.ipAddress 
        };
      } else {
        payload = {
          transactionId: inputs.transactionId || Date.now().toString(),
          customerId: inputs.customerId,
          amount: parseFloat(inputs.amount) || 0,
          ipAddress: inputs.ipAddress
        };
      }

      const apiUrl = import.meta.env.VITE_API_URL || 'YOUR_API_GATEWAY_URL';
      const response = await axios.post(apiUrl, payload, {
        headers: { 'Content-Type': 'application/json' }
      });

      setResult({ outcome: response.data.outcome });
    } catch (error) {
      console.error('Error checking fraud:', error);
      setResult({ 
        error: error.response?.data?.error || 'Failed to check fraud status' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h1 className="text-2xl font-bold mb-6 text-center">Fraud Detection System</h1>
      
      {/* Tab Navigation */}
      <div className="flex mb-6 border-b">
        <button
          className={`py-2 px-4 font-medium ${activeTab === 'email' 
            ? 'border-b-2 border-blue-500 text-blue-600' 
            : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => setActiveTab('email')}
        >
          Email/IP Check
        </button>
        <button
          className={`py-2 px-4 font-medium ${activeTab === 'transaction' 
            ? 'border-b-2 border-blue-500 text-blue-600' 
            : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => setActiveTab('transaction')}
        >
          Transaction Check
        </button>
      </div>

      {/* Email/IP Check Form */}
      {activeTab === 'email' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </label>
            <input
              type="email"
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              placeholder="user@example.com"
              value={inputs.email}
              onChange={(e) => setInputs({...inputs, email: e.target.value})}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              IP Address
            </label>
            <input
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              placeholder="192.168.1.1"
              value={inputs.ipAddress}
              onChange={(e) => setInputs({...inputs, ipAddress: e.target.value})}
            />
          </div>
        </div>
      )}

      {/* Transaction Check Form */}
      {activeTab === 'transaction' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Customer ID
            </label>
            <input
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              placeholder="cust-123"
              value={inputs.customerId}
              onChange={(e) => setInputs({...inputs, customerId: e.target.value})}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Transaction Amount
            </label>
            <input
              type="number"
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              placeholder="100.00"
              value={inputs.amount}
              onChange={(e) => setInputs({...inputs, amount: e.target.value})}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              IP Address
            </label>
            <input
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              placeholder="192.168.1.1"
              value={inputs.ipAddress}
              onChange={(e) => setInputs({...inputs, ipAddress: e.target.value})}
            />
          </div>
        </div>
      )}

      {/* Submit Button */}
      <button
        className={`mt-6 w-full py-2 px-4 rounded-md text-white font-medium ${
          isLoading ? 'bg-blue-400' : 'bg-blue-600 hover:bg-blue-700'
        }`}
        onClick={checkFraud}
        disabled={isLoading}
      >
        {isLoading ? 'Checking...' : 'Check for Fraud'}
      </button>

      {/* Results Display */}
      {result.outcome && (
        <div className={`mt-4 p-3 rounded-md text-center ${
          result.outcome === 'fraud' 
            ? 'bg-red-100 text-red-800' 
            : 'bg-green-100 text-green-800'
        }`}>
          <p className="font-medium">Result: {result.outcome.toUpperCase()}</p>
          {result.outcome === 'fraud' && (
            <p className="text-sm mt-1">Fraud alert has been sent to administrators</p>
          )}
        </div>
      )}

      {result.error && (
        <div className="mt-4 p-3 bg-yellow-100 text-yellow-800 rounded-md text-center">
          <p className="font-medium">Error: {result.error}</p>
        </div>
      )}
    </div>
  );
}