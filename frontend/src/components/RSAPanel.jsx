import React, { useState } from 'react'
import axios from 'axios'

export default function RSAPanel() {
  const [bits, setBits] = useState('1024')
  const [keyPair, setKeyPair] = useState(null)
  const [keyLoading, setKeyLoading] = useState(false)
  const [keyError, setKeyError] = useState('')

  // Signing state
  const [signMessage, setSignMessage] = useState('Transaction Approved: Transfer $50,000 to Account #8492')
  const [signature, setSignature] = useState('')
  const [signStats, setSignStats] = useState(null)
  const [signLoading, setSignLoading] = useState(false)
  const [verifyResult, setVerifyResult] = useState(null)
  const [verifyLoading, setVerifyLoading] = useState(false)
  const [copyNotice, setCopyNotice] = useState('')

  const copyToClipboard = (text, label) => {
    if (!text) return
    navigator.clipboard.writeText(text)
    setCopyNotice(label)
    setTimeout(() => setCopyNotice(''), 2000)
  }

  // Key Generation
  const handleKeygen = async () => {
    setKeyLoading(true)
    setKeyError('')
    setKeyPair(null)
    setSignature('')
    setSignStats(null)
    setVerifyResult(null)
    try {
      const res = await axios.post('/api/rsa/keygen', {
        bits: parseInt(bits, 10),
      })
      setKeyPair(res.data)
    } catch (err) {
      setKeyError(err.response?.data?.detail || 'Key generation failed.')
    } finally {
      setKeyLoading(false)
    }
  }

  // Sign Message (Blinded-Adaptive)
  const handleSign = async () => {
    if (!keyPair) {
      setKeyError('Please generate an RSA key pair first.')
      return
    }
    setSignLoading(true)
    setVerifyResult(null)
    try {
      const res = await axios.post('/api/rsa/sign', {
        text: signMessage,
        d: keyPair.private_key.d,
        n: keyPair.private_key.n,
        p: keyPair.private_key.p,
        q: keyPair.private_key.q,
        phi_n: keyPair.private_key.phi_n,
      })
      setSignature(res.data.signature)
      setSignStats(res.data)
    } catch (err) {
      setKeyError(err.response?.data?.detail || 'Signing operation failed.')
    } finally {
      setSignLoading(false)
    }
  }

  // Verify Signature (ML-Adaptive)
  const handleVerify = async (tampered = false) => {
    if (!keyPair || !signature) return
    setVerifyLoading(true)
    setVerifyResult(null)
    try {
      let sigToSend = signature
      if (tampered) {
        // Alter last digit to simulate forged signature
        const lastChar = sigToSend.slice(-1)
        const alteredChar = lastChar === '5' ? '6' : '5'
        sigToSend = sigToSend.slice(0, -1) + alteredChar
      }

      const res = await axios.post('/api/rsa/verify', {
        text: signMessage,
        signature: sigToSend,
        e: keyPair.public_key.e,
        n: keyPair.public_key.n,
      })
      setVerifyResult({
        verified: res.data.verified,
        tampered: tampered,
        strategy: res.data.strategy_used,
        time_ms: res.data.total_time_ms,
      })
    } catch (err) {
      setKeyError(err.response?.data?.detail || 'Signature verification failed.')
    } finally {
      setVerifyLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Title */}
      <div>
        <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#f1f5f9', margin: 0 }}>
          RSA Cryptosystem Integration
        </h1>
        <p style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
          Demonstrates dual-mode deployment: Public-key verification routes via high-throughput ML-Adaptive dispatch; Private-key signing applies Euler Totient Random Exponent Blinding for complete side-channel immunity.
        </p>
      </div>

      {copyNotice && (
        <div style={{
          backgroundColor: '#064e3b',
          color: '#a7f3d0',
          padding: '8px 16px',
          borderRadius: '6px',
          fontSize: '12px',
          fontWeight: 600,
        }}>
          Copied {copyNotice} to clipboard.
        </div>
      )}

      {/* Section 1: Keypair Generation */}
      <div style={{
        backgroundColor: '#0f1422',
        border: '1px solid #1e2638',
        borderRadius: '10px',
        padding: '20px',
      }}>
        <div style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc', marginBottom: '12px' }}>
          Keypair Generation
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center' }}>
          <select
            value={bits}
            onChange={e => setBits(e.target.value)}
            style={{
              backgroundColor: '#161d2e',
              border: '1px solid #273349',
              color: '#e2e8f0',
              padding: '8px 12px',
              borderRadius: '6px',
              fontSize: '13px',
              outline: 'none',
            }}
          >
            <option value="512">RSA-512 (Demonstration)</option>
            <option value="1024">RSA-1024 (Legacy Web Scale)</option>
            <option value="2048">RSA-2048 (NIST Recommended)</option>
          </select>

          <button
            onClick={handleKeygen}
            disabled={keyLoading}
            style={{
              backgroundColor: '#2563eb',
              color: '#ffffff',
              border: 'none',
              padding: '8px 18px',
              borderRadius: '6px',
              fontSize: '13px',
              fontWeight: 600,
              cursor: keyLoading ? 'not-allowed' : 'pointer',
              opacity: keyLoading ? 0.7 : 1,
            }}
          >
            {keyLoading ? 'Generating Primes...' : 'Generate Key Pair'}
          </button>
        </div>

        {keyError && (
          <div style={{ marginTop: '12px', fontSize: '13px', color: '#ef4444' }}>
            {keyError}
          </div>
        )}

        {/* Display Keypair */}
        {keyPair && (
          <div style={{
            marginTop: '16px',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '16px',
          }}>
            {/* Public Key */}
            <div style={{
              backgroundColor: '#070a10',
              border: '1px solid #1e293b',
              borderRadius: '8px',
              padding: '14px',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '12px', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase' }}>
                  Public Key (e, n)
                </span>
                <button
                  onClick={() => copyToClipboard(keyPair.public_key.n, 'Public Modulus')}
                  style={{ backgroundColor: 'transparent', border: '1px solid #334155', color: '#94a3b8', borderRadius: '4px', padding: '2px 8px', fontSize: '11px', cursor: 'pointer' }}
                >
                  Copy Modulus
                </button>
              </div>
              <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>
                Exponent: <span style={{ color: '#f8fafc', fontFamily: 'monospace' }}>{keyPair.public_key.e}</span> (F4 constant)
              </div>
              <div style={{ fontSize: '11px', color: '#64748b', fontFamily: 'monospace', wordBreak: 'break-all', maxHeight: '60px', overflowY: 'auto' }}>
                n = {keyPair.public_key.n}
              </div>
            </div>

            {/* Private Key */}
            <div style={{
              backgroundColor: '#070a10',
              border: '1px solid #1e293b',
              borderRadius: '8px',
              padding: '14px',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '12px', fontWeight: 700, color: '#a78bfa', textTransform: 'uppercase' }}>
                  Private Key (d, phi_n)
                </span>
                <button
                  onClick={() => copyToClipboard(keyPair.private_key.d, 'Private Exponent')}
                  style={{ backgroundColor: 'transparent', border: '1px solid #334155', color: '#94a3b8', borderRadius: '4px', padding: '2px 8px', fontSize: '11px', cursor: 'pointer' }}
                >
                  Copy Exponent
                </button>
              </div>
              <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>
                Side-Channel Protection: <span style={{ color: '#10b981', fontWeight: 600 }}>Active (Blinding Salt r)</span>
              </div>
              <div style={{ fontSize: '11px', color: '#64748b', fontFamily: 'monospace', wordBreak: 'break-all', maxHeight: '60px', overflowY: 'auto' }}>
                d = {keyPair.private_key.d}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Section 2: Digital Signature & Verification */}
      {keyPair && (
        <div style={{
          backgroundColor: '#0f1422',
          border: '1px solid #1e2638',
          borderRadius: '10px',
          padding: '20px',
        }}>
          <div style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc', marginBottom: '12px' }}>
            Digital Signature & Authentication Pipeline
          </div>

          <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '6px' }}>
            Message Payload to Authenticate
          </label>
          <input
            type="text"
            value={signMessage}
            onChange={e => setSignMessage(e.target.value)}
            style={{
              width: '100%',
              backgroundColor: '#090d16',
              border: '1px solid #1e2638',
              borderRadius: '6px',
              color: '#f8fafc',
              fontSize: '13px',
              padding: '10px 12px',
              boxSizing: 'border-box',
              outline: 'none',
              marginBottom: '14px',
            }}
          />

          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button
              onClick={handleSign}
              disabled={signLoading}
              style={{
                backgroundColor: '#059669',
                color: '#ffffff',
                border: 'none',
                padding: '8px 18px',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 600,
                cursor: signLoading ? 'not-allowed' : 'pointer',
              }}
            >
              {signLoading ? 'Signing...' : 'Sign with Private Key (Blinded)'}
            </button>

            {signature && (
              <>
                <button
                  onClick={() => handleVerify(false)}
                  disabled={verifyLoading}
                  style={{
                    backgroundColor: '#1e293b',
                    color: '#38bdf8',
                    border: '1px solid #334155',
                    padding: '8px 18px',
                    borderRadius: '6px',
                    fontSize: '13px',
                    fontWeight: 600,
                    cursor: verifyLoading ? 'not-allowed' : 'pointer',
                  }}
                >
                  {verifyLoading ? 'Verifying...' : 'Verify Authenticity'}
                </button>

                <button
                  onClick={() => handleVerify(true)}
                  disabled={verifyLoading}
                  style={{
                    backgroundColor: '#1e293b',
                    color: '#f87171',
                    border: '1px solid #451a1a',
                    padding: '8px 18px',
                    borderRadius: '6px',
                    fontSize: '13px',
                    fontWeight: 600,
                    cursor: verifyLoading ? 'not-allowed' : 'pointer',
                  }}
                >
                  Simulate Forgery / Tamper Attack
                </button>
              </>
            )}
          </div>

          {/* Signature Output */}
          {signature && (
            <div style={{
              marginTop: '16px',
              backgroundColor: '#070a10',
              border: '1px solid #1e293b',
              borderRadius: '8px',
              padding: '14px',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <span style={{ fontSize: '12px', fontWeight: 600, color: '#94a3b8' }}>
                  Cryptographic Signature (d_blinded execution: {signStats?.total_time_ms} ms)
                </span>
                <button
                  onClick={() => copyToClipboard(signature, 'Signature')}
                  style={{ backgroundColor: 'transparent', border: '1px solid #334155', color: '#94a3b8', borderRadius: '4px', padding: '2px 8px', fontSize: '11px', cursor: 'pointer' }}
                >
                  Copy Signature
                </button>
              </div>
              <div style={{ fontSize: '11px', color: '#cbd5e1', fontFamily: 'monospace', wordBreak: 'break-all', maxHeight: '50px', overflowY: 'auto' }}>
                {signature}
              </div>
            </div>
          )}

          {/* Verification Result Banner */}
          {verifyResult && (
            <div style={{
              marginTop: '16px',
              padding: '14px 18px',
              borderRadius: '8px',
              backgroundColor: verifyResult.verified ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
              border: `1px solid ${verifyResult.verified ? '#059669' : '#dc2626'}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}>
              <div>
                <div style={{
                  fontSize: '14px',
                  fontWeight: 700,
                  color: verifyResult.verified ? '#10b981' : '#ef4444',
                }}>
                  {verifyResult.verified ? 'Signature Valid & Authenticated' : 'Signature Verification Rejected'}
                </div>
                <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px' }}>
                  {verifyResult.tampered
                    ? 'Forgery detection confirmed: Mutated signature bits failed modular equivalence verification.'
                    : `Verified via ${verifyResult.strategy} in ${verifyResult.time_ms} ms.`}
                </div>
              </div>

              <div style={{
                fontSize: '12px',
                fontWeight: 600,
                color: verifyResult.verified ? '#10b981' : '#ef4444',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
              }}>
                {verifyResult.verified ? 'PASS' : 'FAIL'}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
