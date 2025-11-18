"""
COLD CALLING CHECKLIST - 30 CISEL
Ověřovací seznam připravenosti na masivní cold calling kampaň
"""

CHECKLIST = """

╔══════════════════════════════════════════════════════════════════════╗
║          COLD CALLING CHECKLIST - PŘIPRAVENO NA 30 ČÍSEL?          ║
╚══════════════════════════════════════════════════════════════════════╝

📋 PRE-CAMPAIGN CHECKS
─────────────────────────────────────────────────────────────────────

API CREDENTIALS:
  ☐ OPENAI_API_KEY je nastavený (.env)
  ☐ ELEVENLABS_API_KEY je nastavený (.env)
  ☐ TWILIO_ACCOUNT_SID je nastavený (.env)
  ☐ TWILIO_AUTH_TOKEN je nastavený (.env)
  ☐ TWILIO_PHONE_NUMBER je nastavený (.env)
  
  → Spuštěnív: python utils/pre_campaign_optimizer.py <CAMPAIGN_ID>

DATABÁZE:
  ☐ Máš 30+ kontaktů v kampani (data/calls.db)
  ☐ Kontakty jsou ve statusu "pending"
  ☐ Kontakty obsahují: name, phone, company (optional)
  
  → Kontrola: v admin panelu na http://localhost:5000/admin


CODE OPTIMIZATION:
  ✅ TTSEngine:
     - Normalizace číslic (14:00 → čtrnáct hodin)
     - Česká výslovnost
     - Streaming latency = 2 (max speed)
     - Cache enabled
  
  ✅ AIEngine:
     - MAX_TOKENS = 40 (kratší odpovědi)
     - Cleanup českého STT vstupu
     - Temperature = 0.9 (více přirozené)
  
  ✅ Settings:
     - CALLS_PER_MINUTE = 6 (6 hovorů/minutu)
     - MAX_CALL_DURATION = 120s
     - RETRY_FAILED = True
     - MAX_RETRIES = 1


📱 TESTOVÁNÍ PŘED LAUNCH
─────────────────────────────────────────────────────────────────────

Czech Pronunciation:
  ☐ Spusť test České výslovnosti:
    → python utils/test_czech_tts.py
  
  ☐ Zkontroluj vygenerované audio soubory:
    → static/audio/ 
  
  ☐ Ověř:
    • Časy: "14:00" se vyslovuje jako "čtrnáct hodin"
    • Čísla: "5" se vyslovuje jako "pět"
    • České fráze: bez chyb a přirozené

Test Volání (1-2 čísla):
  ☐ Zavolej 1 testovací číslo přes admin panel
  ☐ Zkontroluj transcript - je srozumitelný?
  ☐ Zkontroluj analytics - Call > Transcript tab
  ☐ Poslouchej audio - správná rytmika a intonace?


🚀 LAUNCH PREPARATION (DAY BEFORE)
─────────────────────────────────────────────────────────────────────

1. FINAL CHECKS:
   ☐ API rate limits: máš dostatek kreditu na OpenAI?
   ☐ API rate limits: máš dostatek kreditu na ElevenLabs?
   ☐ Twilio account: zaplaceno? SMS capable?
   ☐ Database: backupu stará verze? (data/calls.db.backup)
   ☐ Server: spuštěn a http://localhost:5000 dostupný?

2. CACHE PREPARATION:
   ☐ Spusť pre-campaign optimizer:
     → python utils/pre_campaign_optimizer.py <CAMPAIGN_ID>
   
   ☐ Ověř cachované audio:
     → static/audio/ by měl obsahovat ~10+ mp3 souborů

3. MONITORING SETUP:
   ☐ Připrav monitoring:
     → http://localhost:5000/admin/campaign/<CAMPAIGN_ID>
   ☐ Měj otevřenou admin dashboard během kampanně
   ☐ Máš kontakt na support (v případě selhání)?

4. CAMPAIGN PARAMETERS:
   ☐ Ověř kampaň nastavení:
     • Name: jasný identifikátor
     • System prompt: je optimalizován pro TTS?
     • Contacts: všechny mají phone?
     • Status: všechny jsou "pending"?


🎯 BĚHEM KAMPANNĚ (REAL-TIME MONITORING)
─────────────────────────────────────────────────────────────────────

Monitoruj každých 5 minut:
  ☐ Admin dashboard: http://localhost:5000/admin
  ☐ Počet kompletovaných volání
  ☐ Success rate
  ☐ Problémy v logu (server console)

Očekávaný čas:
  • 30 volání × 2.5 min/průměr = ~75 minut
  • Počítej s 10s pauzou mezi hovory
  • Celkem: ~2-2.5 hodiny

Pokud vidíš problémy:
  ☐ Chyba "503 Service Unavailable": počkej 30s a zkus znovu
  ☐ Chyba v TTS: zkontroluj ElevenLabs API status
  ☐ Chyba v STT: zkontroluj audio kvalitu
  ☐ Chyba v AI: zkontroluj OpenAI API status


📊 EXPECTED RESULTS
─────────────────────────────────────────────────────────────────────

Target KPIs za 30 volání:
  • Completion rate: 50-70% (někdo zvedá, někdo ne)
  • Answer rate: 40-60% (někdo se na rozhovoru zúčastní)
  • Booking rate: 3-10% (někdo si vezme schůzku)
  • Record rate: 80%+ (měli by být nahrávky)

Analýza:
  ☐ Zkontroluj nahrávky v admin > campaign > detail
  ☐ Přečti si transcripty (AI dělá smysl?)
  ☐ Slušuj audio (vypadá přirozeně?)
  ☐ Zkontroluj learning system: data/learning/


✅ POST-CAMPAIGN
─────────────────────────────────────────────────────────────────────

1. BACKUP:
   ☐ Zálohuj data:
     → cp data/calls.db data/calls.db.backup.after_30

2. ANALYSIS:
   ☐ Exportuj results z admin panelu
   ☐ Analyzuj na jaké čísla nejlépe reagují
   ☐ Vylepši product pitch na základě feedbacku
   ☐ Zkontroluj failed calls a zjisti proč

3. OPTIMIZATION:
   ☐ Updatuj system prompt na základě učení
   ☐ Přidej nové objections do KB
   ☐ Vylepši seznam kontaktů (target audience)
   ☐ Zvýš CALLS_PER_MINUTE na 8-10 pokud dopadlo dobře


💡 COMMON ISSUES & FIXES
─────────────────────────────────────────────────────────────────────

Problém: "14:00" se vyslovuje jako "jeden čtyři nula nula"
  Řešení: ✅ Už opraveno v new TTSEngine._normalize_czech_text()
  Tip: Zavolej utils/test_czech_tts.py pro test

Problém: Hovory jsou příliš pomalé
  Řešení: Zvýšen CALLS_PER_MINUTE z 4 → 6
  Řešení: Snížen MAX_TOKENS z 60 → 40
  Řešení: Nastaven streaming_latency na 2 (max)

Problém: AI nedovede česky
  Řešení: ✅ Přidán cleanup_czech_input v AIEngine
  Řešení: ✅ Zkráceni prompty - jsou jasnější

Problém: Cache miss - TTS volá API na každý call
  Řešení: ✅ Spusť pre_campaign_optimizer.py
  Řešení: ✅ Cache_common_phrases() cachuje běžné fráze

Problém: Příliš mnoho API errů
  Řešení: Znižuj CALLS_PER_MINUTE (max 10)
  Řešení: Zduplikuj API kredity
  Řešení: Přidej retry logic (je tam: MAX_RETRIES=1)


🎯 READING THIS MEANS YOU'RE READY!

Pokud máš všechny ☐ zaškrtnuté → POKRAČUJ S KLIDNOU DUŠÍ! 🚀

Spuštění kampanně:
  1. python utils/pre_campaign_optimizer.py <CAMPAIGN_ID>
  2. Jdi na http://localhost:5000/admin
  3. Klikni "Start Campaign"
  4. Sleduj progress

VÍTĚZSTVÍ = 30+ volání za 2-3 hodiny bez manuální práce! 🎉

═══════════════════════════════════════════════════════════════════════
"""

if __name__ == '__main__':
    print(CHECKLIST)
