# services/meeting_scheduler.py
"""
AI logika pro domlouvání schůzek
- Detekce požadavku na schůzku
- Parsování času z přirozeného jazyka
- Kontrola dostupnosti a konfliktů
- Nabízení alternativních termínů
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database.meetings_db import MeetingsDB


class MeetingScheduler:
    """AI asistent pro domlouvání schůzek"""
    
    def __init__(self):
        self.db = MeetingsDB()
        self.min_spacing_hours = 24  # Minimální rozestup mezi schůzkami
        
        # Slovník pro parsování času
        self.day_keywords = {
            'dnes': 0,
            'dneska': 0,
            'zítra': 1,
            'zítřek': 1,
            'pozítří': 2,
            'pozítřek': 2,
            'pondělí': None,
            'úterý': None,
            'středa': None,
            'středu': None,
            'čtvrtek': None,
            'pátek': None,
            'sobota': None,
            'neděle': None,
        }
        
        self.time_keywords = {
            'ráno': '09:00',
            'dopoledne': '10:00',
            'poledne': '12:00',
            'odpoledne': '14:00',
            'večer': '18:00',
        }
    
    def detect_meeting_request(self, text: str) -> bool:
        """
        Detekuje, zda text obsahuje požadavek na schůzku
        
        Args:
            text: Text k analýze
            
        Returns:
            True pokud text obsahuje požadavek na schůzku
        """
        text_lower = text.lower()
        
        meeting_keywords = [
            'schůzka', 'schůzku', 'sejít', 'setkání', 'potkat',
            'můžeme se sejít', 'můžem se vidět', 'sejdeme se',
            'setkat', 'osobně', 'prezentace', 'schůzce'
        ]
        
        return any(keyword in text_lower for keyword in meeting_keywords)
    
    def parse_time_from_text(self, text: str) -> Optional[str]:
        """
        Parsuje datum a čas z přirozeného jazyka
        
        Args:
            text: Text obsahující časové údaje
            
        Returns:
            ISO formát datetime nebo None
        """
        text_lower = text.lower()
        now = datetime.now()
        
        # Detekce dne
        target_date = None
        
        # Relativní dny (dnes, zítra, pozítří)
        for keyword, days_offset in self.day_keywords.items():
            if days_offset is not None and keyword in text_lower:
                target_date = now + timedelta(days=days_offset)
                break
        
        # Dny v týdnu
        if not target_date:
            weekdays = {
                'pondělí': 0, 'úterý': 1, 'středa': 2, 'středu': 2,
                'čtvrtek': 3, 'pátek': 4, 'sobota': 5, 'neděle': 6
            }
            
            for day_name, weekday in weekdays.items():
                if day_name in text_lower:
                    # Najdi nejbližší výskyt tohoto dne v týdnu
                    days_ahead = weekday - now.weekday()
                    if days_ahead <= 0:
                        days_ahead += 7
                    target_date = now + timedelta(days=days_ahead)
                    break
        
        # Pokud není den specifikován, použij zítřek
        if not target_date:
            target_date = now + timedelta(days=1)
        
        # Detekce času
        target_time = None
        
        # Číselný čas (např. "ve 3", "v 15:00", "14:30")
        time_patterns = [
            r've?\s*(\d{1,2}):(\d{2})',  # "ve 14:30", "v 9:00"
            r've?\s*(\d{1,2})\s*hodin',  # "ve 3 hodiny"
            r've?\s*(\d{1,2})',          # "ve 3", "v 15"
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if len(match.groups()) > 1 and match.group(2) else 0
                
                # Pokud je čas < 8, předpokládej odpoledne (15 = 3 odpoledne)
                if hour < 8:
                    hour += 12
                
                target_time = f"{hour:02d}:{minute:02d}"
                break
        
        # Slovní označení času
        if not target_time:
            for keyword, time_str in self.time_keywords.items():
                if keyword in text_lower:
                    target_time = time_str
                    break
        
        # Výchozí čas pokud není specifikován
        if not target_time:
            target_time = "14:00"
        
        # Složení datetime
        datetime_str = f"{target_date.strftime('%Y-%m-%d')} {target_time}:00"
        
        try:
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            return dt.isoformat()
        except ValueError:
            return None
    
    def suggest_meeting_time(self, requested_time: str) -> Dict:
        """
        Navrhne čas schůzky nebo alternativy
        
        Args:
            requested_time: Požadovaný čas (ISO format)
            
        Returns:
            Dict s výsledkem: {
                'available': bool,
                'datetime': str,
                'conflicts': list,
                'alternatives': list,
                'blocked': dict nebo None
            }
        """
        # Kontrola blokovaných časů
        blocked = self.db.is_time_blocked(requested_time)
        if blocked:
            alternatives = self._generate_alternatives(requested_time, 3)
            return {
                'available': False,
                'datetime': requested_time,
                'blocked': blocked,
                'conflicts': [],
                'alternatives': alternatives
            }
        
        # Kontrola konfliktů
        conflicts = self.db.check_conflicts(requested_time, self.min_spacing_hours)
        
        if conflicts:
            alternatives = self._generate_alternatives(requested_time, 3)
            return {
                'available': False,
                'datetime': requested_time,
                'blocked': None,
                'conflicts': conflicts,
                'alternatives': alternatives
            }
        
        # Čas je dostupný
        return {
            'available': True,
            'datetime': requested_time,
            'blocked': None,
            'conflicts': [],
            'alternatives': []
        }
    
    def _generate_alternatives(self, requested_time: str, count: int = 3) -> List[str]:
        """
        Vygeneruje alternativní termíny
        
        Args:
            requested_time: Původní požadovaný čas
            count: Počet alternativ
            
        Returns:
            Seznam alternativních časů (ISO format)
        """
        try:
            dt = datetime.fromisoformat(requested_time)
        except ValueError:
            return []
        
        alternatives = []
        
        # Hledej další dostupné časy
        for days_offset in range(1, 14):  # Hledej až 2 týdny dopředu
            for hour_offset in [0, 1, 2, -1, -2]:  # Zkus různé časy
                candidate_dt = dt + timedelta(days=days_offset, hours=hour_offset)
                
                # Pracovní doba (8-18)
                if candidate_dt.hour < 8 or candidate_dt.hour > 18:
                    continue
                
                candidate_iso = candidate_dt.isoformat()
                
                # Zkontroluj dostupnost
                if (not self.db.is_time_blocked(candidate_iso) and
                    not self.db.check_conflicts(candidate_iso, self.min_spacing_hours)):
                    alternatives.append(candidate_iso)
                    
                    if len(alternatives) >= count:
                        return alternatives
        
        return alternatives
    
    def schedule_meeting(self, contact_name: str, contact_phone: str,
                        meeting_datetime: str, location_type: str = None,
                        location_details: str = None, followup_person: str = "Ondřej",
                        notes: str = None, call_sid: str = None) -> int:
        """
        Naplánuje schůzku
        
        Args:
            contact_name: Jméno kontaktu
            contact_phone: Telefon
            meeting_datetime: Čas schůzky (ISO format)
            location_type: Typ místa
            location_details: Detaily místa
            followup_person: Kdo bude následovat
            notes: Poznámky
            call_sid: ID hovoru
            
        Returns:
            ID nové schůzky
        """
        return self.db.add_meeting(
            contact_name=contact_name,
            contact_phone=contact_phone,
            meeting_datetime=meeting_datetime,
            location_type=location_type,
            location_details=location_details,
            followup_person=followup_person,
            notes=notes,
            call_sid=call_sid
        )
    
    def format_datetime_czech(self, datetime_iso: str) -> str:
        """
        Formátuje datetime do českého formátu pro AI odpověď
        
        Args:
            datetime_iso: ISO format datetime
            
        Returns:
            Český formát (např. "středa 15. ledna ve 14:00")
        """
        try:
            dt = datetime.fromisoformat(datetime_iso)
        except ValueError:
            return datetime_iso
        
        # České názvy dnů
        weekdays = ['pondělí', 'úterý', 'středa', 'čtvrtek', 
                   'pátek', 'sobota', 'neděle']
        
        # České názvy měsíců (2. pád)
        months = ['ledna', 'února', 'března', 'dubna', 'května', 'června',
                 'července', 'srpna', 'září', 'října', 'listopadu', 'prosince']
        
        weekday = weekdays[dt.weekday()]
        day = dt.day
        month = months[dt.month - 1]
        hour = dt.hour
        minute = dt.minute
        
        return f"{weekday} {day}. {month} ve {hour}:{minute:02d}"
    
    def get_upcoming_meetings(self, days: int = 7) -> List[Dict]:
        """
        Získá nadcházející schůzky
        
        Args:
            days: Počet dní dopředu
            
        Returns:
            Seznam nadcházejících schůzek
        """
        now = datetime.now()
        end_date = now + timedelta(days=days)
        
        return self.db.get_meetings(
            status='scheduled',
            from_date=now.isoformat(),
            to_date=end_date.isoformat()
        )
    
    def generate_ai_response(self, request_text: str) -> str:
        """
        Vygeneruje AI odpověď na požadavek schůzky
        
        Args:
            request_text: Text požadavku od zákazníka
            
        Returns:
            Vhodná odpověď AI
        """
        # Parsuj čas z požadavku
        requested_time = self.parse_time_from_text(request_text)
        
        if not requested_time:
            return "Kdy byste měl čas? Mohu nabídnout termín zítra odpoledne ve 14:00."
        
        # Zkontroluj dostupnost
        result = self.suggest_meeting_time(requested_time)
        
        if result['available']:
            formatted_time = self.format_datetime_czech(requested_time)
            return f"Výborně! {formatted_time} mám volno. Kde byste preferoval schůzku - u vás, u nás nebo online?"
        
        # Není dostupné - nabídni alternativy
        formatted_requested = self.format_datetime_czech(requested_time)
        
        if result['blocked']:
            reason = result['blocked'].get('reason', 'obsazený čas')
            response = f"Bohužel {formatted_requested} nemám čas ({reason}). "
        else:
            response = f"Bohužel {formatted_requested} už mám schůzku. "
        
        # Přidej alternativy
        if result['alternatives']:
            alt1 = self.format_datetime_czech(result['alternatives'][0])
            response += f"Šlo by {alt1}"
            
            if len(result['alternatives']) > 1:
                alt2 = self.format_datetime_czech(result['alternatives'][1])
                response += f" nebo {alt2}"
            
            response += "?"
        else:
            response += "Nejbližší volno mám až za týden."
        
        return response
