# Advanced Learning AI System - Dokumentace

## Přehled

Tento dokument popisuje pokročilý učící se AI systém implementovaný pro lepší a inteligentnější konverzace.

## Implementované funkce

### 1. Změna názvu firmy ✅
- **Změna**: "MoravskeWeby" → "Moravské Weby" (dvě slova)
- **Důvod**: Přirozenější vyslovování AI hlasem
- **Soubor**: `database/knowledge_base.py`

### 2. Adaptivní znalostní báze (Adaptive KB) ✅

**Soubor**: `services/adaptive_kb.py`

Systém, který se učí z každého hovoru a ukládá úspěšné vzorce odpovědí.

**Funkce:**
- ✅ Automatické učení z konverzací
- ✅ Scoring system pro kvalitu odpovědí (0-100)
- ✅ Ukládání nejlepších odpovědí na časté dotazy
- ✅ Fuzzy matching pro podobné dotazy
- ✅ Dynamické aktualizace na základě zkušeností

**Použití:**
```python
from services.adaptive_kb import AdaptiveKnowledgeBase

kb = AdaptiveKnowledgeBase()

# Učení z konverzace
kb.learn_from_conversation(
    call_sid="call_123",
    conversation_history=history,
    outcome_score=85
)

# Získání naučené odpovědi
response = kb.get_best_response("Kolik stojí web?")

# Statistiky
stats = kb.get_stats()
```

**Scoring kritéria:**
- Optimální délka odpovědi (20-100 znaků): +10 bodů
- Obsahuje otázku (engagement): +15 bodů
- Obsahuje konkrétní informace: +10 bodů
- Přirozený konverzační styl: +10 bodů
- Není příliš formální: -15 bodů

### 3. Inteligentní detekce vět (Sentence Detector) ✅

**Soubor**: `services/sentence_detector.py`

Inteligentní systém pro čekání na kompletní věty s timeout mechanismem.

**Funkce:**
- ✅ Buffer pro neúplné věty
- ✅ Detekce kdy uživatel skončil mluvit vs. se zasekl
- ✅ Rozlišení mezi zakoktáním (0.5s) a koncem věty (1.5s)
- ✅ České gramatické kontroly pro kompletnost vět

**Použití:**
```python
from services.sentence_detector import SentenceDetector

detector = SentenceDetector(
    incomplete_timeout=2.0,      # Timeout pro neúplné věty
    pause_threshold=1.5,         # Minimální pauza pro konec věty
    stutter_threshold=0.5        # Max pauza považovaná za zakoktání
)

# Přidání fragmentu
result = detector.add_fragment("Kolik to")
if result['complete']:
    # Věta je kompletní, zpracuj
    process_text(result['text'])
else:
    # Čekej na další fragment
    wait_for_more()

# Kontrola kompletnosti
is_complete = detector.is_sentence_complete("Kolik stojí web?")  # True
```

**Typy pauz:**
- `stutter` - Zakoktání (< 0.5s)
- `thinking` - Přemýšlení (0.5-1.5s)
- `end_of_sentence` - Konec věty (> 1.5s)

### 4. Optimalizace rychlosti odpovědí (Response Optimizer) ✅

**Soubor**: `services/response_optimizer.py`

Systém pro cachování a optimalizaci rychlosti odpovědí.

**Funkce:**
- ✅ Prediktivní cache pro časté dotazy
- ✅ Cache s TTL (Time To Live)
- ✅ Statistiky hit/miss rate
- ✅ Měření času saved
- ✅ Inteligentní rozhodování kdy cachovat

**Použití:**
```python
from services.response_optimizer import ResponseOptimizer

optimizer = ResponseOptimizer(cache_ttl=3600)  # 1 hodina TTL

# Cache odpověď
optimizer.cache_response(
    query="Kolik stojí web?",
    response="Od 8000 Kč",
    context={'intent': 'price'},
    generation_time=0.5
)

# Získej z cache
cached = optimizer.get_cached_response(
    query="Kolik stojí web?",
    context={'intent': 'price'}
)

# Statistiky
stats = optimizer.get_cache_stats()
# {'total_cached': 10, 'hit_rate': '85%', 'total_time_saved': '4.2s'}
```

**Kdy se cachuje:**
- Krátké dotazy (≤5 slov)
- Specifické intenty: price, confirmation, rejection, availability
- Časté dotazy (detekováno automaticky)

### 5. Dlouhodobá paměť konverzací (Conversation Memory) ✅

**Soubor**: `services/conversation_memory.py`

Ukládání a analýza úspěšných vzorců konverzací.

**Funkce:**
- ✅ Ukládání úspěšných vzorců konverzací
- ✅ User profiling (anonymizované)
- ✅ Cross-conversation learning
- ✅ Best practices z úspěšných hovorů
- ✅ Doporučení pro zlepšení

**Použití:**
```python
from services.conversation_memory import ConversationMemory

memory = ConversationMemory()

# Uložení konverzace
conversation_data = {
    'history': conversation_history,
    'outcome_score': 85,
    'outcome': 'interested',
    'summary': 'Zákazník má zájem o web'
}
memory.store_conversation('call_123', conversation_data)

# Získání best practices
best_practices = memory.get_best_practices()
# {
#   'best_openings': [...],
#   'best_closings': [...],
#   'objection_handling': {...},
#   'successful_patterns': [...]
# }

# Doporučení pro zlepšení
recommendations = memory.get_insights_for_improvement()

# Statistiky
stats = memory.get_stats()
```

**Ukládané patterns:**
- Úspěšné openings (top 10)
- Úspěšné closings (top 10)
- Best objection handlers (top 5 pro každý typ)
- Timing insights
- Conversation flow patterns

### 6. Database pro vzorce konverzací (Conversation Patterns DB) ✅

**Soubor**: `database/conversation_patterns.py`

SQLite databáze pro strukturované ukládání vzorců.

**Funkce:**
- ✅ Strukturované ukládání konverzací
- ✅ Tracking patterns a jejich úspěšnosti
- ✅ Ukládání námitek a jejich překonávání
- ✅ Analýza conversation flow
- ✅ Statistiky a reporting

**Použití:**
```python
from database.conversation_patterns import ConversationPatternsDB

db = ConversationPatternsDB()

# Uložení konverzace
conv_id = db.store_conversation('call_123', conversation_data)

# Update pattern stats
db.update_pattern_stats('success_short_smooth', 'outcome', True, 85)

# Získání úspěšných patterns
patterns = db.get_successful_patterns(min_occurrences=3)

# Statistiky objection handling
obj_stats = db.get_objection_success_rate('price')
# {'total': 10, 'overcome': 7, 'success_rate': '70%', 'avg_score': 75}

# Analýza conversation flow
flow = db.analyze_conversation_flow()
```

**Tabulky:**
- `conversations` - Kompletní konverzace
- `conversation_turns` - Jednotlivé tahy
- `patterns` - Naučené patterns
- `objections` - Námitky a jejich handling
- `successful_phrases` - Úspěšné fráze

### 7. Enhanced AI Engine ✅

**Soubor**: `core/ai_engine.py`

Vylepšený AI engine integrující všechny nové systémy.

**Nové funkce:**
- ✅ Integrace Adaptive KB
- ✅ Integrace Sentence Detector
- ✅ Integrace Response Optimizer
- ✅ Integrace Conversation Memory
- ✅ Automatické učení z hovorů
- ✅ Cache responses pro rychlejší odpovědi

**Změny v API:**
```python
from core.ai_engine import AIEngine

engine = AIEngine()

# Start konverzace (beze změn)
engine.start_conversation(call_sid, system_prompt)

# Get response (nově používá cache & learned responses)
response = engine.get_response(call_sid, user_message)

# NOVÉ: Zpracování fragmentů řeči
result = engine.process_speech_fragment(call_sid, text_fragment)
if result['complete']:
    response = engine.get_response(call_sid, result['complete_text'])

# End konverzace (nově s outcome_score pro learning)
history = engine.end_conversation(call_sid, outcome_score=85)

# NOVÉ: Statistiky systémů
stats = engine.get_system_stats()
```

### 8. Enhanced Learning System ✅

**Soubor**: `services/learning_system.py`

Vylepšený learning system s integrací conversation memory.

**Nové funkce:**
- ✅ Integrace s conversation memory
- ✅ Optimalizované prompty na základě best practices
- ✅ Real-time learning z každé konverzace

**Použití:**
```python
from services.learning_system import LearningSystem

learning = LearningSystem()

# Učení z úspěšného hovoru
learning.learn_from_successful_call(call_sid, report)

# Učení z neúspěšného hovoru
learning.learn_from_failed_call(call_sid, report)

# Získání optimalizovaného promptu (nově s conversation memory insights)
prompt = learning.get_optimized_prompt(product, contact_name)
```

## Integrace do existujícího systému

### Automatická inicializace

Všechny nové systémy jsou automaticky inicializovány v `AIEngine.__init__()`:

```python
engine = AIEngine()
# Automaticky načte:
# - AdaptiveKnowledgeBase
# - SentenceDetector  
# - ResponseOptimizer
# - ConversationMemory
```

### Graceful degradation

Pokud nějaký systém selže, zbytek funguje normálně:

```python
# Pokud adaptive_kb není dostupný, použije se standardní KB
# Pokud response_optimizer není dostupný, generuje se vždy nová odpověď
# Pokud sentence_detector není dostupný, zpracuje se okamžitě
```

## Testování

### Spuštění testů

```bash
python3 test_advanced_ai_system.py
```

### Co se testuje

- ✅ SentenceDetector - detekce kompletních vět
- ✅ ResponseOptimizer - cachování a statistiky
- ✅ AdaptiveKB - učení a scoring
- ✅ ConversationMemory - ukládání vzorců
- ✅ ConversationPatternsDB - databázové operace
- ✅ Knowledge Base - aktualizace názvu firmy

### Výsledky testů

Všechny testy úspěšně prošly ✅

## Výhody nového systému

1. **Rychlejší odpovědi** - Cachování snižuje latenci o ~0.5s na cached dotazy
2. **Lepší porozumění** - Čeká na kompletní věty místo fragmentů
3. **Kontinuální zlepšování** - Učí se z každé konverzace
4. **Data-driven optimalizace** - Rozhodnutí na základě skutečných dat
5. **Přirozená konverzace** - Správný název firmy, lepší flow

## Soubory změněny

- ✅ `database/knowledge_base.py` - Změna názvu firmy
- ✅ `core/ai_engine.py` - Integrace nových systémů
- ✅ `services/learning_system.py` - Enhanced learning

## Soubory vytvořeny

- ✅ `services/adaptive_kb.py` - Adaptivní znalostní báze
- ✅ `services/sentence_detector.py` - Detekce vět
- ✅ `services/response_optimizer.py` - Optimalizace rychlosti
- ✅ `services/conversation_memory.py` - Dlouhodobá paměť
- ✅ `database/conversation_patterns.py` - Database pro vzorce
- ✅ `test_advanced_ai_system.py` - Integration testy
- ✅ `.gitignore` - Excluse generovaných dat

## Monitoring a statistiky

### Získání statistik

```python
# AIEngine stats
stats = engine.get_system_stats()
# {
#   'conversations_active': 3,
#   'adaptive_kb': {...},
#   'response_optimizer': {...},
#   'conversation_memory': {...}
# }

# Adaptive KB stats
kb_stats = engine.adaptive_kb.get_stats()
# {
#   'total_patterns': 150,
#   'total_responses': 300,
#   'avg_pattern_score': 78.5,
#   'patterns_over_80': 45
# }

# Response Optimizer stats
opt_stats = engine.response_optimizer.get_cache_stats()
# {
#   'total_cached': 50,
#   'hit_rate': '72%',
#   'total_time_saved': '25.3s'
# }

# Conversation Memory stats
mem_stats = engine.conversation_memory.get_stats()
# {
#   'total_conversations': 200,
#   'success_rate': '65%',
#   'learned_openings': 10,
#   'learned_closings': 10
# }
```

## Bezpečnost

- ✅ CodeQL security scan: 0 alerts
- ✅ Anonymizace user profilů pomocí hash
- ✅ Žádné sensitive data v logu
- ✅ SQLite injection protection (parameterized queries)

## Údržba

### Čištění cache

Response cache se automaticky čistí od expirovaných položek:

```python
optimizer.clear_expired_cache()
```

### Backup databází

Databáze jsou v `data/`:
- `data/conversation_patterns.db` - SQLite databáze
- `data/adaptive_kb/*.json` - JSON soubory
- `data/conversation_memory/*.json` - JSON soubory
- `data/response_cache/*.json` - JSON soubory

Doporučený backup: denní kopírování celé `data/` složky.

## Budoucí vylepšení

Možná rozšíření:
- [ ] Streaming responses (real-time generování)
- [ ] Paralelní zpracování STT + intent detection
- [ ] ML model pro predikci úspěchu konverzace
- [ ] Dashboard pro vizualizaci statistik
- [ ] A/B testing různých přístupů

## Podpora

Pro otázky nebo problémy, viz test soubor `test_advanced_ai_system.py` pro příklady použití.
