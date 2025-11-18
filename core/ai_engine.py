# core/ai_engine.py - KOMPLETNĚ PŘEPSANÉ
"""
AI Engine s vylepšeným porozuměním češtině
Rychlejší, přirozenější, inteligentní cleanup
"""

import openai
from config import Config
import re


class AIEngine:
    """AI engine pro konverzace s Knowledge Base podporou"""
    
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.conversations = {}
        self.model = "gpt-4o-mini"  # ✅ Rychlejší než gpt-4
        
        # ✅ IMPORT KB
        try:
            from database.knowledge_base import get_context_for_query
            self.kb_retriever = get_context_for_query
            print("  ✅ Knowledge Base načtena")
        except Exception as e:
            print(f"  ⚠️  KB import error: {e}")
            self.kb_retriever = None
        
        # ✅ NOVÉ: Integrace pokročilých systémů
        try:
            from services.adaptive_kb import AdaptiveKnowledgeBase
            from services.sentence_detector import SentenceDetector
            from services.response_optimizer import ResponseOptimizer
            from services.conversation_memory import ConversationMemory
            
            self.adaptive_kb = AdaptiveKnowledgeBase()
            self.sentence_detector = SentenceDetector()
            self.response_optimizer = ResponseOptimizer()
            self.conversation_memory = ConversationMemory()
            
            print("  ✅ Pokročilé systémy načteny (Adaptive KB, Sentence Detector, Response Optimizer, Memory)")
        except Exception as e:
            print(f"  ⚠️  Pokročilé systémy error: {e}")
            self.adaptive_kb = None
            self.sentence_detector = None
            self.response_optimizer = None
            self.conversation_memory = None
    
    def _cleanup_czech_input(self, text):
        """
        Vyčistí a normalizuje český vstup z STT
        Opraví časté chyby rozpoznávání a dialekty
        
        VYLEPŠENO: Rozumí více české slangům, dialektům a místním výrazům
        """
        # Lowercase pro porovnání
        cleaned = text.lower().strip()
        
        # ✅ NOVÉ: Větší seznam STT chyb a dialektů
        replacements = {
            # Duplicity
            'slyšíme se dobrý den': 'dobrý den',
            'dobry den dobry den': 'dobrý den',
            'dobrý den dobrý den': 'dobrý den',
            'jo jo': 'jo',
            'ne ne': 'ne',
            'tak tak': 'tak',
            'já já': 'já',
            'mám mám': 'mám',
            'takhle takhle': 'takhle',
            'uvažuji uvažuji': 'uvažuji',
            'jó jó': 'jó',
            
            # Číslice vs. slova
            'nula': '0',
            'zero': '0',
            'jeden': '1',
            'dva': '2',
            'tři': '3',
            'čtyři': '4',
            'pět': '5',
            
            # ✅ NOVÉ: Slang a dialekty
            'jo': 'ano',
            'jojo': 'ano',
            'jó': 'ano',
            'áno': 'ano',
            'no': 'ano',  # moravské "no" = ano
            'nee': 'ne',
            'ne-ne': 'ne',
            'ne prosím': 'ne',
            'vůbec ne': 'ne',
            
            # ✅ NOVÉ: Chyby při vyslovování
            'víte': 'víte',
            'vite': 'víte',
            'vidíte': 'vidíte',
            'vidite': 'vidíte',
            'jak se mate': 'jak se máte',
            'jak se máte': 'jak se máte',
            'nemam': 'nemám',
            'nema': 'nemá',
            'nemate': 'nemáte',
            'nemáte': 'nemáte',
            'mám zájem': 'mám zájem',
            'mamzajem': 'mám zájem',
            
            # ✅ NOVÉ: Běžné spojnice
            'a tak': 'a tak',
            'podívej': 'poslechni',
            'poslechni': 'poslechni',
            'slyš': 'poslechni',
            'počkej': 'chvíli',
            'počkej chvíli': 'chvíli',
            
            # ✅ NOVÉ: Email a URL opravy
            'at': 'at',  # @ symbol
            'tečka': '.',
            'lomítko': '/',
            'dvě lomítka': '//',
            
            # ✅ NOVÉ: Mormální výrazy STT
            'hmm': 'hmm',
            'hm': 'hmm',
            'ehm': 'hmm',
            'aha': 'aha',
            'áha': 'aha',
            'jáha': 'aha',
            'uh': 'hmm',
            'ehm': 'hmm',
            'ej': 'ej',
            'hele': 'hele',
        }
        
        for wrong, correct in replacements.items():
            if wrong in cleaned:
                cleaned = cleaned.replace(wrong, correct)
        
        # Odstraň vícenásobné mezery
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def start_conversation(self, call_sid, system_prompt):
        """Zahájí novou konverzaci"""
        self.conversations[call_sid] = [
            {'role': 'system', 'content': system_prompt}
        ]
        print(f"[AIEngine] Konverzace {call_sid} zahájena")
    
    def _detect_intent(self, text):
        """
        ✅ NOVÉ: Detekuj INTENCI za slovy
        Pomáhá AI lépe rozumět co zákazník opravdu chce
        """
        text_lower = text.lower()
        
        # ✅ INTENCE SLOVA-KLÍČE (co chce)
        intents = {
            'price': ['kolik', 'cena', 'stojí', 'cenu', 'náklady', 'kolik to'],
            'availability': ['kdy', 'termin', 'volne', 'kdy se můžeme sejít'],
            'interest': ['zajímá', 'chci', 'mám zájem', 'bylo by', 'co kdyby'],
            'rejection': ['ne', 'nemám', 'nechci', 'nevím', 'přesunout', 'ne prosím'],
            'confirmation': ['ano', 'jo', 'jo dobře', 'super', 'ok', 'je to'],
            'question': ['jaký', 'jak', 'co', 'proč', 'kde'],
        }
        
        detected = []
        for intent, keywords in intents.items():
            if any(keyword in text_lower for keyword in keywords):
                detected.append(intent)
        
        return detected[0] if detected else 'unknown'
    
    def get_response(self, call_sid, user_message):
        """
        Získá odpověď od AI s automatickým KB kontextem
        VYLEPŠENO: Detekuje INTENCI, lépe rozumí českému kontextu
        NOVÉ: Používá adaptive KB, response optimizer a sentence detection
        """
        if call_sid not in self.conversations:
            raise ValueError(f"Konverzace {call_sid} neexistuje!")
        
        # ✅ VYČISTI ČESKÝ VSTUP
        cleaned_message = self._cleanup_czech_input(user_message)
        print(f"  🧹 Cleaned: '{cleaned_message}'")
        
        # ✅ NOVÉ: DETEKUJ INTENCI
        intent = self._detect_intent(cleaned_message)
        print(f"  🎯 Intent: {intent}")
        
        # ✅ NOVÉ: Zkus najít naučenou odpověď z Adaptive KB
        learned_response = None
        if self.adaptive_kb:
            learned_response = self.adaptive_kb.get_best_response(cleaned_message)
        
        # ✅ NOVÉ: Zkontroluj cache pro rychlejší odpověď
        cached_response = None
        if self.response_optimizer and self.response_optimizer.should_use_cache(cleaned_message, intent):
            cached_response = self.response_optimizer.get_cached_response(
                cleaned_message, 
                {'intent': intent}
            )
        
        # Pokud máme cached nebo learned response, použij ho
        if cached_response:
            return cached_response
        
        if learned_response:
            print(f"  📚 Using learned response")
            # Cache learned response pro další použití
            if self.response_optimizer:
                self.response_optimizer.cache_response(
                    cleaned_message, learned_response, 
                    {'intent': intent}, generation_time=0.1
                )
            return learned_response
        
        # ✅ VYHLEDEJ KONTEXT Z KB (s vědomím INTENCE!)
        kb_context = ""
        if self.kb_retriever:
            try:
                kb_context = self.kb_retriever(cleaned_message)
                if kb_context:
                    print(f"  📚 KB context: {kb_context[:100]}...")
            except Exception as e:
                print(f"  ⚠️  KB retrieval error: {e}")
        
        # ✅ VYTVOŘ ZPRÁVU S KONTEXTEM + INTENCÍ
        if kb_context:
            enhanced_message = f"[INTENT: {intent}]\n{cleaned_message}\n\n[INFO Z DATABÁZE]:\n{kb_context}"
        else:
            enhanced_message = f"[INTENT: {intent}]\n{cleaned_message}"
        
        # Přidej do historie
        self.conversations[call_sid].append({
            'role': 'user',
            'content': enhanced_message
        })
        
        # ✅ ZAVOLEJ OpenAI - SUPER RYCHLÉ PARAMETRY
        try:
            import time
            start_time = time.time()
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=self.conversations[call_sid],
                temperature=0.80,  # ✅ JEŠTĚ méně náhodné (ostřejší porozumění)
                max_tokens=45,     # ✅ JEŠTĚ KRATŠÍ = ostřejší odpovědi
                presence_penalty=0.6,  # ✅ SILNĚJŠÍ zákaz opakování
                frequency_penalty=0.6,  # ✅ SILNĚJŠÍ rozmanitost
                top_p=0.85  # ✅ JEŠTĚ specifičtější výběr
            )
            
            generation_time = time.time() - start_time
            
            ai_reply = response.choices[0].message.content.strip()
            
            # ✅ VYČISTI ODPOVĚĎ (odstraň markdown, emojis apod.)
            ai_reply = self._cleanup_ai_response(ai_reply)
            
            # Ulož odpověď
            self.conversations[call_sid].append({
                'role': 'assistant',
                'content': ai_reply
            })
            
            # ✅ NOVÉ: Cache odpověď pro budoucí použití
            if self.response_optimizer:
                self.response_optimizer.cache_response(
                    cleaned_message, ai_reply,
                    {'intent': intent}, generation_time
                )
            
            return ai_reply
            
        except Exception as e:
            print(f"[AIEngine] OpenAI error: {e}")
            raise
    
    def _cleanup_ai_response(self, text):
        """
        Vyčistí AI odpověď pro TTS
        - Odstranění markdown/emojis
        - Optimalizace pro českou výslovnost
        - Kratší věty
        """
        # Odstraň markdown
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # **bold**
        text = re.sub(r'\*(.+?)\*', r'\1', text)      # *italic*
        
        # Odstraň emojis
        text = re.sub(r'[😀-🙏🌀-🗿🚀-🛿]', '', text)
        
        # Odstraň vícenásobné tečky
        text = re.sub(r'\.{2,}', '.', text)
        
        # ČESKÁ OPTIMALIZACE: Oprav běžné chyby
        replacements = {
            'aha': 'aha',
            'hmm': 'hmm',
            '...': '.',
            '  ': ' ',
        }
        
        for wrong, correct in replacements.items():
            text = text.replace(wrong, correct)
        
        # ROZDĚL DLOUHÉ VĚTY - TTS je lépe čte v kratších kusech
        # Pokud je věta delší než 150 znaků, slož ji lépe
        sentences = text.split('.')
        if len(sentences) > 1 and len(text) > 200:
            # Zkrať odpověď na 2-3 věty max
            text = '. '.join(sentences[:2]).strip() + '.'
        
        # Trim
        text = text.strip()
        
        return text
    
    def end_conversation(self, call_sid, outcome_score: int = 0):
        """
        Ukončí konverzaci a vrátí historii
        NOVÉ: Učí se z konverzace pomocí adaptive KB a conversation memory
        
        Args:
            call_sid: ID hovoru
            outcome_score: Skóre výsledku (0-100) pro learning
        """
        if call_sid not in self.conversations:
            return []
        
        history = self.conversations[call_sid].copy()
        
        # ✅ NOVÉ: Ulož konverzaci pro learning
        if self.adaptive_kb and outcome_score > 0:
            try:
                self.adaptive_kb.learn_from_conversation(call_sid, history, outcome_score)
            except Exception as e:
                print(f"  ⚠️  Adaptive KB learning error: {e}")
        
        if self.conversation_memory and outcome_score > 0:
            try:
                conversation_data = {
                    'history': history,
                    'outcome_score': outcome_score,
                    'start_time': None,  # TODO: track actual times
                    'end_time': None
                }
                self.conversation_memory.store_conversation(call_sid, conversation_data)
            except Exception as e:
                print(f"  ⚠️  Conversation memory error: {e}")
        
        # ⚠️ NESMAŽ JEŠTĚ! Learning system potřebuje přístup
        # del self.conversations[call_sid]
        
        print(f"[AIEngine] Konverzace {call_sid} ukončena ({len(history)} zpráv)")
        return history
    
    def get_conversation_history(self, call_sid):
        """Vrátí historii konverzace"""
        return self.conversations.get(call_sid, [])
    
    def process_speech_fragment(self, call_sid: str, text_fragment: str) -> dict:
        """
        NOVÉ: Zpracuje fragment řeči se sentence detection
        Inteligentně čeká na kompletní věty
        
        Args:
            call_sid: ID hovoru
            text_fragment: Fragment textu ze STT
            
        Returns:
            Dict s akcí: {'action': 'wait'|'process', 'complete_text': str}
        """
        if not self.sentence_detector:
            # Fallback - zpracuj okamžitě
            return {'action': 'process', 'complete_text': text_fragment, 'complete': True}
        
        # Přidej fragment do detektoru
        result = self.sentence_detector.add_fragment(text_fragment)
        
        if result['complete']:
            print(f"  ✅ Sentence complete: '{result['text'][:50]}...'")
            return {
                'action': 'process',
                'complete_text': result['text'],
                'complete': True,
                'detection_type': result.get('detected', 'unknown')
            }
        else:
            print(f"  ⏳ Waiting for complete sentence (buffer: '{result['buffer'][:50]}...')")
            return {
                'action': 'wait',
                'complete_text': '',
                'complete': False,
                'buffer': result.get('buffer', '')
            }
    
    def get_system_stats(self) -> dict:
        """
        NOVÉ: Vrátí statistiky všech pokročilých systémů
        
        Returns:
            Dict se statistikami
        """
        stats = {
            'conversations_active': len(self.conversations),
            'adaptive_kb': None,
            'response_optimizer': None,
            'conversation_memory': None
        }
        
        if self.adaptive_kb:
            stats['adaptive_kb'] = self.adaptive_kb.get_stats()
        
        if self.response_optimizer:
            stats['response_optimizer'] = self.response_optimizer.get_cache_stats()
        
        if self.conversation_memory:
            stats['conversation_memory'] = self.conversation_memory.get_stats()
        
        return stats