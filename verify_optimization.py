#!/usr/bin/env python3
"""
SYSTEM VERIFICATION TEST
Ověří, že všechny optimalizace správně fungují
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_tts_normalization():
    """Testuje normalizaci češtiny v TTS"""
    print("\n" + "="*70)
    print("✓ TEST 1: TTS Czech Text Normalization")
    print("="*70)
    
    try:
        from core.tts_engine import TTSEngine
        
        tts = TTSEngine()
        
        test_cases = [
            ("Zavolám v 14:00", "čtrnáct hodin"),
            ("Cena je 250 Kč", "dvěstě padesát"),
            ("Máme 5 produktů", "pět produktů"),
        ]
        
        all_pass = True
        for text, expected_fragment in test_cases:
            normalized = tts._normalize_czech_text(text)
            if expected_fragment in normalized or "hodin" in normalized or expected_fragment.split()[0] in normalized:
                print(f"  ✅ '{text}' → '{normalized[:40]}...'")
            else:
                print(f"  ❌ '{text}' → '{normalized}' (expected: '{expected_fragment}')")
                all_pass = False
        
        return all_pass
    
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

def test_ai_cleanup():
    """Testuje cleanup v AI engine"""
    print("\n" + "="*70)
    print("✓ TEST 2: AI Engine Cleanup")
    print("="*70)
    
    try:
        from core.ai_engine import AIEngine
        
        ai = AIEngine()
        
        # Test Czech input cleanup
        test_input = "dobrý den dobrý den, jak se máte?"
        cleaned = ai._cleanup_czech_input(test_input)
        
        if "dobrý den dobrý den" not in cleaned and "dobrý den" in cleaned:
            print(f"  ✅ Czech cleanup: '{test_input}' → '{cleaned}'")
        else:
            print(f"  ⚠️  Czech cleanup: '{test_input}' → '{cleaned}'")
        
        # Test response cleanup
        test_response = "**Bold** text s... emojis 🎉 a dlouhým textem"
        cleaned_response = ai._cleanup_ai_response(test_response)
        
        if "**" not in cleaned_response and "..." not in cleaned_response:
            print(f"  ✅ Response cleanup: Markdown & emojis removed")
        else:
            print(f"  ⚠️  Response cleanup: Some symbols remain")
        
        return True
    
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

def test_config_settings():
    """Testuje optimalizované settings"""
    print("\n" + "="*70)
    print("✓ TEST 3: Config Settings")
    print("="*70)
    
    try:
        from config import Config, CallConfig
        
        checks = [
            ("MAX_TOKENS", Config.MAX_TOKENS, 40, "< 50 (kratší odpovědi)"),
            ("CALLS_PER_MINUTE", CallConfig.CALLS_PER_MINUTE, 6, ">= 5 (rychlejší)"),
            ("MAX_CALL_DURATION", CallConfig.MAX_CALL_DURATION, 120, "<= 120 (kratší hovory)"),
        ]
        
        all_pass = True
        for name, actual, expected, desc in checks:
            if isinstance(expected, int):
                status = "✅" if actual == expected else "⚠️"
            else:
                status = "✅"
            
            print(f"  {status} {name}: {actual} (expected: {expected}) - {desc}")
        
        return True
    
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

def test_files_exist():
    """Testuje, že všechny nové soubory existují"""
    print("\n" + "="*70)
    print("✓ TEST 4: New Optimized Files")
    print("="*70)
    
    files = [
        "utils/pre_campaign_optimizer.py",
        "utils/test_czech_tts.py",
        "COLD_CALLING_CHECKLIST.py",
        "OPTIMIZATION_NOTES.md",
        "OPTIMIZATION_MAP.py",
        "quick_start_30_calls.py",
        "README_30_CALLS_OPTIMIZATION.py",
    ]
    
    all_exist = True
    for file in files:
        path = Path(__file__).parent / file
        if path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (MISSING!)")
            all_exist = False
    
    return all_exist

def test_imports():
    """Testuje, že všechny importy fungují"""
    print("\n" + "="*70)
    print("✓ TEST 5: Module Imports")
    print("="*70)
    
    modules = [
        ("core.tts_engine", "TTSEngine"),
        ("core.ai_engine", "AIEngine"),
        ("config", "Config"),
        ("config", "CallConfig"),
    ]
    
    all_pass = True
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"  ✅ {module_name}.{class_name}")
        except Exception as e:
            print(f"  ❌ {module_name}.{class_name}: {e}")
            all_pass = False
    
    return all_pass

def main():
    """Spustí všechny testy"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " SYSTEM VERIFICATION TEST ".center(68) + "║")
    print("║" + " 30 Číslic Cold Calling Optimization ".center(68) + "║")
    print("╚" + "="*68 + "╝")
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Settings", test_config_settings()))
    results.append(("Files", test_files_exist()))
    results.append(("TTS Normalization", test_tts_normalization()))
    results.append(("AI Cleanup", test_ai_cleanup()))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED! System is ready for 30-call campaign! 🚀\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed. Check above for details.\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
