import React, { useState, useEffect } from 'react'
import ExponentAnalyzer from './components/ExponentAnalyzer.jsx'
import BenchmarkPanel from './components/BenchmarkPanel.jsx'
import RSAPanel from './components/RSAPanel.jsx'
import BackendsPanel from './components/BackendsPanel.jsx'

const TABS = [
  { id: 'analyzer',  label: 'Exponent Analyzer' },
  { id: 'benchmark', label: 'Benchmark Suite'   },
  { id: 'rsa',       label: 'RSA Cryptosystem'  },
  { id: 'backends',  label: 'Hardware Targets'  },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('analyzer')
  const [apiStatus, setApiStatus] = useState('checking')

  useEffect(() => {
    fetch('/api/backends')
      .then(res => {
        if (res.ok) setApiStatus('online')
        else setApiStatus('degraded')
      })
      .catch(() => setApiStatus('offline'))
  }, [])

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#0a0d14',
      color: '#e2e8f0',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      display: 'flex',
      flexDirection: 'column',
    }}>
      {/* Top Navigation Bar */}
      <header style={{
        backgroundColor: '#0f1422',
        borderBottom: '1px solid #1e2638',
        padding: '0 24px',
        height: '64px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 800,
            fontSize: '14px',
            color: '#ffffff',
            letterSpacing: '0.5px',
          }}>
            ACE
          </div>
          <div>
            <div style={{ fontSize: '15px', fontWeight: 700, color: '#f8fafc', letterSpacing: '-0.2px' }}>
              Adaptive Cryptographic Engine
            </div>
            <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 500 }}>
              Workload-Aware Exponentiation & Side-Channel Mitigation
            </div>
          </div>
        </div>

        {/* Tab Switcher */}
        <nav style={{
          display: 'flex',
          gap: '4px',
          backgroundColor: '#070a10',
          padding: '4px',
          borderRadius: '8px',
          border: '1px solid #1a2234',
        }}>
          {TABS.map(tab => {
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  padding: '6px 14px',
                  borderRadius: '6px',
                  border: 'none',
                  fontSize: '13px',
                  fontWeight: isActive ? 600 : 500,
                  backgroundColor: isActive ? '#1e293b' : 'transparent',
                  color: isActive ? '#38bdf8' : '#94a3b8',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  outline: 'none',
                }}
              >
                {tab.label}
              </button>
            )
          })}
        </nav>

        {/* System Status Pill */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: apiStatus === 'online' ? '#10b981' : apiStatus === 'checking' ? '#f59e0b' : '#ef4444',
            boxShadow: apiStatus === 'online' ? '0 0 8px rgba(16,185,129,0.6)' : 'none',
          }} />
          <span style={{ fontSize: '12px', color: '#94a3b8', fontWeight: 500, textTransform: 'capitalize' }}>
            API {apiStatus}
          </span>
        </div>
      </header>

      {/* Main View Area */}
      <main style={{
        flex: 1,
        width: '100%',
        maxWidth: '1360px',
        margin: '0 auto',
        padding: '24px 20px 48px 20px',
        boxSizing: 'border-box',
      }}>
        {activeTab === 'analyzer'  && <ExponentAnalyzer />}
        {activeTab === 'benchmark' && <BenchmarkPanel />}
        {activeTab === 'rsa'       && <RSAPanel />}
        {activeTab === 'backends'  && <BackendsPanel />}
      </main>

      {/* Minimalist Footer */}
      <footer style={{
        borderTop: '1px solid #151b2a',
        padding: '16px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '12px',
        color: '#475569',
        backgroundColor: '#0a0d14',
      }}>
        <span>Adaptive Cryptographic Engine · Modular Exponentiation Architecture</span>
        <span>C99 Intrinsics · Python AOT Predictor · SystemVerilog Targets</span>
      </footer>
    </div>
  )
}
