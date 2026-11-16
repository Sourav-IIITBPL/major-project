import React, { useState } from 'react'
import axios from 'axios'

const card = {
  background: 'rgba(26,31,46,0.8)', border: '1px solid #2d3748',
  borderRadius: '12px', padding: '24px', marginBottom: '20px',
}
const label   = { fontSize: '13px', color: '#a0aec0', marginBottom: '6px', fontWeight: 600 }
const select  = {
  background: '#0f1117', border: '1px solid #2d3748', borderRadius: '8px',
  padding: '10px 14px', color: '#e2e8f0', fontSize: '13px', outline: 'none', width: '100%'
}
const input   = { ...select }
const textarea = { ...input, height: '70px', resize: 'vertical', fontFamily: 'monospace', fontSize: '12px' }
const btn = (color = '#2563eb') => ({
  background: `linear-gradient(90deg, ${color}, #7c3aed)`, color: 'white',
  border: 'none', borderRadius: '8px', padding: '10px 24px',
  cursor: 'pointer', fontWeight: 700, fontSize: '14px', marginRight: '12px',
})
const statusBox = (ok) => ({
  display: 'inline-block', padding: '4px 14px', borderRadius: '20px', fontWeight: 700,
  fontSize: '14px', background: ok ? 'rgba(52,211,153,0.15)' : 'rgba(252,129,129,0.15)',
  color: ok ? '#34d399' : '#fc8181', border: `1px solid ${ok ? '#34d399' : '#fc8181'}`,
})

function KeyDisplay({ keyPair }) {
  if (!keyPair) return null
  return (
    <div style={{ ...card, background: 'rgba(37,99,235,0.08)', borderColor: '#3b82f6' }}>
      <h3 style={{ color: '#60a5fa', marginBottom: '14px', fontSize: '14px' }}>✅ Key Pair Generated</h3>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', fontSize: '12px' }}>
        <div>
          <div style={{ color: '#34d399', fontWeight: 700, marginBottom: '6px' }}>PUBLIC KEY (share freely)</div>
          <div style={{ fontFamily: 'monospace', background: '#0f1117', borderRadius: '6px', padding: '10px', wordBreak: 'break-all', color: '#a0aec0' }}>
            e = {keyPair.public_key.e.toString()}<br/>
            n = {keyPair.public_key.n.toString().slice(0,60)}…
          </div>
        </div>
        <div>
          <div style={{ color: '#fc8181', fontWeight: 700, marginBottom: '6px' }}>PRIVATE KEY (keep secret)</div>
          <div style={{ fontFamily: 'monospace', background: '#0f1117', borderRadius: '6px', padding: '10px', wordBreak: 'break-all', color: '#a0aec0' }}>
            d = {keyPair.private_key.d.toString().slice(0,60)}…<br/>
            phi_n = {keyPair.private_key.phi_n.toString().slice(0,50)}…
          </div>
        </div>
      </div>
    </div>
  )
}

export default function RSAPanel() {
  const [bits,    setBits]    = useState('1024')
  const [keyPair, setKeyPair] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')

  // Sign/Verify state
  const [signText,     setSignText]     = useState('Hello, IIIT Bhopal! This is a signed message.')
  const [signature,    setSignature]    = useState('')
  const [signResult,   setSignResult]   = useState(null)
  const [verifyResult, setVerifyResult] = useState(null)
  const [signLoading,  setSignLoading]  = useState(false)
  const [verifyLoading,setVerifyLoading]= useState(false)

  const keygen = async () => {
    setLoading(true); setError('')
    setKeyPair(null); setSignResult(null); setVerifyResult(null); setSignature('')
    try {
      const { data } = await axios.post('/api/rsa/keygen', { bits: parseInt(bits) })
      setKeyPair(data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  const sign = async () => {
    if (!keyPair) { setError('Generate a key pair first.'); return }
    setSignLoading(true); setSignResult(null); setVerifyResult(null)
    try {
      const { data } = await axios.post('/api/rsa/sign', {
        text:  signText,
        d:     keyPair.private_key.d,
        n:     keyPair.private_key.n,
        p:     keyPair.private_key.p,
        q:     keyPair.private_key.q,
        phi_n: keyPair.private_key.phi_n,
      })
      setSignResult(data)
      setSignature(data.signature.toString())
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setSignLoading(false)
    }
  }

  const verify = async (tamper = false) => {
    if (!keyPair || !signature) { setError('Sign first.'); return }
    setVerifyLoading(true); setVerifyResult(null)
    try {
      let sig = BigInt(signature)
      if (tamper) sig = sig ^ 0xFFn
      const { data } = await axios.post('/api/rsa/verify', {
        text:      signText,
        signature: sig.toString(),
        e:         keyPair.public_key.e,
        n:         keyPair.public_key.n,
      })
      setVerifyResult({ ...data, tampered: tamper })
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setVerifyLoading(false)
    }
  }

  return (
    <div>
      <h2 style={{ fontSize: '22px', fontWeight: 700, marginBottom: '20px' }}>
        🔐 Full RSA Key Lifecycle Pipeline
      </h2>

      <div style={{ background: 'rgba(37,99,235,0.06)', border: '1px solid #2563eb', borderRadius: '10px', padding: '14px 18px', marginBottom: '20px', fontSize: '13px', color: '#93c5fd', lineHeight: 1.6 }}>
        <strong>How it works:</strong> All private-key operations (keygen, sign, decrypt) use the{' '}
        <strong>Blinded-Adaptive</strong> engine (Euler totient randomization, side-channel immune).
        All public-key operations (encrypt, verify) use the <strong>ML-Adaptive</strong> engine for
        maximum throughput. Both are backed by the same ML dispatch layer.
      </div>

      {/* Key Generation */}
      <div style={card}>
        <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '14px' }}>① Key Generation</h3>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: '16px' }}>
          <div style={{ flex: 1 }}>
            <div style={label}>RSA Key Size</div>
            <select style={select} value={bits} onChange={e => setBits(e.target.value)}>
              {['512','1024','2048'].map(b => (
                <option key={b} value={b}>{b}-bit (RSA-{b})</option>
              ))}
            </select>
          </div>
          <button style={btn()} onClick={keygen} disabled={loading}>
            {loading ? '⏳ Generating primes…' : '🔑 Generate Key Pair'}
          </button>
        </div>
        {error && <div style={{ color: '#fc8181', marginTop: '10px', fontSize: '13px' }}>{error}</div>}
      </div>

      <KeyDisplay keyPair={keyPair} />

      {/* Sign / Verify */}
      {keyPair && (
        <div style={card}>
          <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '14px' }}>② Sign & Verify (SHA-256)</h3>
          <div style={{ marginBottom: '12px' }}>
            <div style={label}>Message to Sign</div>
            <textarea
              style={textarea}
              value={signText}
              onChange={e => setSignText(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
            <button style={btn('#059669')} onClick={sign} disabled={signLoading}>
              {signLoading ? '⏳ Signing…' : '✍️ Sign (Blinded-Adaptive)'}
            </button>
          </div>

          {signResult && (
            <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '8px', padding: '12px', marginBottom: '16px', fontSize: '12px' }}>
              <div style={{ color: '#34d399', fontWeight: 700, marginBottom: '8px' }}>
                ✅ Signed in {signResult.total_time_ms?.toFixed(2)} ms · Strategy: {signResult.strategy_used}
              </div>
              <div style={{ fontFamily: 'monospace', color: '#a0aec0', wordBreak: 'break-all' }}>
                sig = {signResult.signature?.toString().slice(0, 80)}…
              </div>
            </div>
          )}

          {signature && (
            <div style={{ display: 'flex', gap: '12px' }}>
              <button style={btn('#2563eb')} onClick={() => verify(false)} disabled={verifyLoading}>
                {verifyLoading ? '⏳ Verifying…' : '✅ Verify (ML-Adaptive)'}
              </button>
              <button style={btn('#dc2626')} onClick={() => verify(true)} disabled={verifyLoading}>
                🔨 Verify Tampered Signature
              </button>
            </div>
          )}

          {verifyResult && (
            <div style={{ marginTop: '16px', padding: '14px', borderRadius: '8px', background: verifyResult.verified ? 'rgba(52,211,153,0.1)' : 'rgba(252,129,129,0.1)', border: `1px solid ${verifyResult.verified ? '#34d399' : '#fc8181'}` }}>
              <div style={statusBox(verifyResult.verified)}>
                {verifyResult.verified ? '✅ SIGNATURE VALID' : '❌ SIGNATURE INVALID'}
              </div>
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#a0aec0' }}>
                {verifyResult.tampered
                  ? 'Tampered signature correctly rejected — cryptographic integrity confirmed.'
                  : `Verified in ${verifyResult.total_time_ms?.toFixed(2)} ms · Strategy: ${verifyResult.strategy_used}`}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
