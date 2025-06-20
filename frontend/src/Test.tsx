import React, { useState } from 'react';

const Test: React.FC = () => {
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSendDate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    const today = new Date().toISOString().split('T')[0];
    try {
      const response = await fetch('/api/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ date: today }),
      });
      let data;
      try {
        data = await response.json();
      } catch {
        throw new Error('Response is not valid JSON');
      }
      if (!response.ok) throw new Error(data.error || 'Unknown error');
      setResult(JSON.stringify(data));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Test Page</h2>
      <button onClick={handleSendDate} disabled={loading}>
        {loading ? 'Sending...' : 'Send Today\'s Date to API'}
      </button>
      {result && (
        <div>
          <h3>Result:</h3>
          <pre>{result}</pre>
        </div>
      )}
      {error && <div style={{ color: 'red' }}>{error}</div>}
    </div>
  );
};

export default Test; 