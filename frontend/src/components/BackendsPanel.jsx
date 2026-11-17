import React, { useState, useEffect } from 'react'
import axios from 'axios'

const BACKEND_THEMES = {
  python_bigint: { color: '#38bdf8', badge: 'Software' },
  c_montgomery:  { color: '#34d399', badge: 'C Native' },
  fpga_radix4:   { color: '#a78bfa', badge: 'FPGA RTL' },
  asic_csa52:    { color: '#f43f5e', badge: 'ASIC Silicon' },
}

export default function BackendsPanel() {
  const [backends, setBackends] = useState([])
  const [selectedBackend, setSelectedBackend] = useState('python_bigint')
  const [expInput, setExpInput] = useState('')
  const [dispatchResult, setDispatchResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [genLoading, setGenLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    axios.get('/api/backends')
      .then(res => setBackends(res.data.backends))
      .catch(() => {})
  }, [])

  const handleGenerate = async (bits = 1024) => {
    setGenLoading(true)
    setError('')
    try {
      const res = await axios.post('/api/generate-exponent', {
        bits: bits,
        profile: 'bursty',
      })
      setExpInput(res.data.exponent)
    } catch (err) {
      setError('Failed to generate exponent.')
    } finally {
      setGenLoading(false)
    }
  }

  const handleDispatch = async () => {
    const trimmed = expInput.trim()
    if (!trimmed) {
      setError('Please provide an exponent value or click Generate Exponent.')
      return
    }
    setLoading(true)
    setError('')
    setDispatchResult(null)
    try {
      const res = await axios.post('/api/backends/dispatch', {
        exponent: trimmed,
        backend: selectedBackend,
      })
      setDispatchResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Dispatch failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Title */}
      <div>
        <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#f1f5f9', margin: 0 }}>
          Cross-Architecture Target Profiling
        </h1>
        <p style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
          Demonstrates how target silicon characteristics (C_sqr, C_mult, C_ctrl) cause optimal algorithm crossover boundaries to shift, justifying machine learning routing over static heuristics.
        </p>
      </div>

      {/* Target Backend Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '16px',
      }}>
        {backends.map(b => {
          const isSelected = selectedBackend === b.name
          const theme = BACKEND_THEMES[b.name] || { color: '#38bdf8', badge: 'Target' }
          return (
            <div
              key={b.name}
              onClick={() => setSelectedBackend(b.name)}
              style={{
                backgroundColor: '#0f1422',
                border: `1px solid ${isSelected ? theme.color : '#1e2638'}`,
                borderRadius: '10px',
                padding: '18px',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                position: 'relative',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc' }}>
                  {b.name}
                </span>
                <span style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  backgroundColor: 'rgba(255,255,255,0.06)',
                  color: theme.color,
                  padding: '2px 8px',
                  borderRadius: '4px',
                }}>
                  {theme.badge}
                </span>
              </div>

              <div style={{ fontSize: '12px', color: '#64748b', lineHeight: '1.4', marginBottom: '12px', minHeight: '34px' }}>
                {b.description}
              </div>

              <div style={{
                display: 'flex',
                gap: '12px',
                paddingTop: '10px',
                borderTop: '1px solid #1a2234',
                fontSize: '12px',
              }}>
                <div><span style={{ color: '#64748b' }}>C_sqr:</span> <span style={{ color: '#f8fafc', fontWeight: 600 }}>{b.cost_sqr}</span></div>
                <div><span style={{ color: '#64748b' }}>C_mult:</span> <span style={{ color: theme.color, fontWeight: 700 }}>{b.cost_mult}x</span></div>
                <div><span style={{ color: '#64748b' }}>C_ctrl:</span> <span style={{ color: '#94a3b8', fontWeight: 600 }}>{b.cost_ctrl}</span></div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Dispatch Tester Card */}
      <div style={{
        backgroundColor: '#0f1422',
        border: '1px solid #1e2638',
        borderRadius: '10px',
        padding: '20px',
      }}>
        <div style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc', marginBottom: '12px' }}>
          Evaluate Dispatch for Target Silicon
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <label style={{ fontSize: '12px', fontWeight: 600, color: '#94a3b8' }}>
            Exponent Input
          </label>
          <button
            onClick={() => handleGenerate(1024)}
            disabled={genLoading}
            style={{
              backgroundColor: 'transparent',
              border: '1px solid #273349',
              color: '#38bdf8',
              borderRadius: '4px',
              padding: '4px 10px',
              fontSize: '12px',
              cursor: 'pointer',
            }}
          >
            {genLoading ? 'Generating...' : 'Generate 1024-bit Bursty Key'}
          </button>
        </div>

        <textarea
          value={expInput}
          onChange={e => setExpInput(e.target.value)}
          placeholder="Paste or generate an exponent integer..."
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

        <div style={{ marginTop: '12px', display: 'flex', gap: '12px', alignItems: 'center' }}>
          <button
            onClick={handleDispatch}
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
            {loading ? 'Dispatching...' : `Dispatch for ${selectedBackend}`}
          </button>

          {error && (
            <span style={{ fontSize: '13px', color: '#ef4444' }}>
              {error}
            </span>
          )}
        </div>

        {/* Dispatch Result Display */}
        {dispatchResult && (
          <div style={{
            marginTop: '16px',
            backgroundColor: '#070a10',
            border: '1px solid #1e293b',
            borderRadius: '8px',
            padding: '16px',
            display: 'flex',
            flexWrap: 'wrap',
            gap: '24px',
            alignItems: 'center',
          }}>
            <div>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', color: '#64748b', fontWeight: 600 }}>
                Target Architecture
              </div>
              <div style={{ fontSize: '15px', fontWeight: 700, color: '#f8fafc', marginTop: '2px' }}>
                {dispatchResult.backend}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', color: '#64748b', fontWeight: 600 }}>
                Selected Strategy
              </div>
              <div style={{ fontSize: '15px', fontWeight: 700, color: '#10b981', marginTop: '2px' }}>
                {dispatchResult.predicted_strategy}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', color: '#64748b', fontWeight: 600 }}>
                Hardware Cost Ratios
              </div>
              <div style={{ fontSize: '12px', fontFamily: 'monospace', color: '#94a3b8', marginTop: '2px' }}>
                C_sqr={dispatchResult.backend_costs.cost_sqr} | C_mult={dispatchResult.backend_costs.cost_mult}x | C_ctrl={dispatchResult.backend_costs.cost_ctrl}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', color: '#64748b', fontWeight: 600 }}>
                Scale
              </div>
              <div style={{ fontSize: '15px', fontWeight: 700, color: '#38bdf8', marginTop: '2px' }}>
                {dispatchResult.exponent_bits}-bit
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
