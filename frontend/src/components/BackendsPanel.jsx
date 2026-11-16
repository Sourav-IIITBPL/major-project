import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts'

const card = {
  background: 'rgba(26,31,46,0.8)', border: '1px solid #2d3748',
  borderRadius: '12px', padding: '24px', marginBottom: '20px',
}
const label   = { fontSize: '13px', color: '#a0aec0', marginBottom: '6px', fontWeight: 600 }
const select  = {
  background: '#0f1117', border: '1px solid #2d3748', borderRadius: '8px',
  padding: '10px 14px', color: '#e2e8f0', fontSize: '13px', outline: 'none', width: '100%'
}
const textarea = { ...select, height: '70px', resize: 'vertical', fontFamily: 'monospace', fontSize: '12px' }
const btn = {
  background: 'linear-gradient(90deg, #2563eb, #7c3aed)', color: 'white',
  border: 'none', borderRadius: '8px', padding: '10px 24px',
  cursor: 'pointer', fontWeight: 700, fontSize: '14px', marginTop: '12px',
}

const BACKEND_COLORS = {
  python_bigint:  '#3498db',
  c_montgomery:   '#2ecc71',
  fpga_radix4:    '#9b59b6',
  asic_csa52:     '#e74c3c',
}

export default function BackendsPanel() {
  const [backends,    setBackends]   = useState([])
  const [selected,    setSelected]   = useState('python_bigint')
  const [expInput,    setExpInput]   = useState('')
  const [dispResult,  setDispResult] = useState(null)
  const [loading,     setLoading]    = useState(false)
  const [error,       setError]      = useState('')

  useEffect(() => {
    axios.get('/api/backends')
      .then(r => setBackends(r.data.backends))
      .catch(() => {})
  }, [])

  const dispatch = async () => {
    if (!expInput.trim()) { setError('Enter an exponent.'); return }
    setLoading(true); setError(''); setDispResult(null)
    try {
      const { data } = await axios.post('/api/backends/dispatch', {
        exponent: parseInt(expInput),
        backend:  selected,
      })
      setDispResult(data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  const activeCfg = backends.find(b => b.name === selected)
  const radarData = activeCfg ? [
    { axis: 'C_sqr',  value: 1.0 },
    { axis: 'C_mult', value: activeCfg.cost_mult },
    { axis: 'C_ctrl', value: Math.min(activeCfg.cost_ctrl * 10, 5) },
  ] : []

  return (
    <div>
      <h2 style={{ fontSize: '22px', fontWeight: 700, marginBottom: '20px' }}>
        ⚙️ Cross-Architecture Hardware Backend Profiling
      </h2>

      <div style={{ background: 'rgba(37,99,235,0.06)', border: '1px solid #2563eb', borderRadius: '10px', padding: '14px 18px', marginBottom: '20px', fontSize: '13px', color: '#93c5fd', lineHeight: 1.6 }}>
        <strong>Insight:</strong> The optimal strategy crossover point shifts dramatically across hardware backends.
        A backend-specific trained model automatically captures these cross-architecture divergences —
        this is the core justification for using ML instead of a hardcoded rule.
      </div>

      {/* Backend Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2,1fr)', gap: '16px', marginBottom: '20px' }}>
        {backends.map(b => (
          <div
            key={b.name}
            onClick={() => setSelected(b.name)}
            style={{
              ...card, cursor: 'pointer', marginBottom: 0,
              borderColor: selected === b.name ? BACKEND_COLORS[b.name] : '#2d3748',
              background: selected === b.name ? `rgba(${b.name === 'python_bigint' ? '52,152,219' : b.name === 'c_montgomery' ? '46,204,113' : b.name === 'fpga_radix4' ? '155,89,182' : '231,76,60'},0.08)` : 'rgba(26,31,46,0.8)',
              transition: 'all 0.2s',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
              <span style={{
                width: 12, height: 12, borderRadius: '50%',
                background: BACKEND_COLORS[b.name], flexShrink: 0,
              }} />
              <span style={{ fontWeight: 700, fontSize: '14px' }}>{b.name}</span>
              {selected === b.name && <span style={{ marginLeft: 'auto', fontSize: '12px', color: BACKEND_COLORS[b.name] }}>✓ Selected</span>}
            </div>
            <div style={{ display: 'flex', gap: '20px', marginBottom: '8px', fontSize: '13px' }}>
              <div><span style={{ color: '#718096' }}>C_sqr:</span> <strong style={{ color: '#e2e8f0' }}>{b.cost_sqr}</strong></div>
              <div><span style={{ color: '#718096' }}>C_mult:</span> <strong style={{ color: '#fbbf24' }}>{b.cost_mult}×</strong></div>
              <div><span style={{ color: '#718096' }}>C_ctrl:</span> <strong style={{ color: '#a78bfa' }}>{b.cost_ctrl}</strong></div>
            </div>
            <div style={{ fontSize: '12px', color: '#718096', lineHeight: 1.5 }}>{b.description.slice(0, 100)}…</div>
          </div>
        ))}
      </div>

      {/* Dispatch Tester */}
      <div style={card}>
        <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '14px' }}>
          🎯 Backend-Specific Strategy Dispatch
        </h3>
        <div style={{ marginBottom: '12px' }}>
          <div style={label}>Exponent Integer</div>
          <textarea
            style={textarea}
            value={expInput}
            onChange={e => setExpInput(e.target.value)}
            placeholder="Paste a large integer exponent here…"
          />
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <div style={{ flex: 1 }}>
            <div style={label}>Target Backend</div>
            <select style={select} value={selected} onChange={e => setSelected(e.target.value)}>
              {backends.map(b => <option key={b.name} value={b.name}>{b.name}</option>)}
            </select>
          </div>
          <button style={{ ...btn, marginTop: '20px' }} onClick={dispatch} disabled={loading}>
            {loading ? '⏳ Dispatching…' : '⚡ Dispatch for Backend'}
          </button>
        </div>
        {error && <div style={{ color: '#fc8181', marginTop: '10px', fontSize: '13px' }}>{error}</div>}

        {dispResult && (
          <div style={{ marginTop: '20px', background: 'rgba(37,99,235,0.08)', border: '1px solid #3b82f6', borderRadius: '10px', padding: '16px' }}>
            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
              <div>
                <div style={{ fontSize: '11px', color: '#718096' }}>EXPONENT SIZE</div>
                <div style={{ fontWeight: 700, fontSize: '20px', color: '#60a5fa' }}>{dispResult.exponent_bits}-bit</div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: '#718096' }}>BACKEND</div>
                <div style={{ fontWeight: 700, fontSize: '16px', color: BACKEND_COLORS[dispResult.backend] || '#e2e8f0' }}>{dispResult.backend}</div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: '#718096' }}>OPTIMAL STRATEGY</div>
                <div style={{ fontWeight: 700, fontSize: '20px', color: '#34d399' }}>{dispResult.predicted_strategy}</div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: '#718096' }}>COST COEFFICIENTS</div>
                <div style={{ fontSize: '12px', fontFamily: 'monospace', color: '#a0aec0' }}>
                  sqr={dispResult.backend_costs?.cost_sqr} · mult={dispResult.backend_costs?.cost_mult}× · ctrl={dispResult.backend_costs?.cost_ctrl}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Cost Comparison Table */}
      {backends.length > 0 && (
        <div style={card}>
          <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '14px', color: '#a78bfa' }}>
            📊 Backend Cost Coefficient Comparison
          </h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #2d3748' }}>
                {['Backend','C_sqr','C_mult','C_ctrl','Dominant Strategy Favored'].map(h => (
                  <th key={h} style={{ textAlign: h==='Backend'?'left':'center', color: '#718096', padding: '8px 12px' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {backends.map((b, i) => {
                const dominant = b.cost_ctrl < 0.1 ? 'VLIM (clock cycles dominate)' : b.cost_mult > 3 ? 'VLIM / NAF (mult expensive)' : b.cost_mult > 1.5 ? 'wNAF (reduce mults)' : 'Binary / wNAF'
                return (
                  <tr key={b.name} style={{ borderBottom: '1px solid #1e2535', background: b.name === selected ? `rgba(255,255,255,0.03)` : 'transparent' }}>
                    <td style={{ padding: '10px 12px', fontWeight: 700, color: BACKEND_COLORS[b.name] }}>{b.name}</td>
                    <td style={{ textAlign: 'center', padding: '10px 12px', fontFamily: 'monospace' }}>{b.cost_sqr}</td>
                    <td style={{ textAlign: 'center', padding: '10px 12px', fontFamily: 'monospace', color: '#fbbf24', fontWeight: 700 }}>{b.cost_mult}</td>
                    <td style={{ textAlign: 'center', padding: '10px 12px', fontFamily: 'monospace', color: '#a78bfa' }}>{b.cost_ctrl}</td>
                    <td style={{ textAlign: 'center', padding: '10px 12px', color: '#a0aec0', fontSize: '12px' }}>{dominant}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
