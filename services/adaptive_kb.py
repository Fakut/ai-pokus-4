# services/adaptive_kb.py
"""
Adaptive Knowledge Base - učí se z každé konverzace
Dynamicky aktualizuje znalosti na základě úspěšných vzorců
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class AdaptiveKnowledgeBase:
    """
    Adaptivní znalostní báze, která se učí z každé konverzace
    - Ukládá úspěšné odpovědi
    - Scoruje kvalitu odpovědí
    - Dynamicky aktualizuje KB na základě zkušeností
    """
    
    def __init__(self):
        self.data_dir = Path("data/adaptive_kb")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.patterns_file = self.data_dir / "learned_patterns.json"
        self.responses_file = self.data_dir / "successful_responses.json"
        self.scores_file = self.data_dir / "response_scores.json"
        
        self._init_files()
        self.learned_patterns = self._load_patterns()
        self.successful_responses = self._load_responses()
        self.response_scores = self._load_scores()
    
    def _init_files(self):
        """Inicializuje soubory pro ukládání dat"""
        for file in [self.patterns_file, self.responses_file, self.scores_file]:
            if not file.exists():
                file.write_text(json.dumps({}, indent=2))
    
    def _load_patterns(self) -> Dict:
        """Načte naučené vzorce"""
        try:
            return json.loads(self.patterns_file.read_text())
        except:
            return {}
    
    def _load_responses(self) -> Dict:
        """Načte úspěšné odpovědi"""
        try:
            return json.loads(self.responses_file.read_text())
        except:
            return {}
    
    def _load_scores(self) -> Dict:
        """Načte skóre odpovědí"""
        try:
            return json.loads(self.scores_file.read_text())
        except:
            return {}
    
    def learn_from_conversation(self, call_sid: str, conversation_history: List[Dict], 
                                outcome_score: int):
        """
        Učí se z konverzace a ukládá úspěšné vzorce
        
        Args:
            call_sid: ID hovoru
            conversation_history: Historie konverzace
            outcome_score: Skóre výsledku (0-100)
        """
        print(f"\n🧠 [AdaptiveKB] Learning from conversation {call_sid}")
        print(f"   Outcome score: {outcome_score}/100")
        
        if outcome_score < 40:
            print(f"   ⏭️  Score příliš nízké, přeskakuji learning")
            return
        
        # Extrahuj užitečné vzorce z konverzace
        for i, msg in enumerate(conversation_history):
            if msg['role'] == 'user' and i + 1 < len(conversation_history):
                user_msg = msg['content']
                ai_response = conversation_history[i + 1]['content']
                
                if conversation_history[i + 1]['role'] == 'assistant':
                    # Ulož vzorec otázka -> odpověď
                    self._learn_pattern(user_msg, ai_response, outcome_score)
        
        print(f"   ✅ Learning complete")
    
    def _learn_pattern(self, user_input: str, ai_response: str, score: int):
        """
        Uloží vzorec user input -> AI response s score
        """
        # Normalize user input pro matching
        normalized_input = self._normalize_text(user_input)
        
        # Pokud tento pattern ještě neexistuje, vytvoř ho
        if normalized_input not in self.learned_patterns:
            self.learned_patterns[normalized_input] = {
                "responses": [],
                "avg_score": 0,
                "count": 0
            }
        
        pattern = self.learned_patterns[normalized_input]
        
        # Přidej response
        pattern["responses"].append({
            "text": ai_response,
            "score": score,
            "timestamp": datetime.now().isoformat()
        })
        
        # Udržuj max 5 nejlepších responses
        pattern["responses"] = sorted(
            pattern["responses"], 
            key=lambda x: x["score"], 
            reverse=True
        )[:5]
        
        # Aktualizuj průměrné score
        pattern["count"] += 1
        pattern["avg_score"] = sum(r["score"] for r in pattern["responses"]) / len(pattern["responses"])
        
        # Ulož
        self._save_patterns()
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalizuje text pro lepší matching
        Odstraní detaily, zachová základ
        """
        # Lowercase
        normalized = text.lower().strip()
        
        # Odstraň čísla a speciální znaky, zachovej podstatu
        import re
        normalized = re.sub(r'\d+', '', normalized)
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Pro lepší matching zkrať na klíčová slova (první 50 znaků)
        if len(normalized) > 50:
            words = normalized.split()[:7]  # Prvních 7 slov
            normalized = ' '.join(words)
        
        return normalized
    
    def get_best_response(self, user_input: str) -> Optional[str]:
        """
        Najde nejlepší naučenou odpověď pro daný input
        
        Returns:
            Nejlépe scorovaná odpověď nebo None
        """
        normalized_input = self._normalize_text(user_input)
        
        # Přesná shoda
        if normalized_input in self.learned_patterns:
            pattern = self.learned_patterns[normalized_input]
            if pattern["responses"]:
                best_response = pattern["responses"][0]  # První je nejlepší (sorted)
                print(f"   📚 [AdaptiveKB] Found learned response (score: {best_response['score']})")
                return best_response["text"]
        
        # Fuzzy matching - najdi podobný pattern
        best_match = self._find_similar_pattern(normalized_input)
        if best_match:
            print(f"   📚 [AdaptiveKB] Found similar pattern (score: {best_match['score']})")
            return best_match["text"]
        
        return None
    
    def _find_similar_pattern(self, normalized_input: str) -> Optional[Dict]:
        """
        Najde podobný pattern pomocí keyword overlap
        """
        input_words = set(normalized_input.split())
        best_match = None
        best_overlap = 0
        
        for pattern_key, pattern_data in self.learned_patterns.items():
            pattern_words = set(pattern_key.split())
            overlap = len(input_words & pattern_words)
            
            # Musí mít alespoň 50% overlap
            overlap_ratio = overlap / max(len(input_words), len(pattern_words))
            
            if overlap_ratio > 0.5 and overlap > best_overlap:
                best_overlap = overlap
                if pattern_data["responses"]:
                    best_match = pattern_data["responses"][0]
        
        return best_match
    
    def _save_patterns(self):
        """Uloží naučené vzorce"""
        self.patterns_file.write_text(
            json.dumps(self.learned_patterns, indent=2, ensure_ascii=False)
        )
    
    def score_response_quality(self, response: str, context: Dict) -> int:
        """
        Scoruje kvalitu odpovědi (0-100)
        
        Args:
            response: AI odpověď
            context: Kontext (user input, intent, atd.)
        
        Returns:
            Score 0-100
        """
        score = 50  # Baseline
        
        # Délka odpovědi (optimální je 20-100 znaků)
        response_len = len(response)
        if 20 <= response_len <= 100:
            score += 10
        elif response_len < 10:
            score -= 20  # Příliš krátké
        elif response_len > 150:
            score -= 10  # Příliš dlouhé
        
        # Obsahuje otázku? (aktivní engagement)
        if '?' in response:
            score += 15
        
        # Obsahuje konkrétní informace (čísla, fakta)
        import re
        if re.search(r'\d+', response):
            score += 10
        
        # Není příliš formální nebo robotický
        robotic_phrases = ['děkuji za dotaz', 'rádi vám pomůžeme', 'těší nás']
        if any(phrase in response.lower() for phrase in robotic_phrases):
            score -= 15
        
        # Je přirozený a konverzační
        conversational = ['jo', 'super', 'skvělé', 'výborně', 'jasně']
        if any(word in response.lower() for word in conversational):
            score += 10
        
        # Clamp 0-100
        return max(0, min(100, score))
    
    def get_stats(self) -> Dict:
        """Vrátí statistiky adaptivní KB"""
        total_patterns = len(self.learned_patterns)
        total_responses = sum(len(p["responses"]) for p in self.learned_patterns.values())
        avg_score = sum(p["avg_score"] for p in self.learned_patterns.values()) / total_patterns if total_patterns > 0 else 0
        
        return {
            "total_patterns": total_patterns,
            "total_responses": total_responses,
            "avg_pattern_score": round(avg_score, 1),
            "patterns_over_80": sum(1 for p in self.learned_patterns.values() if p["avg_score"] > 80)
        }
    
    def update_dynamic_kb(self, kb_updates: Dict):
        """
        Dynamicky aktualizuje znalostní bázi na základě zkušeností
        
        Args:
            kb_updates: Slovník s aktualizacemi KB
        """
        print(f"\n🔄 [AdaptiveKB] Updating dynamic KB")
        
        for key, value in kb_updates.items():
            print(f"   Updating: {key}")
        
        # Zde by mohla být logika pro update originální KB
        # Pro teď jen logujeme
        print(f"   ✅ KB updates logged")
