import React, { useState } from 'react'
import axios from 'axios'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts'

const card = {
  background: 'rgba(26,31,46,0.8)',
  border: '1px solid #2d3748',
  borderRadius: '12px',
  padding: '24px',
  marginBottom: '20px',
}
const label = { fontSize: '13px', color: '#a0aec0', marginBottom: '6px', fontWeight: 600 }
const input = {
  width: '100%', background: '#0f1117', border: '1px solid #2d3748',
  borderRadius: '8px', padding: '10px 14px', color: '#e2e8f0',
  fontSize: '13px', outline: 'none', fontFamily: 'monospace',
}
const btn = (color = '#2563eb') => ({
  background: `linear-gradient(90deg, ${color}, #7c3aed)`,
  color: 'white', border: 'none', borderRadius: '8px',
  padding: '10px 24px', cursor: 'pointer', fontWeight: 700,
  fontSize: '14px', marginTop: '12px',
})
const badge = (color) => ({
  display: 'inline-block', padding: '4px 12px', borderRadius: '20px',
  background: color, color: 'white', fontWeight: 700, fontSize: '13px',
})

const STRATEGY_COLORS = {
  Binary: '#e74c3c', NAF: '#e67e22', wNAF: '#3498db', VLIM: '#9b59b6'
}

const FEATURE_LABELS = {
  bit_length: 'Bit Length', hamming_weight: 'Hamming Weight',
  zero_density: 'Zero Density', longest_zero_run: 'Max Zero Run',
  avg_zero_run: 'Avg Zero Run', longest_one_run: 'Max One Run',
  trailing_zeros: 'Trailing Zeros', wnaf_weight: 'wNAF Weight',
  wnaf_zero_density: 'wNAF Zero Density', longest_wnaf_zero_run: 'Max wNAF Zero Run',
}

export default function ExponentAnalyzer() {
  const [expInput, setExpInput] = useState('')
  const [bitLen,   setBitLen]   = useState('1024')
  const [mode,     setMode]     = useState('random')
  const [result,   setResult]   = useState(null)
  const [loading,  setLoading]  = useState(false)
  const [error,    setError]    = useState('')

  const generateRandom = () => {
    // Generate a random number by picking random hex digits
    const bytes = Math.ceil(parseInt(bitLen) / 4)
    let hex = ''
    const chars = '0123456789abcdef'
    for (let i = 0; i < bytes; i++) hex += chars[Math.floor(Math.random() * 16)]
    // Ensure MSB is set
    hex = '8' + hex.slice(1)
    const bigNum = BigInt('0x' + hex)
    setExpInput(bigNum.toString())
  }

  const analyze = async () => {
    if (!expInput.trim()) { setError('Enter an exponent value.'); return }
    setError(''); setLoading(true); setResult(null)
    try {
      const { data } = await axios.post('/api/analyze', {
        exponent: parseInt(expInput), w: 3
      })
      setResult(data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  const radarData = result
    ? Object.entries(FEATURE_LABELS).map(([key, label]) => {
        const val = result.features[key] || 0
        // Normalize 0-100 for radar
        const max = key === 'bit_length' ? 4096
          : key.includes('density') ? 1
          : key.includes('weight') ? result.features.bit_length || 1
          : result.features.bit_length || 1
        return { feature: label, value: Math.min(100, (val / max) * 100), raw: val }
      })
    : []

  return (
    <div>
      <h2 style={{ fontSize: '22px', fontWeight: 700, marginBottom: '20px' }}>
        🔍 Exponent Feature Analyzer & ML Dispatcher
      </h2>

      {/* Input Card */}
      <div style={card}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 160px', gap: '16px', alignItems: 'end' }}>
          <div>
            <div style={label}>Exponent Value (integer)</div>
            <textarea
              style={{ ...input, height: '80px', resize: 'vertical', fontFamily: 'monospace', fontSize: '12px' }}
              value={expInput}
              onChange={e => setExpInput(e.target.value)}
              placeholder="Enter a large integer (or click Generate Random)…"
            />
          </div>
          <div>
            <div style={label}>Bit Length (for random)</div>
            <select
              style={input}
              value={bitLen}
              onChange={e => setBitLen(e.target.value)}
            >
              {['256','512','1024','2048','4096'].map(b => (
                <option key={b} value={b}>{b}-bit</option>
              ))}
            </select>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
          <button style={btn('#2563eb')} onClick={analyze} disabled={loading}>
            {loading ? '⏳ Analyzing…' : '🚀 Analyze & Dispatch'}
          </button>
          <button style={{ ...btn('#059669'), marginTop: 0 }} onClick={generateRandom}>
            🎲 Generate Random {bitLen}-bit
          </button>
        </div>
        {error && <div style={{ color: '#fc8181', marginTop: '10px', fontSize: '13px' }}>{error}</div>}
      </div>

      {/* Results */}
      {result && (
        <>
          {/* Strategy Decision */}
          <div style={{ ...card, borderColor: '#2d3748', background: 'rgba(37,99,235,0.08)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
              <div>
                <div style={{ fontSize: '12px', color: '#718096', marginBottom: '4px' }}>ML PREDICTED STRATEGY</div>
                <div style={badge(STRATEGY_COLORS[result.predicted_strategy] || '#4a5568')}>
                  {result.predicted_strategy}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '12px', color: '#718096', marginBottom: '4px' }}>EXPONENT SIZE</div>
                <div style={{ fontWeight: 700, fontSize: '18px', color: '#60a5fa' }}>
                  {result.exponent_bits}-bit
                </div>
              </div>
            </div>
            <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '8px', padding: '12px', fontSize: '13px', color: '#a0aec0', lineHeight: 1.6 }}>
              💡 <strong style={{ color: '#e2e8f0' }}>Rationale:</strong> {result.strategy_rationale}
            </div>
          </div>

          {/* Features Table + Radar */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            {/* Table */}
            <div style={card}>
              <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '14px', color: '#a78bfa' }}>
                📐 10-Dimensional Feature Vector
              </h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: 'left', color: '#718096', padding: '6px 0', borderBottom: '1px solid #2d3748' }}>Feature</th>
                    <th style={{ textAlign: 'right', color: '#718096', padding: '6px 0', borderBottom: '1px solid #2d3748' }}>Value</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(FEATURE_LABELS).map(([key, lbl]) => (
                    <tr key={key}>
                      <td style={{ padding: '6px 0', color: '#a0aec0', borderBottom: '1px solid #1e2535' }}>{lbl}</td>
                      <td style={{ textAlign: 'right', fontFamily: 'monospace', fontWeight: 600,
                        color: key === 'longest_one_run' ? '#fbbf24' : '#e2e8f0',
                        borderBottom: '1px solid #1e2535' }}>
                        {typeof result.features[key] === 'number'
                          ? result.features[key] % 1 !== 0
                            ? result.features[key].toFixed(4)
                            : result.features[key]
                          : '—'}
                        {key === 'longest_one_run' && ' ⭐'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div style={{ marginTop: '10px', fontSize: '11px', color: '#4a5568' }}>
                ⭐ longest_one_run: 66.4% feature importance (Decision Tree primary split)
              </div>
            </div>

            {/* Radar Chart */}
            <div style={card}>
              <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '14px', color: '#a78bfa' }}>
                📡 Feature Radar (Normalized 0–100)
              </h3>
              <ResponsiveContainer width="100%" height={320}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#2d3748" />
                  <PolarAngleAxis dataKey="feature" tick={{ fill: '#718096', fontSize: 10 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#4a5568', fontSize: 9 }} />
                  <Radar
                    dataKey="value" stroke="#7c3aed" fill="#7c3aed" fillOpacity={0.3}
                  />
                  <Tooltip
                    formatter={(val, _, props) => [
                      `${val.toFixed(1)} (raw: ${props.payload.raw})`, 'Normalized Value'
                    ]}
                    contentStyle={{ background: '#1a1f2e', border: '1px solid #2d3748', borderRadius: '8px', color: '#e2e8f0' }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
