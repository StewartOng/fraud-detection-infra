import { useState } from 'react';
import axios from 'axios';

export default function App() {
  const [txn, setTxn] = useState({
    transactionId: '',
    customerId: '',
    amount: '',
    ipAddress: ''
  });
  const [result, setResult] = useState<{outcome?: string, error?: string}>({});
  const [loading, setLoading] = useState(false);

  const sendTxn = async () => {
    setLoading(true);
    try {
      const res = await axios.post(
        'YOUR_API_GATEWAY_URL/check', // Replace with your actual API URL
        txn,
        { headers: { 'Content-Type': 'application/json' } }
      );
      setResult(res.data);
    } catch (err) {
      setResult({ error: 'Error submitting transaction' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-10 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Fraud Checker</h1>
      
      <div className="space-y-4">
        <div>
          <label className="block mb-1">Transaction ID</label>
          <input 
            className="border p-2 w-full rounded" 
            value={txn.transactionId}
            onChange={e => setTxn({...txn, transactionId: e.target.value})} 
          />
        </div>
        
        <div>
          <label className="block mb-1">Customer ID</label>
          <input 
            className="border p-2 w-full rounded" 
            value={txn.customerId}
            onChange={e => setTxn({...txn, customerId: e.target.value})} 
          />
        </div>
        
        <div>
          <label className="block mb-1">Amount</label>
          <input 
            className="border p-2 w-full rounded" 
            type="number" 
            value={txn.amount}
            onChange={e => setTxn({...txn, amount: e.target.value})} 
          />
        </div>
        
        <div>
          <label className="block mb-1">IP Address</label>
          <input 
            className="border p-2 w-full rounded" 
            value={txn.ipAddress}
            onChange={e => setTxn({...txn, ipAddress: e.target.value})} 
          />
        </div>
      </div>

      <button 
        className="mt-6 bg-blue-500 hover:bg-blue-600 text-white p-2 rounded w-full disabled:bg-gray-400"
        onClick={sendTxn}
        disabled={loading}
      >
        {loading ? 'Checking...' : 'Submit'}
      </button>

      {result.outcome && (
        <div className={`mt-4 p-4 rounded ${result.outcome === 'fraud' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
          Result: {result.outcome.toUpperCase()}
        </div>
      )}
      
      {result.error && (
        <div className="mt-4 p-4 bg-yellow-100 text-yellow-800 rounded">
          {result.error}
        </div>
      )}
    </div>
  );
}