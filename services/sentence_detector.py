# services/sentence_detector.py
"""
Inteligentní detekce kompletních vět s timeout mechanismem
Rozlišuje mezi zakoktáním a koncem věty
"""

import time
from typing import Optional, Dict
from datetime import datetime


class SentenceDetector:
    """
    Detekuje kdy uživatel dokončil myšlenku vs. se zasekl
    Používá buffer pro neúplné věty s timeout mechanismem
    """
    
    def __init__(self, 
                 incomplete_timeout: float = 2.0,
                 pause_threshold: float = 1.5,
                 stutter_threshold: float = 0.5):
        """
        Args:
            incomplete_timeout: Čas v sekundách pro timeout neúplné věty
            pause_threshold: Minimální pauza pro konec věty (sekundy)
            stutter_threshold: Max pauza považovaná za zakoktání (sekundy)
        """
        self.incomplete_timeout = incomplete_timeout
        self.pause_threshold = pause_threshold
        self.stutter_threshold = stutter_threshold
        
        self.buffer = ""
        self.last_input_time = None
        self.sentence_complete = False
    
    def add_fragment(self, text_fragment: str) -> Dict[str, any]:
        """
        Přidá fragment textu do bufferu a rozhodne co dělat
        
        Args:
            text_fragment: Nový fragment textu ze STT
            
        Returns:
            Dict s: {
                'complete': bool - je věta kompletní?,
                'text': str - kompletní text (pokud complete=True),
                'action': str - 'wait', 'process', 'timeout'
            }
        """
        current_time = time.time()
        
        # První fragment
        if self.last_input_time is None:
            self.buffer = text_fragment
            self.last_input_time = current_time
            return {
                'complete': False,
                'text': '',
                'action': 'wait',
                'buffer': self.buffer
            }
        
        # Vypočítej pauzu od posledního inputu
        pause_duration = current_time - self.last_input_time
        
        # Přidej fragment do bufferu
        if text_fragment.strip():
            # Pokud je pauza kratší než stutter_threshold, je to asi zakoktání
            if pause_duration < self.stutter_threshold:
                self.buffer += " " + text_fragment
                self.last_input_time = current_time
                return {
                    'complete': False,
                    'text': '',
                    'action': 'wait',
                    'buffer': self.buffer,
                    'detected': 'stutter'
                }
            
            # Pokud je pauza mezi stutter a pause threshold, čekáme
            elif pause_duration < self.pause_threshold:
                self.buffer += " " + text_fragment
                self.last_input_time = current_time
                return {
                    'complete': False,
                    'text': '',
                    'action': 'wait',
                    'buffer': self.buffer,
                    'detected': 'continuing'
                }
            
            # Pauza je dostatečná - uživatel dokončil myšlenku
            else:
                # Předchozí buffer byl kompletní věta
                complete_text = self.buffer.strip()
                
                # Reset pro nový fragment
                self.buffer = text_fragment
                self.last_input_time = current_time
                
                return {
                    'complete': True,
                    'text': complete_text,
                    'action': 'process',
                    'buffer': self.buffer,
                    'detected': 'complete_sentence'
                }
        
        # Prázdný fragment - kontrola timeoutu
        else:
            if pause_duration >= self.incomplete_timeout:
                # Timeout - zpracuj co máme
                complete_text = self.buffer.strip()
                self.buffer = ""
                self.last_input_time = None
                
                if complete_text:
                    return {
                        'complete': True,
                        'text': complete_text,
                        'action': 'timeout',
                        'buffer': '',
                        'detected': 'timeout'
                    }
            
            # Ještě čekáme
            return {
                'complete': False,
                'text': '',
                'action': 'wait',
                'buffer': self.buffer
            }
    
    def is_sentence_complete(self, text: str) -> bool:
        """
        Kontroluje zda je věta gramaticky kompletní
        
        Args:
            text: Text k analýze
            
        Returns:
            True pokud vypadá jako kompletní věta
        """
        text = text.strip().lower()
        
        if not text:
            return False
        
        # Má koncovou interpunkci?
        if text[-1] in '.?!':
            return True
        
        # Obsahuje sloveso a má alespoň 3 slova? (základní heuristika pro češtinu)
        words = text.split()
        if len(words) < 3:
            return False
        
        # České slovesné koncovky
        verb_endings = ['ám', 'áš', 'á', 'áme', 'áte', 'ají',
                       'ím', 'íš', 'í', 'íme', 'íte', 'í',
                       'uju', 'uješ', 'uje', 'ujeme', 'ujete', 'ují',
                       'oval', 'ovala', 'ovali',
                       'bych', 'bys', 'by', 'bychom', 'byste']
        
        has_verb = any(
            any(word.endswith(ending) for ending in verb_endings)
            for word in words
        )
        
        # Běžné kompletní otázky
        question_starts = ['kolik', 'kdy', 'kde', 'jak', 'co', 'proč', 'kdo']
        is_question = any(text.startswith(q) for q in question_starts)
        
        if is_question and len(words) >= 2:
            return True
        
        return has_verb
    
    def detect_pause_type(self, pause_duration: float) -> str:
        """
        Detekuje typ pauzy
        
        Args:
            pause_duration: Délka pauzy v sekundách
            
        Returns:
            'stutter', 'thinking', 'end_of_sentence'
        """
        if pause_duration < self.stutter_threshold:
            return 'stutter'  # Zakoktání
        elif pause_duration < self.pause_threshold:
            return 'thinking'  # Přemýšlí nad dalším slovem
        else:
            return 'end_of_sentence'  # Dokončil větu
    
    def should_wait_for_more(self) -> bool:
        """
        Rozhodne zda čekat na další input nebo zpracovat buffer
        
        Returns:
            True pokud by měl systém čekat
        """
        if not self.buffer:
            return False
        
        # Zkontroluj čas
        if self.last_input_time is None:
            return False
        
        current_time = time.time()
        time_since_last = current_time - self.last_input_time
        
        # Pokud timeout vypršel, nezkat
        if time_since_last >= self.incomplete_timeout:
            return False
        
        # Pokud věta vypadá nekompletně, čekej
        if not self.is_sentence_complete(self.buffer):
            return True
        
        return False
    
    def get_buffer(self) -> str:
        """Vrátí aktuální buffer"""
        return self.buffer
    
    def clear_buffer(self):
        """Vyčistí buffer"""
        self.buffer = ""
        self.last_input_time = None
        self.sentence_complete = False
    
    def get_status(self) -> Dict:
        """Vrátí aktuální stav detektoru"""
        current_time = time.time()
        time_since_last = None
        
        if self.last_input_time:
            time_since_last = current_time - self.last_input_time
        
        return {
            'buffer': self.buffer,
            'buffer_length': len(self.buffer),
            'time_since_last_input': time_since_last,
            'should_wait': self.should_wait_for_more(),
            'appears_complete': self.is_sentence_complete(self.buffer) if self.buffer else False
        }
    
    def analyze_speech_pattern(self, text_fragments: list) -> Dict:
        """
        Analyzuje pattern mluvy z fragmentů
        Detekuje zda uživatel mluví plynule, zakoktává se, nebo má dlouhé pauzy
        
        Args:
            text_fragments: List fragmentů s timestamps
            
        Returns:
            Dict s analýzou patternu
        """
        if len(text_fragments) < 2:
            return {'pattern': 'insufficient_data'}
        
        # Vypočítej pauzy mezi fragmenty
        pauses = []
        for i in range(1, len(text_fragments)):
            if 'timestamp' in text_fragments[i] and 'timestamp' in text_fragments[i-1]:
                pause = text_fragments[i]['timestamp'] - text_fragments[i-1]['timestamp']
                pauses.append(pause)
        
        if not pauses:
            return {'pattern': 'no_timing_data'}
        
        avg_pause = sum(pauses) / len(pauses)
        
        # Kategorizuj pattern
        if avg_pause < 0.5:
            pattern = 'fluent'  # Plynulá řeč
        elif avg_pause < 1.5:
            pattern = 'normal'  # Normální tempo
        elif avg_pause < 3.0:
            pattern = 'hesitant'  # Váhavý, přemýšlí
        else:
            pattern = 'very_slow'  # Velmi pomalý
        
        # Detekuj zakoktávání (hodně krátkých pauz)
        short_pauses = sum(1 for p in pauses if p < self.stutter_threshold)
        if short_pauses / len(pauses) > 0.6:
            pattern = 'stuttering'
        
        return {
            'pattern': pattern,
            'avg_pause': round(avg_pause, 2),
            'total_pauses': len(pauses),
            'short_pauses': short_pauses,
            'confidence': 'high' if len(pauses) > 5 else 'low'
        }
