import React, { useState } from 'react'
import ExponentAnalyzer from './components/ExponentAnalyzer.jsx'
import BenchmarkPanel from './components/BenchmarkPanel.jsx'
import RSAPanel from './components/RSAPanel.jsx'
import BackendsPanel from './components/BackendsPanel.jsx'

const NAV_TABS = [
  { id: 'analyzer',  label: '🔍 Exponent Analyzer' },
  { id: 'benchmark', label: '📊 Live Benchmark'    },
  { id: 'rsa',       label: '🔐 RSA Pipeline'      },
  { id: 'backends',  label: '⚙️ Hardware Backends'  },
]

const styles = {
  app: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0f1117 0%, #1a1f2e 100%)',
    color: '#e2e8f0',
  },
  header: {
    background: 'rgba(26,31,46,0.95)',
    borderBottom: '1px solid #2d3748',
    padding: '16px 32px',
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    backdropFilter: 'blur(8px)',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  logo: {
    fontSize: '28px',
  },
  titleBlock: { flex: 1 },
  title: {
    fontSize: '20px',
    fontWeight: 700,
    background: 'linear-gradient(90deg, #60a5fa, #a78bfa)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  subtitle: { fontSize: '12px', color: '#718096', marginTop: '2px' },
  badge: {
    background: 'linear-gradient(90deg, #2563eb, #7c3aed)',
    color: 'white',
    padding: '4px 12px',
    borderRadius: '20px',
    fontSize: '11px',
    fontWeight: 600,
  },
  nav: {
    display: 'flex',
    gap: '4px',
    padding: '12px 32px',
    borderBottom: '1px solid #1e2535',
  },
  tabBtn: (active) => ({
    padding: '8px 18px',
    borderRadius: '8px',
    border: 'none',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: 600,
    transition: 'all 0.2s',
    background: active ? 'linear-gradient(90deg, #2563eb, #7c3aed)' : 'transparent',
    color: active ? 'white' : '#718096',
    outline: 'none',
  }),
  content: { padding: '32px', maxWidth: '1400px', margin: '0 auto' },
  footer: {
    textAlign: 'center',
    padding: '20px',
    color: '#4a5568',
    fontSize: '12px',
    borderTop: '1px solid #1e2535',
  },
}

export default function App() {
  const [activeTab, setActiveTab] = useState('analyzer')

  return (
    <div style={styles.app}>
      {/* Header */}
      <header style={styles.header}>
        <span style={styles.logo}>🔐</span>
        <div style={styles.titleBlock}>
          <div style={styles.title}>ML-Assisted Adaptive Cryptographic Engine</div>
          <div style={styles.subtitle}>
            Sourav Yadav (23U01074) · Eric Dazzle George (23U01035) · IIIT Bhopal · Supervisor: Dr. Aashish Parihar
          </div>
        </div>
        <span style={styles.badge}>B.Tech Major Project</span>
      </header>

      {/* Navigation */}
      <nav style={styles.nav}>
        {NAV_TABS.map(tab => (
          <button
            key={tab.id}
            style={styles.tabBtn(activeTab === tab.id)}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {/* Main Content */}
      <main style={styles.content}>
        {activeTab === 'analyzer'  && <ExponentAnalyzer />}
        {activeTab === 'benchmark' && <BenchmarkPanel />}
        {activeTab === 'rsa'       && <RSAPanel />}
        {activeTab === 'backends'  && <BackendsPanel />}
      </main>

      {/* Footer */}
      <footer style={styles.footer}>
        ML-Assisted Adaptive Cryptographic Engine · Department of ECE · IIIT Bhopal · 2026
      </footer>
    </div>
  )
}
