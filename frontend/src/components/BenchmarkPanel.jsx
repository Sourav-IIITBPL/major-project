import React, { useState } from 'react'
import api from '../api'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell
} from 'recharts'

const STRATEGY_COLORS = {
  fixed_binary:     '#dc2626',
  fixed_naf:        '#d97706',
  fixed_wnaf:       '#2563eb',
  fixed_vlim:       '#7c3aed',
  ml_adaptive:      '#059669',
  hybrid_sliced:    '#d97706',
  blinded_adaptive: '#0284c7',
}

const STRATEGY_NAMES = {
  fixed_binary:     'Binary (Baseline)',
  fixed_naf:        'Standard NAF',
  fixed_wnaf:       'Windowed NAF (w=3)',
  fixed_vlim:       'Adaptive VLIM',
  ml_adaptive:      'ML-Adaptive (Ours)',
  hybrid_sliced:    'Hybrid Sliced',
  blinded_adaptive: 'Blinded-Adaptive (Secure)',
}

export default function BenchmarkPanel() {
  const [bitLen, setBitLen] = useState('1024')
  const [profile, setProfile] = useState('uniform')
  const [trials, setTrials] = useState('1')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleRun = async () => {
    setLoading(true)
    setError('')
    setData(null)
    try {
      const res = await api.post('/api/benchmark', {
        bit_length: parseInt(bitLen, 10),
        profile: profile,
        trials: parseInt(trials, 10),
      })
      setData(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Benchmark execution failed.')
    } finally {
      setLoading(false)
    }
  }

  const chartLatency = data?.results.map(r => ({
    name: STRATEGY_NAMES[r.mode] || r.mode,
    latency: r.avg_time_ms,
    mode: r.mode,
  })) || []

  const chartMults = data?.results.map(r => ({
    name: STRATEGY_NAMES[r.mode] || r.mode,
    mults: r.avg_mults,
    mode: r.mode,
  })) || []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Title */}
      <div>
        <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#f1f5f9', margin: 0 }}>
          Comparative Cryptographic Benchmark Suite
        </h1>
        <p style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
          Executes true RSA modular exponentiations across 7 strategies simultaneously, recording wall-clock latency, multiplications, and state-machine transitions.
        </p>
      </div>

      {/* Configuration Controls Card */}
      <div style={{
        backgroundColor: '#0f1422',
        border: '1px solid #1e2638',
        borderRadius: '10px',
        padding: '20px',
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px',
          alignItems: 'flex-end',
        }}>
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '6px' }}>
              Cryptographic Scale
            </label>
            <select
              value={bitLen}
              onChange={e => setBitLen(e.target.value)}
              style={{
                width: '100%',
                backgroundColor: '#161d2e',
                border: '1px solid #273349',
                color: '#e2e8f0',
                padding: '8px 12px',
                borderRadius: '6px',
                fontSize: '13px',
                outline: 'none',
              }}
            >
              <option value="256">256-bit (ECC field scale)</option>
              <option value="512">512-bit (Legacy RSA)</option>
              <option value="1024">1024-bit (Standard RSA)</option>
              <option value="2048">2048-bit (NIST Standard)</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '6px' }}>
              Exponent Topology
            </label>
            <select
              value={profile}
              onChange={e => setProfile(e.target.value)}
              style={{
                width: '100%',
                backgroundColor: '#161d2e',
                border: '1px solid #273349',
                color: '#e2e8f0',
                padding: '8px 12px',
                borderRadius: '6px',
                fontSize: '13px',
                outline: 'none',
              }}
            >
              <option value="uniform">Uniform Random</option>
              <option value="dense">Dense Key (&gt;85% Ones)</option>
              <option value="sparse">Sparse Key (&lt;15% Ones)</option>
              <option value="bursty">Bursty Zero Clusters</option>
              <option value="alternating">Alternating (101010...)</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '6px' }}>
              Statistical Iterations
            </label>
            <select
              value={trials}
              onChange={e => setTrials(e.target.value)}
              style={{
                width: '100%',
                backgroundColor: '#161d2e',
                border: '1px solid #273349',
                color: '#e2e8f0',
                padding: '8px 12px',
                borderRadius: '6px',
                fontSize: '13px',
                outline: 'none',
              }}
            >
              <option value="1">1 Run (Fastest)</option>
              <option value="2">2 Runs (Averaged)</option>
              <option value="3">3 Runs (Statistical)</option>
            </select>
          </div>

          <div>
            <button
              onClick={handleRun}
              disabled={loading}
              style={{
                width: '100%',
                backgroundColor: '#2563eb',
                color: '#ffffff',
                border: 'none',
                padding: '9px 16px',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1,
              }}
            >
              {loading ? 'Evaluating...' : 'Execute Benchmark'}
            </button>
          </div>
        </div>

        {error && (
          <div style={{ marginTop: '14px', fontSize: '13px', color: '#ef4444' }}>
            {error}
          </div>
        )}
      </div>

      {/* Results Section */}
      {data && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Charts Row */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
            gap: '20px',
          }}>
            {/* Latency Chart */}
            <div style={{
              backgroundColor: '#0f1422',
              border: '1px solid #1e2638',
              borderRadius: '10px',
              padding: '20px',
            }}>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc', marginBottom: '4px' }}>
                Execution Latency (ms)
              </div>
              <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '16px' }}>
                Lower values indicate superior wall-clock performance.
              </div>

              <div style={{ width: '100%', height: '260px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartLatency} layout="vertical" margin={{ left: 10, right: 30, top: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e2638" horizontal={false} />
                    <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                    <YAxis dataKey="name" type="category" tick={{ fill: '#cbd5e1', fontSize: 11 }} width={140} />
                    <Tooltip
                      formatter={(val) => [`${val.toFixed(3)} ms`, 'Latency']}
                      contentStyle={{ backgroundColor: '#0f1422', borderColor: '#273349', borderRadius: '6px', fontSize: '12px', color: '#f8fafc' }}
                    />
                    <Bar dataKey="latency" radius={[0, 4, 4, 0]}>
                      {chartLatency.map((entry, idx) => (
                        <Cell key={idx} fill={STRATEGY_COLORS[entry.mode] || '#38bdf8'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Multiplications Chart */}
            <div style={{
              backgroundColor: '#0f1422',
              border: '1px solid #1e2638',
              borderRadius: '10px',
              padding: '20px',
            }}>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc', marginBottom: '4px' }}>
                Modular Multiplications Count
              </div>
              <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '16px' }}>
                Primary determinant of hardware area and cryptographic power dissipation.
              </div>

              <div style={{ width: '100%', height: '260px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartMults} layout="vertical" margin={{ left: 10, right: 30, top: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e2638" horizontal={false} />
                    <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                    <YAxis dataKey="name" type="category" tick={{ fill: '#cbd5e1', fontSize: 11 }} width={140} />
                    <Tooltip
                      formatter={(val) => [val, 'Multiplications']}
                      contentStyle={{ backgroundColor: '#0f1422', borderColor: '#273349', borderRadius: '6px', fontSize: '12px', color: '#f8fafc' }}
                    />
                    <Bar dataKey="mults" radius={[0, 4, 4, 0]}>
                      {chartMults.map((entry, idx) => (
                        <Cell key={idx} fill={STRATEGY_COLORS[entry.mode] || '#38bdf8'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Detailed Data Table */}
          <div style={{
            backgroundColor: '#0f1422',
            border: '1px solid #1e2638',
            borderRadius: '10px',
            padding: '20px',
            overflowX: 'auto',
          }}>
            <div style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc', marginBottom: '12px' }}>
              Comparative Performance Metrics ({data.bit_length}-bit {data.profile})
            </div>

            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', minWidth: '600px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #273349', textAlign: 'left' }}>
                  <th style={{ padding: '10px 12px', color: '#64748b', fontWeight: 600 }}>Strategy</th>
                  <th style={{ padding: '10px 12px', color: '#64748b', fontWeight: 600, textAlign: 'right' }}>Latency (ms)</th>
                  <th style={{ padding: '10px 12px', color: '#64748b', fontWeight: 600, textAlign: 'right' }}>Speedup</th>
                  <th style={{ padding: '10px 12px', color: '#64748b', fontWeight: 600, textAlign: 'right' }}>Multiplications</th>
                  <th style={{ padding: '10px 12px', color: '#64748b', fontWeight: 600, textAlign: 'right' }}>Mult Reduction</th>
                  <th style={{ padding: '10px 12px', color: '#64748b', fontWeight: 600, textAlign: 'right' }}>State Transitions</th>
                </tr>
              </thead>
              <tbody>
                {data.results.map((row, idx) => {
                  const isWinner = row.mode === 'ml_adaptive'
                  return (
                    <tr key={idx} style={{
                      borderBottom: '1px solid #151d2e',
                      backgroundColor: isWinner ? 'rgba(5,150,105,0.08)' : idx % 2 === 0 ? '#0b0f19' : 'transparent',
                    }}>
                      <td style={{ padding: '10px 12px', fontWeight: 600, color: STRATEGY_COLORS[row.mode] || '#e2e8f0' }}>
                        {STRATEGY_NAMES[row.mode] || row.mode}
                      </td>
                      <td style={{ padding: '10px 12px', textAlign: 'right', fontFamily: 'monospace' }}>
                        {row.avg_time_ms.toFixed(3)} ms
                      </td>
                      <td style={{
                        padding: '10px 12px',
                        textAlign: 'right',
                        fontWeight: 600,
                        color: row.speedup_pct > 0 ? '#10b981' : row.speedup_pct < 0 ? '#ef4444' : '#94a3b8',
                      }}>
                        {row.speedup_pct > 0 ? `+${row.speedup_pct}%` : `${row.speedup_pct}%`}
                      </td>
                      <td style={{ padding: '10px 12px', textAlign: 'right', fontFamily: 'monospace' }}>
                        {row.avg_mults}
                      </td>
                      <td style={{
                        padding: '10px 12px',
                        textAlign: 'right',
                        fontWeight: 600,
                        color: row.mult_cut_pct > 0 ? '#10b981' : '#94a3b8',
                      }}>
                        {row.mult_cut_pct > 0 ? `-${row.mult_cut_pct}%` : `${row.mult_cut_pct}%`}
                      </td>
                      <td style={{ padding: '10px 12px', textAlign: 'right', fontFamily: 'monospace' }}>
                        {row.avg_iters}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
