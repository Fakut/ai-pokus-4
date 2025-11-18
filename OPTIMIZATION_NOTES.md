## 🚀 OPTIMALIZACE PRO COLD CALLING NA 30 ČÍSEL

Upravil jsem tvůj systém pro měřetí 30 čísel s fokusem na:
- **Správná českou vyslovnost** (zejména čísla a časy)
- **Maximální rychlost** (kratší odpovědi, vyšší frekvence)
- **Přirozenost** (kratší věty, lepší cleanup)

---

## 📊 CO SE ZMĚNILO

### 1. **TTSEngine** (`core/tts_engine.py`) ✅
**Nový feature: Normalizace českého textu**
```python
# Automaticky konvertuje:
"Volám v 14:00"  →  "Volám v čtrnáct hodin"
"Máme 5 produktů"  →  "Máme pět produktů"
"Cena: 250 Kč"  →  "Cena: dvěstě padesát"
```

**Optimalizace pro SPEED:**
- `optimize_streaming_latency = 2` (z 3) → nejrychlejší
- `stability = 0.3` (z 0.5) → méně detailů = rychlejší
- `use_speaker_boost = False` → vypnuto = rychlejší

### 2. **AIEngine** (`core/ai_engine.py`) ✅
**Lepší cleanup českého vstupu**
- Opraví "dobry den dobry den" → "dobry den"
- Odstraní vícenásobné mezery
- Zkrátí dlouhé věty (max 2-3 věty)

**Kratší odpovědi:**
- `MAX_TOKENS = 40` (z 60) → kratší = rychlejší TTS

### 3. **Settings** (`config/settings.py`) ✅
```python
# Zvýšeno pro 30 čísel:
CALLS_PER_MINUTE = 6        # z 4 → více volání
MAX_CALL_DURATION = 120     # z 180 → kratší hovory
MAX_RETRIES = 1             # z 2 → méně retries

# Vypnuto pro performance:
DEBUG = False               # Snižuje overhead
```

### 4. **Prompty** (`config/prompts.py`) ✅
Zjednodušené, kratší, jasnější pro TTS:
```
SALES_TEMPLATE - nyní je **2x kratší a jasnější**
```

---

## 🧪 TESTOVÁNÍ ČESKÉ VYSLOVNOSTI

```bash
# Ověř, jak se vyslovují časy a čísla:
python utils/test_czech_tts.py
```

Otestuje:
- ✅ Časy: "14:00" → "čtrnáct hodin"
- ✅ Čísla: "5" → "pět"
- ✅ Ceny: "250" → "dvěstě padesát"
- ✅ České fráze

---

## 🎯 PRE-CAMPAIGN OPTIMIZER

**NEJDŮLEŽITĚJŠÍ SCRIPT** - spusť ho PŘED kampanní:

```bash
# Příprava na 30 číslic:
python utils/pre_campaign_optimizer.py <CAMPAIGN_ID>
```

Co to dělá:
1. ✅ Ověří API klíče (OpenAI, ElevenLabs, Twilio)
2. ✅ Cachuje běžné fráze (ušetří čas + kredity)
3. ✅ Ověří, že máš 30+ kontaktů
4. ✅ Optimalizuje nastavení

---

## 📋 CHECKLIST - PŘIPRAVENO NA 30 ČÍSEL?

```bash
# Kompletní checklist:
python COLD_CALLING_CHECKLIST.py
```

Bude ti ukázat:
- ✅ Co je připraveno
- ❌ Co chybí
- 💡 Jak to opravit
- 🎯 Co očekávat (timing, success rate)

---

## 🚀 SPUŠTĚNÍ KAMPANNĚ

```bash
# 1. Příprava (NUTNÉ):
python utils/pre_campaign_optimizer.py 1

# 2. Start web serveru:
python run.py

# 3. Jdi na admin:
http://localhost:5000/admin

# 4. Spusť kampaň na 30 čísel
# - Klikni "Start Campaign"
# - Sleduj progress v admin panelu
# - Očekávaný čas: ~2-2.5 hodin
```

---

## ⚡ OPTIMALIZAČNÍ TIPY

### Jestli je **STÁLE POMALÉ**:
```python
# config/settings.py
CALLS_PER_MINUTE = 8  # zvýšit z 6 (max ~10)
MAX_TOKENS = 30       # snížit z 40 (kratší odpovědi)
```

### Jestli je **STÁLE ŠPATNÁ VYSLOVNOST**:
```python
# core/tts_engine.py - přidej do _normalize_czech_text():
specific_replacements = {
    'tvoje specialni frazeologie': 'správná výslovnost'
}
```

### Jestli je **MÁLO ÚSPĚŠNÝCH VOLÁNÍ**:
- Vylepši system prompt (zkrač ho, udělej jasněj)
- Přidej nové objections do Knowledge Base
- Zkontroluj na jaké časy nejlépe reagují (analytics)

---

## 📊 EXPECTED RESULTS - 30 VOLÁNÍ

Po spuštění kampanně na 30 čísel bys měl vidět:

| Metrika | Expected | Dobrý sign |
|---------|----------|-----------|
| **Completion** | 50-70% | Hovory byla dokončena |
| **Answer** | 40-60% | Lidé zvedli telefon |
| **Booking** | 3-10% | Aspoň někdo si vezme schůzku |
| **Recording** | 80%+ | Máš záznam |
| **Čas** | ~120 min | Všechny za 2 hodiny |

---

## 🔧 SOUBORY KTERÉ SE ZMĚNILY

```
✅ core/tts_engine.py           - Nové: _normalize_czech_text()
✅ core/ai_engine.py            - Vylepšený cleanup
✅ config/settings.py           - Optimalizace pro 30 čísel
✅ config/prompts.py            - Kratší, jasnější prompty
✨ utils/pre_campaign_optimizer.py  - NOVÝ: Příprava kampanně
✨ utils/test_czech_tts.py      - NOVÝ: Test česka
✨ COLD_CALLING_CHECKLIST.py    - NOVÝ: Kompletní checklist
```

---

## 🎉 TL;DR - QUICK START

```bash
# 1. Kontrola české výslovnosti:
python utils/test_czech_tts.py

# 2. Příprava (cachování běžných frází):
python utils/pre_campaign_optimizer.py 1

# 3. Spuštění kampanně:
python run.py
# → http://localhost:5000/admin → Start Campaign

# 4. Sleduj progress a slušuj audio 🎧

# 5. Analýza výsledků v admin panelu
```

---

## 💡 COMMON ISSUES

| Problém | Řešení |
|---------|--------|
| "14:00" se vyslovuje jako "jeden čtyři" | ✅ Už opraveno v TTSEngine |
| Hovory jsou pomalé | Zvýšit CALLS_PER_MINUTE nebo snížit MAX_TOKENS |
| AI nemluvé česky | ✅ Už opraveno v AIEngine cleanup |
| Příliš mnoho API errů | Snižuj CALLS_PER_MINUTE, kontroluj kredity |
| Cache miss - TTS volá API pořád | Spusť pre_campaign_optimizer.py |

---

## 🎯 SUMMARY

Tvůj systém je **PŘIPRAVEN NA 30 VOLÁNÍ!** 

Klíčové optimalizace:
1. ✅ Správná česká vyslovnost (časy, čísla)
2. ✅ Vyšší rychlost (6 volání/minutu)
3. ✅ Kratší, přirozenější odpovědi
4. ✅ Pre-kampanní příprava (cache, API check)
5. ✅ Monitoring & checklist

**GO GO GO!** 🚀

---

*Vytvořeno: 2025-11-12*
*Optimalizace pro: 30 číslic cold calling s českou podporou*
