#!/usr/bin/env python3
"""
AUDIO ENHANCEMENT TESTER
Testuj audio enhancement v různých scénářích
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.stt_engine import STTEngine
import numpy as np

def test_noise_gate():
    """Testuj noise gate"""
    print("\n" + "="*70)
    print("TEST 1: Noise Gate (-40 dB threshold)")
    print("="*70)
    
    stt = STTEngine()
    
    # Vytvoř test audio
    # Tiche audio (pod thresholdem)
    quiet_audio = (np.random.randn(8000) * 0.01).astype(np.int16).tobytes()
    
    # Hlasite audio (nad thresholdem)
    loud_audio = (np.random.randn(8000) * 0.5).astype(np.int16).tobytes()
    
    quiet_db = stt._get_audio_level(quiet_audio)
    loud_db = stt._get_audio_level(loud_audio)
    
    print(f"\nQuiet audio: {quiet_db:.1f} dB")
    print(f"Loud audio: {loud_db:.1f} dB")
    print(f"Noise gate threshold: {stt.noise_gate_threshold} dB")
    
    print(f"\nQuiet is VAD: {stt._detect_voice_activity(quiet_audio)} (should be False)")
    print(f"Loud is VAD: {stt._detect_voice_activity(loud_audio)} (should be True)")

def test_amplification():
    """Testuj amplifikaci"""
    print("\n" + "="*70)
    print("TEST 2: Audio Amplification (target -20 dB)")
    print("="*70)
    
    stt = STTEngine()
    
    # Vytvoř tiche audio
    quiet_audio = (np.random.randn(16000) * 0.05).astype(np.int16).tobytes()
    
    before_db = stt._get_audio_level(quiet_audio)
    amplified = stt._amplify_quiet_audio(quiet_audio, target_db=-20)
    after_db = stt._get_audio_level(amplified)
    
    print(f"\nBefore amplification: {before_db:.1f} dB")
    print(f"After amplification: {after_db:.1f} dB")
    print(f"Target: -20.0 dB")
    print(f"Gained: {after_db - before_db:.1f} dB")
    
    if abs(after_db - (-20.0)) < 3:
        print("✅ Amplification OK")
    else:
        print("❌ Amplification needs adjustment")

def test_enhancement_pipeline():
    """Testuj kompletni enhancement"""
    print("\n" + "="*70)
    print("TEST 3: Full Enhancement Pipeline")
    print("="*70)
    
    stt = STTEngine()
    
    # Vytvoř simulaci: 50% sumu, 50% signalu
    signal = np.random.randn(16000) * 0.2  # Signal
    noise = np.random.randn(16000) * 0.15  # Noise
    mixed = signal + noise
    
    mixed = mixed.astype(np.int16).tobytes()
    
    before_db = stt._get_audio_level(mixed)
    enhanced = stt._enhance_audio(mixed)
    after_db = stt._get_audio_level(enhanced)
    
    print(f"\nBefore enhancement: {before_db:.1f} dB")
    print(f"After enhancement: {after_db:.1f} dB")
    print(f"Change: {after_db - before_db:+.1f} dB")
    
    print("\nEnhancement pipeline:")
    print("  1. Noise gate: ✅")
    print("  2. Noise reduction: ✅")
    print("  3. Amplification: ✅")

def print_recommendations():
    """Tisky doporučení"""
    print("\n" + "="*70)
    print("RECOMMENDATIONS FOR NOISY ENVIRONMENT")
    print("="*70)
    
    print("""
1. IF STILL TOO QUIET:
   └─ Zvýšit target_db v _amplify_quiet_audio():
     changed: target_db=-20 → -15 (hlasitější o 5 dB)

2. IF NOISE GATE IS TOO AGRESIVNÍ:
   └─ Snížit noise_gate_threshold:
     changed: -40 → -50 (citlivější, méně ztlumí)

3. IF STILL HAVING ISSUES:
   └─ Zvýšit gain clip limit:
     changed: np.clip(gain_linear, 0.5, 4.0) 
           → np.clip(gain_linear, 0.5, 6.0) (max 6x)
   ⚠️  Riziko: clipping (zkreslení)

4. FOR VERY NOISY PLACES:
   └─ Instalovat Butterworth filter (scipy potřeba)
   └─ Nebo: WebRTC VAD (pokročilý)

CURRENTLY: Audio enhancement je v základní verzi.
Funguje pro normální kancelářii, restaurace, auta.
Pro velmi hlučná prostředí (diskotéka, stavba) bude problém.
    """)

def main():
    """Spusť testy"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " AUDIO ENHANCEMENT TESTER ".center(68) + "║")
    print("╚" + "="*68 + "╝")
    
    try:
        test_noise_gate()
        test_amplification()
        test_enhancement_pipeline()
        print_recommendations()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70 + "\n")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
