import React, { useState } from 'react'
import axios from 'axios'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer, Cell
} from 'recharts'

const card = {
  background: 'rgba(26,31,46,0.8)', border: '1px solid #2d3748',
  borderRadius: '12px', padding: '24px', marginBottom: '20px',
}
const label = { fontSize: '13px', color: '#a0aec0', marginBottom: '6px', fontWeight: 600 }
const select = {
  background: '#0f1117', border: '1px solid #2d3748', borderRadius: '8px',
  padding: '10px 14px', color: '#e2e8f0', fontSize: '13px', outline: 'none', width: '100%'
}
const btn = {
  background: 'linear-gradient(90deg, #2563eb, #7c3aed)', color: 'white',
  border: 'none', borderRadius: '8px', padding: '10px 24px',
  cursor: 'pointer', fontWeight: 700, fontSize: '14px',
}

const MODE_COLORS = {
  fixed_binary: '#e74c3c', fixed_naf: '#e67e22', fixed_wnaf: '#3498db',
  fixed_vlim: '#9b59b6', ml_adaptive: '#2ecc71', hybrid_sliced: '#f39c12', blinded_adaptive: '#1abc9c'
}
const MODE_LABELS = {
  fixed_binary: 'Binary', fixed_naf: 'NAF', fixed_wnaf: 'wNAF',
  fixed_vlim: 'VLIM', ml_adaptive: 'ML-Adaptive', hybrid_sliced: 'Hybrid-Sliced', blinded_adaptive: 'Blinded-Adaptive'
}

export default function BenchmarkPanel() {
  const [bitLen,  setBitLen]  = useState('1024')
  const [profile, setProfile] = useState('uniform')
  const [trials,  setTrials]  = useState('3')
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')

  const run = async () => {
    setLoading(true); setError(''); setData(null)
    try {
      const { data: res } = await axios.post('/api/benchmark', {
        bit_length: parseInt(bitLen),
        profile,
        trials: parseInt(trials),
      })
      setData(res)
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  const timeChartData = data?.results.map(r => ({
    name: MODE_LABELS[r.mode] || r.mode,
    'Time (ms)': r.avg_time_ms,
    color: MODE_COLORS[r.mode] || '#ccc',
  })) || []

  const multsChartData = data?.results.map(r => ({
    name: MODE_LABELS[r.mode] || r.mode,
    'Multiplications': r.avg_mults,
    color: MODE_COLORS[r.mode] || '#ccc',
  })) || []

  return (
    <div>
      <h2 style={{ fontSize: '22px', fontWeight: 700, marginBottom: '20px' }}>
        📊 Live Multi-Strategy Benchmark
      </h2>

      {/* Controls */}
      <div style={card}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: '16px' }}>
          <div>
            <div style={label}>Bit Length</div>
            <select style={select} value={bitLen} onChange={e => setBitLen(e.target.value)}>
              {['256','512','1024','2048'].map(b => (
                <option key={b} value={b}>{b}-bit</option>
              ))}
            </select>
          </div>
          <div>
            <div style={label}>Exponent Profile</div>
            <select style={select} value={profile} onChange={e => setProfile(e.target.value)}>
              {['uniform','sparse','dense','bursty','alternating'].map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
          <div>
            <div style={label}>Trials (averaged)</div>
            <select style={select} value={trials} onChange={e => setTrials(e.target.value)}>
              {['1','2','3','5'].map(t => (
                <option key={t} value={t}>{t} trial{t>1?'s':''}</option>
              ))}
            </select>
          </div>
        </div>
        <button style={{ ...btn, marginTop: '16px' }} onClick={run} disabled={loading}>
          {loading ? '⏳ Running Benchmark… (may take 30–60s for large scales)' : '▶ Run Benchmark'}
        </button>
        {error && <div style={{ color: '#fc8181', marginTop: '10px', fontSize: '13px' }}>{error}</div>}
      </div>

      {/* Results */}
      {data && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            {/* Latency Chart */}
            <div style={card}>
              <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '14px', color: '#60a5fa' }}>
                ⏱ Execution Latency (ms) — Lower is Better
              </h3>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={timeChartData} layout="vertical" margin={{ left: 20, right: 30 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" horizontal={false} />
                  <XAxis type="number" tick={{ fill: '#718096', fontSize: 11 }} />
                  <YAxis dataKey="name" type="category" tick={{ fill: '#a0aec0', fontSize: 11 }} width={100} />
                  <Tooltip
                    formatter={(v) => [`${v.toFixed(3)} ms`, 'Latency']}
                    contentStyle={{ background: '#1a1f2e', border: '1px solid #2d3748', borderRadius: '8px', color: '#e2e8f0' }}
                  />
                  <Bar dataKey="Time (ms)" radius={[0,4,4,0]}>
                    {timeChartData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Multiplications Chart */}
            <div style={card}>
              <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '14px', color: '#a78bfa' }}>
                ✖ Modular Multiplications — Lower is Better
              </h3>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={multsChartData} layout="vertical" margin={{ left: 20, right: 30 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" horizontal={false} />
                  <XAxis type="number" tick={{ fill: '#718096', fontSize: 11 }} />
                  <YAxis dataKey="name" type="category" tick={{ fill: '#a0aec0', fontSize: 11 }} width={100} />
                  <Tooltip
                    formatter={(v) => [`${v.toFixed(1)}`, 'Multiplications']}
                    contentStyle={{ background: '#1a1f2e', border: '1px solid #2d3748', borderRadius: '8px', color: '#e2e8f0' }}
                  />
                  <Bar dataKey="Multiplications" radius={[0,4,4,0]}>
                    {multsChartData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Detailed Table */}
          <div style={card}>
            <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '14px', color: '#34d399' }}>
              📋 Detailed Results — {data.bit_length}-bit {data.profile} ({data.trials} trials avg)
            </h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #2d3748' }}>
                    {['Strategy','Time (ms)','Speedup vs Binary','Multiplications','Mult Cut','Iterations','HW Cost'].map(h => (
                      <th key={h} style={{ textAlign: h==='Strategy'?'left':'right', color: '#718096', padding: '8px 12px' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.results.map((r, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid #1e2535', background: i%2===0?'transparent':'rgba(255,255,255,0.02)' }}>
                      <td style={{ padding: '8px 12px' }}>
                        <span style={{
                          display: 'inline-block', width: '10px', height: '10px',
                          borderRadius: '50%', background: MODE_COLORS[r.mode], marginRight: '8px'
                        }} />
                        {MODE_LABELS[r.mode]}
                      </td>
                      <td style={{ textAlign: 'right', padding: '8px 12px', fontFamily: 'monospace' }}>{r.avg_time_ms.toFixed(3)}</td>
                      <td style={{ textAlign: 'right', padding: '8px 12px', fontFamily: 'monospace',
                        color: r.speedup_pct > 0 ? '#34d399' : r.speedup_pct < 0 ? '#fc8181' : '#e2e8f0' }}>
                        {r.speedup_pct > 0 ? '+' : ''}{r.speedup_pct.toFixed(1)}%
                      </td>
                      <td style={{ textAlign: 'right', padding: '8px 12px', fontFamily: 'monospace' }}>{r.avg_mults.toFixed(0)}</td>
                      <td style={{ textAlign: 'right', padding: '8px 12px', fontFamily: 'monospace',
                        color: r.mult_cut_pct > 0 ? '#34d399' : '#e2e8f0' }}>
                        {r.mult_cut_pct > 0 ? '+' : ''}{r.mult_cut_pct.toFixed(1)}%
                      </td>
                      <td style={{ textAlign: 'right', padding: '8px 12px', fontFamily: 'monospace' }}>{r.avg_iters.toFixed(0)}</td>
                      <td style={{ textAlign: 'right', padding: '8px 12px', fontFamily: 'monospace' }}>{r.avg_hw_cost.toFixed(1)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
