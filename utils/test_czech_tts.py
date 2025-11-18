"""
CZECH PRONUNCIATION TESTER
Testuje jak systém vyslovuje čísla a české fráze
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.tts_engine import TTSEngine


def test_czech_pronunciation():
    """Testuje českou výslovnost"""
    
    tts = TTSEngine()
    
    print("\n" + "="*70)
    print("🇨🇿 CZECH PRONUNCIATION TEST")
    print("="*70)
    
    test_cases = [
        # Časy - měly by se vyslovit jako slova
        ("Zavoláme vám v 14:00 hodiny.", "Time 14:00"),
        ("Schůzka je v 15:30.", "Time 15:30"),
        ("V 09:00 ráno.", "Time 09:00"),
        
        # Čísla
        ("Máme 5 produktů.", "Number 5"),
        ("Cena je 250 korun.", "Price 250"),
        ("Kod je 12345.", "Code 12345"),
        
        # České výrazy
        ("Dobry den, jak se máte?", "Hello greeting"),
        ("Mate zájem o naši službu?", "Interest check"),
        ("Děkuji za čas. Hezký den.", "Goodbye"),
        ("To je velmi zajímavé.", "Interest expression"),
        ("Rozumím, ale my to řešíme lépe.", "Objection handle"),
        
        # Complex
        ("Volám z firmy Lososs Web Development ze Prahy.", "Full intro"),
        ("Zavolá vám expert v pátek v 14:00 s nabídkou za 5000 korun.", "Complex sentence"),
    ]
    
    print("\n📝 Testing Czech pronunciations:\n")
    
    for i, (text, description) in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] {description}")
        print(f"  📋 Original: {text}")
        print(f"  🔄 Generating audio...", end=" ", flush=True)
        
        try:
            url = tts.generate(text, use_cache=False)
            if url:
                print(f"✅")
                print(f"  🎵 URL: {url}")
            else:
                print(f"❌ No URL returned")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
    
    print("="*70)
    print("✅ Test complete. Check the generated audio files.")
    print("\n💡 Tips for better pronunciation:")
    print("  • Use simple Czech words, avoid abbreviations")
    print("  • Write numbers as words: 5 → pět")
    print("  • Times: 14:30 → čtrnáct hodin třicet")
    print("  • Short sentences work better than long ones")
    print("="*70 + "\n")


if __name__ == '__main__':
    test_czech_pronunciation()
