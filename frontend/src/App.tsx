import { useState } from 'react';
import axios from 'axios';

export default function App() {
  const [txn, setTxn] = useState({ transactionId: '', customerId: '', amount: '', ipAddress: '' });
  const [result, setResult] = useState('');

  const sendTxn = async () => {
    try {
      const res = await axios.post('https://your-api-id.execute-api.us-west-2.amazonaws.com/prod/check', txn);
      setResult(res.data.outcome);
    } catch (err) {
      setResult('Error submitting transaction');
    }
  };

  return (
    <div className="p-10 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Fraud Checker</h1>
      <input className="border p-2 mb-2 w-full" placeholder="Transaction ID" onChange={e => setTxn({...txn, transactionId: e.target.value})} />
      <input className="border p-2 mb-2 w-full" placeholder="Customer ID" onChange={e => setTxn({...txn, customerId: e.target.value})} />
      <input className="border p-2 mb-2 w-full" placeholder="Amount" type="number" onChange={e => setTxn({...txn, amount: parseFloat(e.target.value)})} />
      <input className="border p-2 mb-2 w-full" placeholder="IP Address" onChange={e => setTxn({...txn, ipAddress: e.target.value})} />
      <button className="bg-blue-500 text-white p-2 rounded" onClick={sendTxn}>Submit</button>
      {result && <div className="mt-4">Result: {result}</div>}
    </div>
  );
}