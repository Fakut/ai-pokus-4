# database/meetings_db.py
"""
Databáze pro správu schůzek a dostupnosti
Podporuje detekci konfliktů, blokované časy a minimální rozestup mezi schůzkami
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


class MeetingsDB:
    """Správa schůzek a dostupnosti"""
    
    def __init__(self, db_path="data/meetings.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Inicializuje databázi schůzek"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabulka pro schůzky
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            call_sid TEXT,
            contact_name TEXT NOT NULL,
            contact_phone TEXT NOT NULL,
            meeting_datetime TEXT NOT NULL,
            location_type TEXT,
            location_details TEXT,
            status TEXT DEFAULT 'scheduled',
            followup_person TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabulka pro blokované časy
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS availability_blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time_from TEXT NOT NULL,
            time_to TEXT NOT NULL,
            reason TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        conn.close()
        print("  ✅ Meetings database initialized")
    
    def add_meeting(self, contact_name: str, contact_phone: str, 
                   meeting_datetime: str, location_type: str = None,
                   location_details: str = None, followup_person: str = None,
                   notes: str = None, call_sid: str = None) -> int:
        """
        Přidá novou schůzku
        
        Args:
            contact_name: Jméno kontaktu
            contact_phone: Telefon kontaktu
            meeting_datetime: Datum a čas schůzky (ISO format)
            location_type: Typ místa (u_nas, u_nich, online)
            location_details: Detaily místa
            followup_person: Kdo bude následovat
            notes: Poznámky
            call_sid: ID hovoru z Twilio
            
        Returns:
            ID nově vytvořené schůzky
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO meetings 
        (call_sid, contact_name, contact_phone, meeting_datetime, 
         location_type, location_details, followup_person, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (call_sid, contact_name, contact_phone, meeting_datetime,
              location_type, location_details, followup_person, notes))
        
        meeting_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"  ✅ Meeting scheduled: {contact_name} on {meeting_datetime}")
        return meeting_id
    
    def get_meetings(self, status: str = None, 
                    from_date: str = None, 
                    to_date: str = None) -> List[Dict]:
        """
        Získá seznam schůzek s možností filtrování
        
        Args:
            status: Filtr podle statusu (scheduled, completed, cancelled)
            from_date: Od data (ISO format)
            to_date: Do data (ISO format)
            
        Returns:
            Seznam schůzek jako slovníky
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM meetings WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if from_date:
            query += " AND meeting_datetime >= ?"
            params.append(from_date)
        
        if to_date:
            query += " AND meeting_datetime <= ?"
            params.append(to_date)
        
        query += " ORDER BY meeting_datetime ASC"
        
        cursor.execute(query, params)
        meetings = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return meetings
    
    def get_meeting(self, meeting_id: int) -> Optional[Dict]:
        """Získá detail konkrétní schůzky"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_meeting(self, meeting_id: int, **kwargs) -> bool:
        """
        Aktualizuje schůzku
        
        Args:
            meeting_id: ID schůzky
            **kwargs: Pole k aktualizaci (meeting_datetime, status, notes, atd.)
            
        Returns:
            True pokud byla aktualizace úspěšná
        """
        if not kwargs:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sestavení UPDATE query
        fields = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [meeting_id]
        
        cursor.execute(f"UPDATE meetings SET {fields} WHERE id = ?", values)
        affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def delete_meeting(self, meeting_id: int) -> bool:
        """Smaže schůzku"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))
        affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def check_conflicts(self, meeting_datetime: str, 
                       min_spacing_hours: int = 24) -> List[Dict]:
        """
        Kontroluje konflikty se stávajícími schůzkami
        
        Args:
            meeting_datetime: Požadovaný čas schůzky (ISO format)
            min_spacing_hours: Minimální rozestup mezi schůzkami v hodinách
            
        Returns:
            Seznam konfliktních schůzek
        """
        try:
            requested_dt = datetime.fromisoformat(meeting_datetime)
        except ValueError:
            return []
        
        # Časové okno pro kontrolu
        start_window = (requested_dt - timedelta(hours=min_spacing_hours)).isoformat()
        end_window = (requested_dt + timedelta(hours=min_spacing_hours)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT * FROM meetings 
        WHERE status = 'scheduled'
        AND meeting_datetime BETWEEN ? AND ?
        """, (start_window, end_window))
        
        conflicts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return conflicts
    
    def add_availability_block(self, date: str, time_from: str, 
                              time_to: str, reason: str = None) -> int:
        """
        Přidá blokovaný čas (nedostupnost)
        
        Args:
            date: Datum (YYYY-MM-DD)
            time_from: Čas od (HH:MM)
            time_to: Čas do (HH:MM)
            reason: Důvod blokace
            
        Returns:
            ID nově vytvořené blokace
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO availability_blocks (date, time_from, time_to, reason)
        VALUES (?, ?, ?, ?)
        """, (date, time_from, time_to, reason))
        
        block_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"  ✅ Availability block added: {date} {time_from}-{time_to}")
        return block_id
    
    def get_availability_blocks(self, date: str = None) -> List[Dict]:
        """
        Získá blokované časy
        
        Args:
            date: Filtr podle data (YYYY-MM-DD)
            
        Returns:
            Seznam blokovaných časů
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if date:
            cursor.execute(
                "SELECT * FROM availability_blocks WHERE date = ? ORDER BY time_from",
                (date,)
            )
        else:
            cursor.execute(
                "SELECT * FROM availability_blocks ORDER BY date, time_from"
            )
        
        blocks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return blocks
    
    def delete_availability_block(self, block_id: int) -> bool:
        """Smaže blokovaný čas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM availability_blocks WHERE id = ?", (block_id,))
        affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def is_time_blocked(self, meeting_datetime: str) -> Optional[Dict]:
        """
        Zkontroluje, zda je čas blokovaný
        
        Args:
            meeting_datetime: Čas ke kontrole (ISO format)
            
        Returns:
            Blokace pokud existuje, jinak None
        """
        try:
            dt = datetime.fromisoformat(meeting_datetime)
        except ValueError:
            return None
        
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M")
        
        blocks = self.get_availability_blocks(date_str)
        
        for block in blocks:
            if block['time_from'] <= time_str <= block['time_to']:
                return block
        
        return None
    
    def get_stats(self) -> Dict:
        """Získá statistiky schůzek"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Celkový počet schůzek
        cursor.execute("SELECT COUNT(*) FROM meetings")
        total = cursor.fetchone()[0]
        
        # Podle statusu
        cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM meetings 
        GROUP BY status
        """)
        by_status = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Nadcházející schůzky
        now = datetime.now().isoformat()
        cursor.execute("""
        SELECT COUNT(*) FROM meetings 
        WHERE status = 'scheduled' AND meeting_datetime >= ?
        """, (now,))
        upcoming = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total,
            'by_status': by_status,
            'upcoming': upcoming
        }
