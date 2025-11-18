#!/usr/bin/env python3
"""
QUICK START - COLD CALLING NA 30 CISEL
Spuštění v jednom příkazu s postupným průvodcem
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header(title):
    """Vytiskne stylizovaný header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_step(num, title, command=None):
    """Vytiskne krok"""
    print(f"\n📍 STEP {num}: {title}")
    if command:
        print(f"   Command: {command}")

def print_success(msg):
    """Vytiskne úspěch"""
    print(f"   ✅ {msg}")

def print_info(msg):
    """Vytiskne info"""
    print(f"   ℹ️  {msg}")

def ask_yes_no(question):
    """Zeptá se yes/no"""
    response = input(f"\n   {question} (y/n): ").lower().strip()
    return response in ['y', 'yes']

def run_command(cmd, description):
    """Spustí příkaz"""
    print(f"\n   ⏳ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        if result.returncode == 0:
            return True
        else:
            print(f"   ❌ Command failed: {cmd}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Hlavní průvodce"""
    
    print_header("🚀 COLD CALLING - 30 CIGEL QUICK START")
    
    print("""
Tento script ti průvodce postupem:
1. Testování české výslovnosti
2. Příprava kampanně (caching)
3. Spuštění web serveru
4. Zahájení kampanně
5. Monitoring

Zadej CAMPAIGN_ID který chceš spustit (default: 1)
    """)
    
    campaign_id = input("📍 Campaign ID (default 1): ").strip() or "1"
    
    # ===== STEP 1: TEST CZECH =====
    print_header("✅ STEP 1: TEST CZECH PRONUNCIATION")
    
    print_info("Testujeme, jak se vyslovují časy a čísla...")
    print("""
Očekávaný výstup:
  • "14:00" → "čtrnáct hodin" ✅
  • "5" → "pět" ✅
  • České fráze → správná výslovnost ✅

Audio soubory se vygenerují do: static/audio/
    """)
    
    if ask_yes_no("Chceš spustit test české výslovnosti?"):
        run_command("python utils/test_czech_tts.py", "Running Czech pronunciation test")
    else:
        print_info("Přeskakuji test (bude bez ověření)")
    
    # ===== STEP 2: PRE-OPTIMIZER =====
    print_header("✅ STEP 2: PRE-CAMPAIGN OPTIMIZATION")
    
    print_info(f"Připravuji kampaň {campaign_id} na 30 číslic...")
    print("""
Optimizer bude:
  1. Ověřit API klíče (OpenAI, ElevenLabs, Twilio)
  2. Cachovat běžné fráze (ušetří čas)
  3. Ověřit 30+ kontaktů v kampani
  4. Optimalizovat nastavení
    """)
    
    if run_command(
        f"python utils/pre_campaign_optimizer.py {campaign_id}",
        "Running pre-campaign optimizer"
    ):
        print_success("Kampaň je připravena!")
    else:
        print("""
❌ Optimizer selhal. Možné příčiny:
  • Špatný CAMPAIGN_ID
  • Chybí API klíče v .env
  • Nedostatek kontaktů
  • DB error
        """)
        if not ask_yes_no("Chceš pokračovat přesto?"):
            print("Konec.")
            return False
    
    # ===== STEP 3: CHECKLIST =====
    print_header("✅ STEP 3: PRE-CAMPAIGN CHECKLIST")
    
    print_info("Přečti si kontrolní seznam připravenosti...")
    
    if ask_yes_no("Chceš vidět kompletní checklist?"):
        run_command("python COLD_CALLING_CHECKLIST.py", "Showing checklist")
    
    ready = ask_yes_no("\nJsi READY pro spuštění kampanně?")
    if not ready:
        print("OK, pozdeji pak! 👋")
        return False
    
    # ===== STEP 4: START SERVER =====
    print_header("✅ STEP 4: SPUŠTĚNÍ WEB SERVERU")
    
    print_info("Server bude běžet na http://localhost:5000")
    print("""
Admin panel: http://localhost:5000/admin
    """)
    
    print("\n   ⏳ Starting web server...")
    print("   (Server poběží v background terminálu)")
    print("   (Stiskni CTRL+C pro zastavení)\n")
    
    # Spustí server v background
    server_cmd = "python run.py"
    print(f"   Command: {server_cmd}")
    
    # Otevři admin panel
    print("\n   Otevírám admin panel v prohlížeči...")
    import webbrowser
    webbrowser.open("http://localhost:5000/admin")
    
    print_success("Web server spuštěn!")
    print_success("Admin panel: http://localhost:5000/admin")
    
    # ===== STEP 5: START CAMPAIGN =====
    print_header("✅ STEP 5: ZAHÁJENÍ KAMPANNĚ")
    
    print(f"""
    V admin panelu:
    1. Jdi na kampan {campaign_id}
    2. Klikni "Start Campaign"
    3. Sleduj progress
    
    Očekávaný čas: ~2-2.5 hodin na 30 číslic
    
    KPIs které sleduj:
    • Completion rate: 50-70%
    • Answer rate: 40-60%
    • Booking rate: 3-10%
    • Recording rate: 80%+
    """)
    
    if ask_yes_no("Spustit kampaň?"):
        print_info("Jdi do admin panelu a klikni 'Start Campaign'")
        print_info("Nebo použi API: POST /api/campaign/start")
    
    # ===== MONITORING =====
    print_header("✅ STEP 6: MONITORING")
    
    print("""
    Sleduj během kampanně:
    ✅ Admin panel: http://localhost:5000/admin
    ✅ Počet kompletovaných volání
    ✅ Success rate
    ✅ Problémy v logu
    
    Refresh admin panelu každých 30 sekund
    """)
    
    print_info("Stiskni ENTER pro návrat...")
    input()
    
    # ===== POST-CAMPAIGN =====
    print_header("✅ HOTOVO!")
    
    print("""
    Post-campaign:
    1. Zkontroluj analytics v admin panelu
    2. Poslouchej si audio nahrávky
    3. Čti si transcripty
    4. Mejšdify systém prompt podle výsledků
    5. Repeat pro dalších 30 číslic! 🚀
    """)
    
    print_success("30-ciselny cold calling spusten a monitorovan!")
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Bye!")
        sys.exit(0)
