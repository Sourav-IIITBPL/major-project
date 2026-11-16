"""
Test Suite for RSA Pipeline (Enhancement 4)
=============================================
Verifies correctness of keygen, encrypt, decrypt, sign, verify
across 512-bit, 1024-bit, and 2048-bit RSA key lengths.

Run:
    python crypto_pipeline/test_rsa_pipeline.py
"""

import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import time
import secrets
from crypto_pipeline.rsa_pipeline import RSAPipeline


def test_rsa(bits: int):
    print(f"\n{'='*65}")
    print(f"  RSA-{bits} Full Lifecycle Test")
    print(f"{'='*65}")

    # 1. Key Generation
    pair = RSAPipeline.keygen(bits=bits)
    pub, priv = pair.public, pair.private
    n = pub.n

    # 2. Encrypt / Decrypt
    message = secrets.randbelow(n - 2) + 1
    print(f"\n[Encrypt/Decrypt]")
    print(f"  Original message : ...{hex(message)[-12:]}")

    enc = RSAPipeline.encrypt(message, pub)
    print(f"  Ciphertext       : ...{hex(enc['ciphertext'])[-12:]}")
    print(f"  Strategy (enc)   : {enc['strategy_used']}")
    print(f"  Encrypt time     : {enc['total_time_ms']:.2f} ms")

    dec = RSAPipeline.decrypt(enc["ciphertext"], priv)
    print(f"  Decrypted        : ...{hex(dec['plaintext'])[-12:]}")
    print(f"  Strategy (dec)   : {dec['strategy_used']}")
    print(f"  Decrypt time     : {dec['total_time_ms']:.2f} ms")
    assert dec["plaintext"] == message, "❌ Decrypt failed!"
    print(f"  ✅ Encrypt / Decrypt PASSED")

    # 3. Sign / Verify (integer)
    msg_int = secrets.randbelow(n - 2) + 1
    print(f"\n[Sign/Verify – Integer]")
    sig_res = RSAPipeline.sign(msg_int, priv)
    print(f"  Signature        : ...{hex(sig_res['signature'])[-12:]}")
    print(f"  Strategy (sign)  : {sig_res['strategy_used']}")
    print(f"  Sign time        : {sig_res['total_time_ms']:.2f} ms")

    ver_res = RSAPipeline.verify(sig_res["signature"], msg_int, pub)
    print(f"  Verified         : {ver_res['verified']}")
    print(f"  Strategy (verify): {ver_res['strategy_used']}")
    print(f"  Verify time      : {ver_res['total_time_ms']:.2f} ms")
    assert ver_res["verified"], "❌ Verify failed!"
    print(f"  ✅ Sign / Verify PASSED")

    # 4. Sign / Verify (text via SHA-256)
    text = f"Hello from RSA-{bits}: Sourav & Eric — Major Project IIIT Bhopal"
    print(f"\n[Sign/Verify – Text  SHA-256]")
    print(f"  Text             : \"{text}\"")
    sign_text_res = RSAPipeline.sign_text(text, priv)
    print(f"  Signature        : ...{hex(sign_text_res['signature'])[-12:]}")
    print(f"  Sign time        : {sign_text_res['total_time_ms']:.2f} ms")

    ver_text_res = RSAPipeline.verify_text(text, sign_text_res["signature"], pub)
    print(f"  Verified         : {ver_text_res['verified']}")
    print(f"  Verify time      : {ver_text_res['total_time_ms']:.2f} ms")
    assert ver_text_res["verified"], "❌ Text verify failed!"
    print(f"  ✅ Text Sign / Verify PASSED")

    # 5. Tampered signature must FAIL
    bad_sig = sign_text_res["signature"] ^ 0xFF
    bad_ver = RSAPipeline.verify_text(text, bad_sig, pub)
    assert not bad_ver["verified"], "❌ Tampered sig passed – security failure!"
    print(f"\n  ✅ Tampered-signature rejection PASSED")

    return True


if __name__ == "__main__":
    all_passed = True
    for bit_len in [512, 1024, 2048]:
        try:
            test_rsa(bit_len)
        except AssertionError as e:
            print(f"\n  ❌ {e}")
            all_passed = False

    print("\n" + "="*65)
    if all_passed:
        print("  🎉 ALL RSA PIPELINE TESTS PASSED!")
    else:
        print("  ❌ SOME TESTS FAILED — see above.")
    print("="*65)
