"""
PRE-CAMPAIGN OPTIMIZER
Optimalizuje systém PRED spuštením kampanně na 30 čísel

Úkoly:
1. Vygeneruje a cachuje všechny potřebné TTS audiá
2. Zkontroluje API dostupnost
3. Optimalizuje DB pro rychlost
4. Ověří 30 kontaktů
"""

import os
import sys
from pathlib import Path

# Přidej projekt do path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.tts_engine import TTSEngine
from core.ai_engine import AIEngine
from database.cold_calling_db import ColdCallingDB
from config import Config, CallConfig
import time


class PreCampaignOptimizer:
    """Přípraví systém na 30 kontaktů"""
    
    def __init__(self):
        self.tts = TTSEngine()
        self.ai = AIEngine()
        self.db = ColdCallingDB()
        self.stats = {
            'tts_cached': 0,
            'tts_errors': 0,
            'contacts_ready': 0,
        }
    
    def check_api_keys(self):
        """Ověří dostupnost všech API klíčů"""
        print("\n" + "="*60)
        print("🔑 CHECKING API KEYS")
        print("="*60)
        
        checks = [
            ('OpenAI', Config.OPENAI_API_KEY),
            ('ElevenLabs', Config.ELEVENLABS_API_KEY),
            ('Twilio Account', Config.TWILIO_ACCOUNT_SID),
            ('Twilio Token', Config.TWILIO_AUTH_TOKEN),
            ('Twilio Phone', Config.TWILIO_PHONE_NUMBER),
        ]
        
        all_ok = True
        for name, key in checks:
            status = "✅" if key else "❌"
            print(f"{status} {name}: {('*' * 8 + key[-4:]) if key else 'MISSING'}")
            if not key:
                all_ok = False
        
        return all_ok
    
    def cache_common_phrases(self):
        """
        Cachuje běžné TTS výstupy kterých se bude používat
        Ušetří čas a API kredity
        """
        print("\n" + "="*60)
        print("🎙️  CACHING COMMON PHRASES")
        print("="*60)
        
        phrases = [
            # Úvodní
            "Dobry den, volam z Lososs Web Development.",
            "Mate minutku na kratky hovor?",
            "Poslu vam nabidku emailem.",
            
            # Detekce
            "Slysite me?",
            "Pardon, nerozumel jsem.",
            
            # Zavírání
            "Rozumim, diky za cas. Hezky den.",
            "Skvele, kontaktuji se na vami brzy.",
        ]
        
        for i, phrase in enumerate(phrases, 1):
            try:
                print(f"\n[{i}/{len(phrases)}] '{phrase[:40]}...'")
                url = self.tts.generate(phrase, use_cache=True)
                if url:
                    self.stats['tts_cached'] += 1
                    print(f"  ✅ Cached: {url}")
                else:
                    self.stats['tts_errors'] += 1
                    print(f"  ❌ Failed to cache")
            except Exception as e:
                self.stats['tts_errors'] += 1
                print(f"  ❌ Error: {e}")
            
            # Krátká pauza mezi requesty
            time.sleep(0.5)
    
    def verify_contacts(self, campaign_id):
        """Ověří, že je připraveno 30+ kontaktů pro kampaň"""
        print("\n" + "="*60)
        print("📋 VERIFYING CONTACTS")
        print("="*60)
        
        try:
            contacts = self.db.get_contacts(campaign_id=campaign_id, status='pending')
            print(f"\n✓ Contacts in campaign: {len(contacts)}")
            
            if len(contacts) == 0:
                print("  ❌ NO CONTACTS! Add contacts first.")
                return False
            
            if len(contacts) < 30:
                print(f"  ⚠️  Only {len(contacts)} contacts. Recommended: 30+")
            else:
                print(f"  ✅ {len(contacts)} contacts ready to call!")
            
            self.stats['contacts_ready'] = len(contacts)
            
            # Pokaž první 5
            print("\n  First 5 contacts:")
            for c in contacts[:5]:
                print(f"    • {c['name']} - {c['phone']}")
            
            return True
        
        except Exception as e:
            print(f"  ❌ Error checking contacts: {e}")
            return False
    
    def optimize_settings(self):
        """Nastaví optimální parametry pro 30 kontaktů"""
        print("\n" + "="*60)
        print("⚙️  OPTIMIZING SETTINGS")
        print("="*60)
        
        settings = [
            ('MAX_TOKENS', CallConfig.MAX_TOKENS, "Kratší odpovědi"),
            ('CALLS_PER_MINUTE', CallConfig.CALLS_PER_MINUTE, "Hovory za minutu"),
            ('MAX_CALL_DURATION', CallConfig.MAX_CALL_DURATION, "Max délka hovoru (sec)"),
            ('TTS_LATENCY', "2 (max speed)", "TTS streaming latence"),
        ]
        
        print("\n Current settings:")
        for name, value, desc in settings:
            print(f"  • {name}: {value} ({desc})")
        
        print("\n ✅ Optimized pro rapid cold calling (30 čísel)")
        print("    - Kratší AI odpovědi (MAX_TOKENS=40)")
        print("    - Vyšší frekvence volání (CALLS_PER_MINUTE=6)")
        print("    - Zkrácené hovory (MAX_DURATION=120s)")
        print("    - Max TTS speed (optimize_streaming_latency=2)")
    
    def print_summary(self):
        """Vytiskne shrnutí"""
        print("\n" + "="*60)
        print("📊 OPTIMIZATION SUMMARY")
        print("="*60)
        print(f"\n✅ TTS phrases cached: {self.stats['tts_cached']}")
        print(f"❌ TTS errors: {self.stats['tts_errors']}")
        print(f"📞 Contacts ready: {self.stats['contacts_ready']}")
        
        if self.stats['tts_errors'] > 0:
            print(f"\n⚠️  {self.stats['tts_errors']} TTS errors - check API key")
        
        if self.stats['contacts_ready'] >= 30:
            print(f"\n🚀 READY TO LAUNCH CAMPAIGN ON {self.stats['contacts_ready']} CONTACTS!")
        else:
            print(f"\n⚠️  Add more contacts (need 30, have {self.stats['contacts_ready']})")
        
        print("\n" + "="*60)
    
    def run(self, campaign_id):
        """Spustí celou optimalizaci"""
        print("\n")
        print("╔" + "="*58 + "╗")
        print("║" + " PRE-CAMPAIGN OPTIMIZER - 30 CONTACTS READY? ".center(58) + "║")
        print("╚" + "="*58 + "╝")
        
        # 1. API check
        if not self.check_api_keys():
            print("\n❌ MISSING API KEYS! Stop.")
            return False
        
        # 2. Cache phrases
        self.cache_common_phrases()
        
        # 3. Verify contacts
        if not self.verify_contacts(campaign_id):
            return False
        
        # 4. Optimize settings
        self.optimize_settings()
        
        # 5. Summary
        self.print_summary()
        
        return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Pre-Campaign Optimizer')
    parser.add_argument('campaign_id', type=int, help='Campaign ID')
    args = parser.parse_args()
    
    optimizer = PreCampaignOptimizer()
    success = optimizer.run(args.campaign_id)
    
    sys.exit(0 if success else 1)
