# database/conversation_patterns.py
"""
Database pro ukládání a analýzu vzorců konverzací
Poskytuje strukturovaný přístup k datům pro machine learning
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import sqlite3


class ConversationPatternsDB:
    """
    Database pro ukládání vzorců konverzací
    Používá SQLite pro strukturované ukládání a rychlé dotazy
    """
    
    def __init__(self, db_path: str = None):
        """
        Args:
            db_path: Cesta k SQLite databázi (default: data/conversation_patterns.db)
        """
        if db_path is None:
            data_dir = Path("data")
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(data_dir / "conversation_patterns.db")
        
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Inicializuje databázové tabulky"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Tabulka pro kompletní konverzace
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_sid TEXT UNIQUE NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_seconds INTEGER,
                outcome TEXT,
                outcome_score INTEGER,
                total_turns INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabulka pro jednotlivé tahy konverzace
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                turn_number INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                intent TEXT,
                timestamp TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
        
        # Tabulka pro vzorce (patterns)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_key TEXT UNIQUE NOT NULL,
                pattern_type TEXT NOT NULL,
                occurrences INTEGER DEFAULT 0,
                successful INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0,
                avg_score REAL DEFAULT 0,
                last_seen TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabulka pro objection handling
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS objections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                objection_type TEXT NOT NULL,
                objection_text TEXT NOT NULL,
                response_text TEXT,
                was_overcome INTEGER DEFAULT 0,
                outcome_score INTEGER,
                timestamp TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
        
        # Tabulka pro úspěšné fráze
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS successful_phrases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phrase_text TEXT NOT NULL,
                phrase_type TEXT NOT NULL,
                usage_count INTEGER DEFAULT 0,
                avg_score REAL DEFAULT 0,
                last_used TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    def store_conversation(self, call_sid: str, conversation_data: Dict) -> int:
        """
        Uloží celou konverzaci do databáze
        
        Args:
            call_sid: ID hovoru
            conversation_data: Kompletní data konverzace
            
        Returns:
            ID vložené konverzace
        """
        cursor = self.conn.cursor()
        
        # Ulož hlavní záznam konverzace
        cursor.execute("""
            INSERT OR REPLACE INTO conversations 
            (call_sid, start_time, end_time, duration_seconds, outcome, outcome_score, total_turns)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            call_sid,
            conversation_data.get('start_time', datetime.now().isoformat()),
            conversation_data.get('end_time', datetime.now().isoformat()),
            conversation_data.get('duration_seconds', 0),
            conversation_data.get('outcome', 'unknown'),
            conversation_data.get('outcome_score', 0),
            len(conversation_data.get('history', []))
        ))
        
        conversation_id = cursor.lastrowid
        
        # Ulož jednotlivé tahy
        history = conversation_data.get('history', [])
        for i, turn in enumerate(history):
            cursor.execute("""
                INSERT INTO conversation_turns 
                (conversation_id, turn_number, role, content, intent, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                conversation_id,
                i,
                turn.get('role', 'unknown'),
                turn.get('content', ''),
                turn.get('intent', ''),
                datetime.now().isoformat()
            ))
        
        # Ulož námitky pokud jsou
        objections = conversation_data.get('objections', [])
        for obj in objections:
            cursor.execute("""
                INSERT INTO objections 
                (conversation_id, objection_type, objection_text, response_text, 
                 was_overcome, outcome_score, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation_id,
                obj.get('type', 'unknown'),
                obj.get('text', ''),
                obj.get('response', ''),
                1 if obj.get('overcome', False) else 0,
                conversation_data.get('outcome_score', 0),
                datetime.now().isoformat()
            ))
        
        self.conn.commit()
        return conversation_id
    
    def update_pattern_stats(self, pattern_key: str, pattern_type: str, 
                            was_successful: bool, score: int):
        """
        Aktualizuje statistiky pro pattern
        
        Args:
            pattern_key: Klíč patternu
            pattern_type: Typ patternu (opening, closing, objection, etc.)
            was_successful: Zda byl úspěšný
            score: Skóre
        """
        cursor = self.conn.cursor()
        
        # Zkontroluj zda pattern existuje
        cursor.execute("SELECT * FROM patterns WHERE pattern_key = ?", (pattern_key,))
        existing = cursor.fetchone()
        
        if existing:
            # Update
            new_occurrences = existing['occurrences'] + 1
            new_successful = existing['successful'] + (1 if was_successful else 0)
            new_failed = existing['failed'] + (0 if was_successful else 1)
            new_avg_score = (existing['avg_score'] * existing['occurrences'] + score) / new_occurrences
            
            cursor.execute("""
                UPDATE patterns 
                SET occurrences = ?, successful = ?, failed = ?, 
                    avg_score = ?, last_seen = ?
                WHERE pattern_key = ?
            """, (
                new_occurrences, new_successful, new_failed,
                new_avg_score, datetime.now().isoformat(), pattern_key
            ))
        else:
            # Insert
            cursor.execute("""
                INSERT INTO patterns 
                (pattern_key, pattern_type, occurrences, successful, failed, avg_score, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern_key, pattern_type, 1,
                1 if was_successful else 0,
                0 if was_successful else 1,
                score, datetime.now().isoformat()
            ))
        
        self.conn.commit()
    
    def get_successful_patterns(self, min_occurrences: int = 3) -> List[Dict]:
        """
        Získá nejúspěšnější patterns
        
        Args:
            min_occurrences: Minimální počet výskytů
            
        Returns:
            List patterns seřazených podle úspěšnosti
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM patterns
            WHERE occurrences >= ? AND successful > failed
            ORDER BY avg_score DESC, occurrences DESC
            LIMIT 20
        """, (min_occurrences,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_objection_success_rate(self, objection_type: str) -> Dict:
        """
        Získá statistiky úspěšnosti překonávání konkrétní námitky
        
        Args:
            objection_type: Typ námitky
            
        Returns:
            Dict se statistikami
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(was_overcome) as overcome,
                AVG(outcome_score) as avg_score
            FROM objections
            WHERE objection_type = ?
        """, (objection_type,))
        
        result = cursor.fetchone()
        
        if result and result['total'] > 0:
            return {
                'total': result['total'],
                'overcome': result['overcome'],
                'success_rate': f"{result['overcome'] / result['total'] * 100:.1f}%",
                'avg_score': round(result['avg_score'], 1) if result['avg_score'] else 0
            }
        
        return {'total': 0, 'overcome': 0, 'success_rate': '0%', 'avg_score': 0}
    
    def get_best_responses_for_objection(self, objection_type: str, limit: int = 5) -> List[Dict]:
        """
        Získá nejlepší odpovědi na konkrétní námitku
        
        Args:
            objection_type: Typ námitky
            limit: Max počet výsledků
            
        Returns:
            List nejlepších odpovědí
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT response_text, outcome_score, timestamp
            FROM objections
            WHERE objection_type = ? AND was_overcome = 1
            ORDER BY outcome_score DESC
            LIMIT ?
        """, (objection_type, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def analyze_conversation_flow(self) -> Dict:
        """
        Analyzuje flow konverzací - kolik tahů trvají, kde končí, atd.
        
        Returns:
            Dict s analýzou
        """
        cursor = self.conn.cursor()
        
        # Průměrný počet tahů
        cursor.execute("""
            SELECT AVG(total_turns) as avg_turns,
                   MIN(total_turns) as min_turns,
                   MAX(total_turns) as max_turns
            FROM conversations
        """)
        turns_stats = dict(cursor.fetchone())
        
        # Outcome distribution
        cursor.execute("""
            SELECT outcome, COUNT(*) as count
            FROM conversations
            GROUP BY outcome
        """)
        outcome_dist = {row['outcome']: row['count'] for row in cursor.fetchall()}
        
        # Průměrné skóre podle délky konverzace
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN total_turns <= 4 THEN 'short'
                    WHEN total_turns <= 10 THEN 'medium'
                    ELSE 'long'
                END as length_category,
                AVG(outcome_score) as avg_score,
                COUNT(*) as count
            FROM conversations
            GROUP BY length_category
        """)
        score_by_length = {row['length_category']: {
            'avg_score': round(row['avg_score'], 1),
            'count': row['count']
        } for row in cursor.fetchall()}
        
        return {
            'turns_stats': turns_stats,
            'outcome_distribution': outcome_dist,
            'score_by_length': score_by_length
        }
    
    def get_database_stats(self) -> Dict:
        """Vrátí celkové statistiky databáze"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM conversations")
        total_conversations = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM patterns")
        total_patterns = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM objections")
        total_objections = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT AVG(outcome_score) as avg_score 
            FROM conversations 
            WHERE outcome_score > 0
        """)
        avg_score = cursor.fetchone()['avg_score']
        
        return {
            'total_conversations': total_conversations,
            'total_patterns': total_patterns,
            'total_objections_logged': total_objections,
            'avg_conversation_score': round(avg_score, 1) if avg_score else 0
        }
    
    def close(self):
        """Uzavře databázové spojení"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Destruktor - zajistí uzavření spojení"""
        self.close()
