import React, { useState } from 'react'
import api from '../api'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts'

const STRATEGY_BADGES = {
  Binary: { bg: '#dc2626', text: '#fee2e2' },
  NAF:    { bg: '#d97706', text: '#fef3c7' },
  wNAF:   { bg: '#2563eb', text: '#dbeafe' },
  VLIM:   { bg: '#7c3aed', text: '#ede9fe' },
}

export default function ExponentAnalyzer() {
  const [expInput, setExpInput] = useState('')
  const [bitLen, setBitLen] = useState('1024')
  const [profile, setProfile] = useState('uniform')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [genLoading, setGenLoading] = useState(false)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  // Generate random exponent via backend API (keeps exact string precision)
  const handleGenerate = async () => {
    setGenLoading(true)
    setError('')
    try {
      const res = await api.post('/api/generate-exponent', {
        bits: parseInt(bitLen, 10),
        profile: profile,
      })
      setExpInput(res.data.exponent)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate exponent.')
    } finally {
      setGenLoading(false)
    }
  }

  // Analyze the exponent using string value
  const handleAnalyze = async () => {
    const trimmed = expInput.trim()
    if (!trimmed) {
      setError('Please provide an exponent value or generate one.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const res = await api.post('/api/analyze', {
        exponent: trimmed,
        w: 3,
      })
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis request failed.')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = () => {
    if (!expInput) return
    navigator.clipboard.writeText(expInput)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Radar metrics normalization (0 - 100)
  const radarData = result ? [
    { metric: 'Hamming Weight', value: Math.min(100, (result.features.hamming_weight / (result.features.bit_length || 1)) * 100), raw: result.features.hamming_weight },
    { metric: 'Zero Density', value: (result.features.zero_density || 0) * 100, raw: `${((result.features.zero_density || 0) * 100).toFixed(1)}%` },
    { metric: 'Max 1-Run', value: Math.min(100, ((result.features.longest_one_run || 0) / 64) * 100), raw: result.features.longest_one_run },
    { metric: 'Max 0-Run', value: Math.min(100, ((result.features.longest_zero_run || 0) / 64) * 100), raw: result.features.longest_zero_run },
    { metric: 'wNAF Weight', value: Math.min(100, (result.features.wnaf_weight / (result.features.bit_length || 1)) * 100), raw: result.features.wnaf_weight },
    { metric: 'wNAF 0-Density', value: (result.features.wnaf_zero_density || 0) * 100, raw: `${((result.features.wnaf_zero_density || 0) * 100).toFixed(1)}%` },
  ] : []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Title & Description */}
      <div>
        <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#f1f5f9', margin: 0 }}>
          Exponent Morphology Analyzer
        </h1>
        <p style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
          Extracts single-pass bitwise structural features and determines optimal modular exponentiation routing.
        </p>
      </div>

      {/* Input Card */}
      <div style={{
        backgroundColor: '#0f1422',
        border: '1px solid #1e2638',
        borderRadius: '10px',
        padding: '20px',
      }}>
        {/* Controls Bar */}
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '12px',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '14px',
        }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', alignItems: 'center' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: '#94a3b8' }}>Scale:</span>
            <select
              value={bitLen}
              onChange={e => setBitLen(e.target.value)}
              style={{
                backgroundColor: '#161d2e',
                border: '1px solid #273349',
                color: '#e2e8f0',
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: '13px',
                outline: 'none',
              }}
            >
              <option value="256">256-bit</option>
              <option value="512">512-bit</option>
              <option value="1024">1024-bit (Standard RSA)</option>
              <option value="2048">2048-bit (High Security)</option>
              <option value="4096">4096-bit (Long Term)</option>
            </select>

            <span style={{ fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginLeft: '6px' }}>Topology:</span>
            <select
              value={profile}
              onChange={e => setProfile(e.target.value)}
              style={{
                backgroundColor: '#161d2e',
                border: '1px solid #273349',
                color: '#e2e8f0',
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: '13px',
                outline: 'none',
              }}
            >
              <option value="uniform">Uniform Random (NIST Default)</option>
              <option value="dense">Dense Key (&gt;85% Ones)</option>
              <option value="sparse">Sparse Key (&lt;15% Ones)</option>
              <option value="bursty">Bursty (Clustered Zero Runs)</option>
              <option value="alternating">Alternating (101010...)</option>
              <option value="ecc_random">ECC Scalar Equivalent</option>
            </select>

            <button
              onClick={handleGenerate}
              disabled={genLoading}
              style={{
                backgroundColor: '#1e293b',
                color: '#38bdf8',
                border: '1px solid #334155',
                padding: '6px 14px',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              {genLoading ? 'Generating...' : 'Generate Key'}
            </button>
          </div>

          {expInput && (
            <button
              onClick={handleCopy}
              style={{
                backgroundColor: '#161d2e',
                color: copied ? '#10b981' : '#94a3b8',
                border: '1px solid #273349',
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: '12px',
                fontWeight: 500,
                cursor: 'pointer',
              }}
            >
              {copied ? 'Copied' : 'Copy Exponent'}
            </button>
          )}
        </div>

        {/* Text Area */}
        <textarea
          value={expInput}
          onChange={e => setExpInput(e.target.value)}
          placeholder="Paste or generate an exponent integer (decimal or 0x-hex format)..."
          rows={3}
          style={{
            width: '100%',
            backgroundColor: '#090d16',
            border: '1px solid #1e2638',
            borderRadius: '6px',
            color: '#f8fafc',
            fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
            fontSize: '12px',
            padding: '12px',
            boxSizing: 'border-box',
            resize: 'vertical',
            outline: 'none',
          }}
        />

        {/* Action Button */}
        <div style={{ marginTop: '12px', display: 'flex', gap: '12px', alignItems: 'center' }}>
          <button
            onClick={handleAnalyze}
            disabled={loading}
            style={{
              backgroundColor: '#2563eb',
              color: '#ffffff',
              border: 'none',
              padding: '8px 20px',
              borderRadius: '6px',
              fontSize: '13px',
              fontWeight: 600,
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? 'Extracting Features...' : 'Analyze Exponent'}
          </button>

          {error && (
            <span style={{ fontSize: '13px', color: '#ef4444' }}>
              {error}
            </span>
          )}
        </div>
      </div>

      {/* Analysis Result Display */}
      {result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Dispatch Banner */}
          <div style={{
            backgroundColor: '#0f1422',
            border: '1px solid #1e2638',
            borderRadius: '10px',
            padding: '20px',
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: '16px',
          }}>
            <div>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', color: '#64748b', fontWeight: 600, letterSpacing: '0.5px' }}>
                Predicted Optimal Strategy
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '6px' }}>
                <span style={{
                  backgroundColor: STRATEGY_BADGES[result.predicted_strategy]?.bg || '#334155',
                  color: STRATEGY_BADGES[result.predicted_strategy]?.text || '#ffffff',
                  fontSize: '14px',
                  fontWeight: 700,
                  padding: '4px 14px',
                  borderRadius: '6px',
                  letterSpacing: '0.3px',
                }}>
                  {result.predicted_strategy}
                </span>
                <span style={{ fontSize: '14px', color: '#cbd5e1', fontWeight: 500 }}>
                  for {result.exponent_bits}-bit Key
                </span>
              </div>
            </div>

            <div style={{
              flex: 1,
              maxWidth: '700px',
              fontSize: '13px',
              color: '#94a3b8',
              lineHeight: '1.5',
              borderLeft: '2px solid #273349',
              paddingLeft: '16px',
            }}>
              <strong style={{ color: '#e2e8f0' }}>Dispatch Rationale:</strong> {result.strategy_rationale}
            </div>

            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>
                Extraction Latency
              </div>
              <div style={{ fontSize: '16px', fontWeight: 700, color: '#38bdf8', marginTop: '2px' }}>
                {result.extract_time_us} µs
              </div>
            </div>
          </div>

          {/* Metrics Grid + Radar */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '20px',
          }}>
            {/* Structural Metrics Table */}
            <div style={{
              backgroundColor: '#0f1422',
              border: '1px solid #1e2638',
              borderRadius: '10px',
              padding: '20px',
            }}>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc', marginBottom: '14px' }}>
                10-Dimensional Feature Fingerprint
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {[
                  { label: 'Bit Length', val: result.features.bit_length, highlight: false },
                  { label: 'Hamming Weight', val: `${result.features.hamming_weight} bits`, highlight: false },
                  { label: 'Zero Density', val: `${(result.features.zero_density * 100).toFixed(2)}%`, highlight: false },
                  { label: 'Longest One Run (Highest ML Signal)', val: `${result.features.longest_one_run} bits`, highlight: true },
                  { label: 'Longest Zero Run', val: `${result.features.longest_zero_run} bits`, highlight: false },
                  { label: 'Average Zero Run', val: `${result.features.avg_zero_run.toFixed(2)} bits`, highlight: false },
                  { label: 'Trailing Zeros', val: `${result.features.trailing_zeros} bits`, highlight: false },
                  { label: 'wNAF Weight (Non-Zero Digits)', val: `${result.features.wnaf_weight}`, highlight: false },
                  { label: 'wNAF Zero Density', val: `${(result.features.wnaf_zero_density * 100).toFixed(2)}%`, highlight: false },
                  { label: 'Longest wNAF Zero Run', val: `${result.features.longest_wnaf_zero_run} bits`, highlight: false },
                ].map((item, idx) => (
                  <div key={idx} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '8px 10px',
                    borderRadius: '6px',
                    backgroundColor: item.highlight ? 'rgba(37,99,235,0.1)' : idx % 2 === 0 ? '#0b0f19' : 'transparent',
                    border: item.highlight ? '1px solid rgba(56,189,248,0.3)' : 'none',
                    fontSize: '13px',
                  }}>
                    <span style={{ color: item.highlight ? '#38bdf8' : '#94a3b8', fontWeight: item.highlight ? 600 : 400 }}>
                      {item.label}
                    </span>
                    <span style={{
                      fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
                      color: item.highlight ? '#f8fafc' : '#e2e8f0',
                      fontWeight: 600,
                    }}>
                      {item.val}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Radar Chart */}
            <div style={{
              backgroundColor: '#0f1422',
              border: '1px solid #1e2638',
              borderRadius: '10px',
              padding: '20px',
              display: 'flex',
              flexDirection: 'column',
            }}>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc', marginBottom: '8px' }}>
                Morphology Radar Graph
              </div>
              <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '12px' }}>
                Normalized topology profile driving Decision Tree splits.
              </div>

              <div style={{ flex: 1, minHeight: '300px' }}>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="#273349" />
                    <PolarAngleAxis dataKey="metric" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                    <PolarRadiusAxis domain={[0, 100]} tick={{ fill: '#475569', fontSize: 10 }} />
                    <Radar dataKey="value" stroke="#38bdf8" fill="#0284c7" fillOpacity={0.25} />
                    <Tooltip
                      formatter={(val, name, entry) => [entry.payload.raw, 'Measurement']}
                      contentStyle={{ backgroundColor: '#0f1422', borderColor: '#273349', borderRadius: '6px', fontSize: '12px', color: '#f8fafc' }}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
