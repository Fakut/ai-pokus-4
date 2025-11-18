# services/conversation_memory.py
"""
Dlouhodobá paměť konverzací
- Ukládání úspěšných vzorců
- User profiling
- Cross-conversation learning
- Kontinuální zlepšování
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class ConversationMemory:
    """
    Dlouhodobá paměť pro ukládání a analýzu konverzací
    Učí se napříč všemi hovory a vytváří profily úspěšných vzorců
    """
    
    def __init__(self):
        self.data_dir = Path("data/conversation_memory")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.patterns_file = self.data_dir / "conversation_patterns.json"
        self.profiles_file = self.data_dir / "user_profiles.json"
        self.insights_file = self.data_dir / "learned_insights.json"
        
        self._init_files()
        
        self.patterns = self._load_patterns()
        self.user_profiles = self._load_profiles()
        self.insights = self._load_insights()
        
        # Ensure insights has the correct structure
        if not self.insights.get('successful_openings'):
            self.insights['successful_openings'] = []
        if not self.insights.get('successful_closings'):
            self.insights['successful_closings'] = []
        if not self.insights.get('best_objection_handlers'):
            self.insights['best_objection_handlers'] = {}
        if not self.insights.get('timing_insights'):
            self.insights['timing_insights'] = {}
        if not self.insights.get('conversation_flow_patterns'):
            self.insights['conversation_flow_patterns'] = []
    
    def _init_files(self):
        """Inicializuje soubory"""
        for file in [self.patterns_file, self.profiles_file, self.insights_file]:
            if not file.exists():
                file.write_text(json.dumps({}, indent=2))
    
    def _load_patterns(self) -> Dict:
        """Načte vzorce konverzací"""
        try:
            return json.loads(self.patterns_file.read_text())
        except:
            return {}
    
    def _load_profiles(self) -> Dict:
        """Načte uživatelské profily"""
        try:
            return json.loads(self.profiles_file.read_text())
        except:
            return {}
    
    def _load_insights(self) -> Dict:
        """Načte naučené poznatky"""
        try:
            return json.loads(self.insights_file.read_text())
        except:
            return {
                'successful_openings': [],
                'successful_closings': [],
                'best_objection_handlers': {},
                'timing_insights': {},
                'conversation_flow_patterns': []
            }
    
    def store_conversation(self, call_sid: str, conversation_data: Dict):
        """
        Uloží celou konverzaci do dlouhodobé paměti
        
        Args:
            call_sid: ID hovoru
            conversation_data: Data konverzace včetně historie, skóre, outcome
        """
        print(f"\n🧠 [Memory] Storing conversation {call_sid}")
        
        # Analyzuj konverzaci
        analysis = self._analyze_conversation(conversation_data)
        
        # Ulož pattern
        pattern_key = self._generate_pattern_key(conversation_data)
        
        if pattern_key not in self.patterns:
            self.patterns[pattern_key] = {
                'occurrences': 0,
                'successful': 0,
                'failed': 0,
                'avg_score': 0,
                'examples': []
            }
        
        pattern = self.patterns[pattern_key]
        pattern['occurrences'] += 1
        
        # Update success/fail
        outcome_score = conversation_data.get('outcome_score', 0)
        if outcome_score >= 60:
            pattern['successful'] += 1
        else:
            pattern['failed'] += 1
        
        # Update avg score
        pattern['avg_score'] = (
            (pattern['avg_score'] * (pattern['occurrences'] - 1) + outcome_score) 
            / pattern['occurrences']
        )
        
        # Ulož příklad (max 5 nejlepších)
        example = {
            'call_sid': call_sid,
            'score': outcome_score,
            'timestamp': datetime.now().isoformat(),
            'summary': conversation_data.get('summary', ''),
            'key_moments': analysis.get('key_moments', [])
        }
        
        pattern['examples'].append(example)
        pattern['examples'] = sorted(
            pattern['examples'],
            key=lambda x: x['score'],
            reverse=True
        )[:5]
        
        self._save_patterns()
        
        # Aktualizuj insights
        self._update_insights(conversation_data, analysis)
        
        print(f"   ✅ Conversation stored (pattern: {pattern_key}, score: {outcome_score})")
    
    def _analyze_conversation(self, conversation_data: Dict) -> Dict:
        """
        Analyzuje konverzaci a extrahuje klíčové momenty
        
        Args:
            conversation_data: Data konverzace
            
        Returns:
            Dict s analýzou
        """
        history = conversation_data.get('history', [])
        
        analysis = {
            'total_turns': len(history),
            'opening': '',
            'closing': '',
            'key_moments': [],
            'objections_raised': [],
            'objections_overcome': []
        }
        
        # Extrahuj opening (první AI zpráva)
        for msg in history:
            if msg['role'] == 'assistant':
                analysis['opening'] = msg['content'][:100]
                break
        
        # Extrahuj closing (poslední AI zpráva)
        for msg in reversed(history):
            if msg['role'] == 'assistant':
                analysis['closing'] = msg['content'][:100]
                break
        
        # Detekuj námitky
        objection_keywords = ['drahé', 'nemám čas', 'nezájem', 'už máme', 'peníze']
        for i, msg in enumerate(history):
            if msg['role'] == 'user':
                content_lower = msg['content'].lower()
                for keyword in objection_keywords:
                    if keyword in content_lower:
                        analysis['objections_raised'].append({
                            'keyword': keyword,
                            'turn': i,
                            'context': msg['content'][:100]
                        })
                        
                        # Zkontroluj zda byla překonána (další AI odpověď)
                        if i + 1 < len(history) and history[i + 1]['role'] == 'assistant':
                            analysis['objections_overcome'].append({
                                'objection': keyword,
                                'response': history[i + 1]['content'][:100]
                            })
        
        return analysis
    
    def _generate_pattern_key(self, conversation_data: Dict) -> str:
        """
        Generuje klíč pro pattern na základě charakteristik konverzace
        
        Args:
            conversation_data: Data konverzace
            
        Returns:
            Pattern key
        """
        # Charakteristiky
        outcome = conversation_data.get('outcome', 'unknown')
        length = len(conversation_data.get('history', []))
        
        # Kategorizuj délku
        if length <= 4:
            length_cat = 'short'
        elif length <= 10:
            length_cat = 'medium'
        else:
            length_cat = 'long'
        
        # Detekuj zda měl námitky
        had_objections = 'objections' in str(conversation_data).lower()
        objection_status = 'with_objections' if had_objections else 'smooth'
        
        return f"{outcome}_{length_cat}_{objection_status}"
    
    def _update_insights(self, conversation_data: Dict, analysis: Dict):
        """
        Aktualizuje naučené poznatky
        
        Args:
            conversation_data: Data konverzace
            analysis: Analýza konverzace
        """
        outcome_score = conversation_data.get('outcome_score', 0)
        
        # Úspěšný hovor?
        if outcome_score >= 70:
            # Ulož úspěšný opening
            if analysis['opening']:
                self.insights['successful_openings'].append({
                    'text': analysis['opening'],
                    'score': outcome_score,
                    'timestamp': datetime.now().isoformat()
                })
                # Drž max 10 nejlepších
                self.insights['successful_openings'] = sorted(
                    self.insights['successful_openings'],
                    key=lambda x: x['score'],
                    reverse=True
                )[:10]
            
            # Ulož úspěšný closing
            if analysis['closing']:
                self.insights['successful_closings'].append({
                    'text': analysis['closing'],
                    'score': outcome_score,
                    'timestamp': datetime.now().isoformat()
                })
                self.insights['successful_closings'] = sorted(
                    self.insights['successful_closings'],
                    key=lambda x: x['score'],
                    reverse=True
                )[:10]
            
            # Ulož úspěšné overcome objections
            for obj in analysis.get('objections_overcome', []):
                objection_type = obj['objection']
                if objection_type not in self.insights['best_objection_handlers']:
                    self.insights['best_objection_handlers'][objection_type] = []
                
                self.insights['best_objection_handlers'][objection_type].append({
                    'response': obj['response'],
                    'score': outcome_score,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Drž max 5 nejlepších pro každý typ
                self.insights['best_objection_handlers'][objection_type] = sorted(
                    self.insights['best_objection_handlers'][objection_type],
                    key=lambda x: x['score'],
                    reverse=True
                )[:5]
        
        self._save_insights()
    
    def get_best_practices(self) -> Dict:
        """
        Vrátí nejlepší praktiky naučené z konverzací
        
        Returns:
            Dict s best practices
        """
        best_practices = {
            'best_openings': [],
            'best_closings': [],
            'objection_handling': {},
            'successful_patterns': []
        }
        
        # Top 3 openings
        if self.insights['successful_openings']:
            best_practices['best_openings'] = [
                o['text'] for o in self.insights['successful_openings'][:3]
            ]
        
        # Top 3 closings
        if self.insights['successful_closings']:
            best_practices['best_closings'] = [
                c['text'] for c in self.insights['successful_closings'][:3]
            ]
        
        # Best objection handlers
        for obj_type, handlers in self.insights['best_objection_handlers'].items():
            if handlers:
                best_practices['objection_handling'][obj_type] = handlers[0]['response']
        
        # Top 5 successful patterns
        successful_patterns = sorted(
            [
                (k, v) for k, v in self.patterns.items()
                if v['successful'] > v['failed'] and v['occurrences'] >= 2
            ],
            key=lambda x: x[1]['avg_score'],
            reverse=True
        )[:5]
        
        best_practices['successful_patterns'] = [
            {
                'pattern': k,
                'success_rate': f"{v['successful'] / v['occurrences'] * 100:.0f}%",
                'avg_score': round(v['avg_score'], 1)
            }
            for k, v in successful_patterns
        ]
        
        return best_practices
    
    def create_user_profile(self, contact_info: Dict, conversation_result: Dict):
        """
        Vytvoří nebo aktualizuje profil uživatele
        Co na něj funguje / nefunguje
        
        Args:
            contact_info: Info o kontaktu (jméno, firma, atd.)
            conversation_result: Výsledek konverzace
        """
        # Pro anonymitu používáme hash
        import hashlib
        phone = contact_info.get('phone', 'unknown')
        profile_id = hashlib.md5(phone.encode()).hexdigest()[:10]
        
        if profile_id not in self.user_profiles:
            self.user_profiles[profile_id] = {
                'first_contact': datetime.now().isoformat(),
                'total_calls': 0,
                'successful_approaches': [],
                'failed_approaches': [],
                'preferences': {}
            }
        
        profile = self.user_profiles[profile_id]
        profile['total_calls'] += 1
        profile['last_contact'] = datetime.now().isoformat()
        
        # Ulož co fungovalo/nefungovalo
        outcome_score = conversation_result.get('score', 0)
        approach = conversation_result.get('approach', 'standard')
        
        if outcome_score >= 60:
            profile['successful_approaches'].append({
                'approach': approach,
                'score': outcome_score,
                'timestamp': datetime.now().isoformat()
            })
        else:
            profile['failed_approaches'].append({
                'approach': approach,
                'score': outcome_score,
                'timestamp': datetime.now().isoformat()
            })
        
        self._save_profiles()
    
    def get_insights_for_improvement(self) -> List[str]:
        """
        Vrátí doporučení pro zlepšení na základě naučených vzorců
        
        Returns:
            List doporučení
        """
        recommendations = []
        
        # Analyzuj patterns
        total_patterns = len(self.patterns)
        if total_patterns == 0:
            return ["Nedostatek dat pro analýzu. Potřeba více konverzací."]
        
        # Najdi neúspěšné patterns
        failed_patterns = [
            (k, v) for k, v in self.patterns.items()
            if v['failed'] > v['successful'] and v['occurrences'] >= 3
        ]
        
        if failed_patterns:
            recommendations.append(
                f"⚠️  Zjištěno {len(failed_patterns)} problematických vzorců konverzace"
            )
            for pattern_key, pattern_data in failed_patterns[:2]:
                recommendations.append(
                    f"  - Pattern '{pattern_key}': {pattern_data['failed']}/{pattern_data['occurrences']} failed"
                )
        
        # Najdi nejúspěšnější přístupy
        successful_patterns = sorted(
            [(k, v) for k, v in self.patterns.items() if v['avg_score'] > 70],
            key=lambda x: x[1]['avg_score'],
            reverse=True
        )[:2]
        
        if successful_patterns:
            recommendations.append(
                f"✅ Nejúspěšnější patterns:"
            )
            for pattern_key, pattern_data in successful_patterns:
                recommendations.append(
                    f"  - '{pattern_key}': avg score {pattern_data['avg_score']:.1f}"
                )
        
        # Doporučení na objection handling
        if self.insights['best_objection_handlers']:
            recommendations.append(
                f"💡 Naučeno {len(self.insights['best_objection_handlers'])} způsobů překonání námitek"
            )
        
        return recommendations
    
    def _save_patterns(self):
        """Uloží vzorce"""
        self.patterns_file.write_text(
            json.dumps(self.patterns, indent=2, ensure_ascii=False)
        )
    
    def _save_profiles(self):
        """Uloží profily"""
        self.profiles_file.write_text(
            json.dumps(self.user_profiles, indent=2, ensure_ascii=False)
        )
    
    def _save_insights(self):
        """Uloží poznatky"""
        self.insights_file.write_text(
            json.dumps(self.insights, indent=2, ensure_ascii=False)
        )
    
    def get_stats(self) -> Dict:
        """Vrátí statistiky paměti"""
        total_conversations = sum(p['occurrences'] for p in self.patterns.values())
        successful_conversations = sum(p['successful'] for p in self.patterns.values())
        
        return {
            'total_patterns': len(self.patterns),
            'total_conversations': total_conversations,
            'successful_conversations': successful_conversations,
            'success_rate': f"{successful_conversations / total_conversations * 100:.1f}%" if total_conversations > 0 else "0%",
            'unique_user_profiles': len(self.user_profiles),
            'learned_openings': len(self.insights['successful_openings']),
            'learned_closings': len(self.insights['successful_closings']),
            'objection_types_learned': len(self.insights['best_objection_handlers'])
        }
