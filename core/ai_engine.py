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
        
        # ✅ MEETING SCHEDULER
        try:
            from services.meeting_scheduler import MeetingScheduler
            self.meeting_scheduler = MeetingScheduler()
            print("  ✅ Meeting Scheduler načten")
        except Exception as e:
            print(f"  ⚠️  Meeting Scheduler import error: {e}")
            self.meeting_scheduler = None
    
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
            'meeting': ['schůzka', 'schůzku', 'sejít', 'setkání', 'potkat', 'můžeme se sejít', 
                       'můžem se vidět', 'setkat', 'osobně', 'prezentace', 'konzultace'],
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
        """
        if call_sid not in self.conversations:
            raise ValueError(f"Konverzace {call_sid} neexistuje!")
        
        # ✅ VYČISTI ČESKÝ VSTUP
        cleaned_message = self._cleanup_czech_input(user_message)
        print(f"  🧹 Cleaned: '{cleaned_message}'")
        
        # ✅ NOVÉ: DETEKUJ INTENCI
        intent = self._detect_intent(cleaned_message)
        print(f"  🎯 Intent: {intent}")
        
        # ✅ MEETING DETECTION - pokud detekujeme požadavek na schůzku
        if intent == 'meeting' and self.meeting_scheduler:
            try:
                meeting_response = self.meeting_scheduler.generate_ai_response(cleaned_message)
                if meeting_response:
                    print(f"  📅 Meeting response generated")
                    # Přidej meeting kontext do zprávy
                    kb_context = f"[MEETING REQUEST DETECTED]\n{meeting_response}"
            except Exception as e:
                print(f"  ⚠️  Meeting scheduler error: {e}")
        
        # ✅ VYHLEDEJ KONTEXT Z KB (s vědomím INTENCE!)
        kb_context = "" if 'kb_context' not in locals() else kb_context
        if self.kb_retriever and not kb_context:
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
            response = openai.chat.completions.create(
                model=self.model,
                messages=self.conversations[call_sid],
                temperature=0.80,  # ✅ JEŠTĚ méně náhodné (ostřejší porozumění)
                max_tokens=45,     # ✅ JEŠTĚ KRATŠÍ = ostřejší odpovědi
                presence_penalty=0.6,  # ✅ SILNĚJŠÍ zákaz opakování
                frequency_penalty=0.6,  # ✅ SILNĚJŠÍ rozmanitost
                top_p=0.85  # ✅ JEŠTĚ specifičtější výběr
            )
            
            ai_reply = response.choices[0].message.content.strip()
            
            # ✅ VYČISTI ODPOVĚĎ (odstraň markdown, emojis apod.)
            ai_reply = self._cleanup_ai_response(ai_reply)
            
            # Ulož odpověď
            self.conversations[call_sid].append({
                'role': 'assistant',
                'content': ai_reply
            })
            
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
    
    def end_conversation(self, call_sid):
        """Ukončí konverzaci a vrátí historii"""
        if call_sid not in self.conversations:
            return []
        
        history = self.conversations[call_sid].copy()
        
        # ⚠️ NESMAŽ JEŠTĚ! Learning system potřebuje přístup
        # del self.conversations[call_sid]
        
        print(f"[AIEngine] Konverzace {call_sid} ukončena ({len(history)} zpráv)")
        return history
    
    def get_conversation_history(self, call_sid):
        """Vrátí historii konverzace"""
        return self.conversations.get(call_sid, [])