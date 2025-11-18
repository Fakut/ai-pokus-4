"""
Text-to-Speech engine
Prevadi text na rec pomoci ElevenLabs s podporou ceskeho jazyka
"""

import os
import re
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from config import Config


class TTSEngine:
    """Engine pro generovani reci z textu"""
    
    def __init__(self):
        print("Inicializuji TTSEngine...")
        try:
            self.client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)
            self._ensure_cache_dir()
            print("  OK: TTSEngine initialized")
        except Exception as e:
            print(f"  ERROR: TTSEngine: {e}")
            raise
    
    
    def _normalize_czech_text(self, text):
        """
        Normalizuje text pro správné vyslovení v češtině
        - Čísla na slova
        - Zkratky na slova
        - Čas na čitatelný formát
        
        POZNÁMKA: Zkratky jsou nebezpečné (mohou pokazit slova),
        tak je nahrazujeme POUZE pokud mají tečku a jsou obklopeny mezerou
        """
        normalized = text
        
        # ČASY - 14:00 -> čtrnáct hodin
        normalized = re.sub(r'(\d{1,2}):(\d{2})', lambda m: self._time_to_words(m.group(1), m.group(2)), normalized)
        
        # ČÍSLA NA KONCI VĚTY - "3." -> "3"
        normalized = re.sub(r'(\d)\.(\s|$)', r'\1\2', normalized)
        
        # JEDNOCIFERNA ČÍSLA v textu - "5 produktů" -> "pět produktů"
        normalized = re.sub(r'\b([0-9])\b', lambda m: self._number_to_words(int(m.group(1))), normalized)
        
        # VĚTŠÍ ČÍSLA - "250 Kč" -> "dvěstě padesát korun"
        normalized = re.sub(r'\b(\d{2,3})(?:\s*Kč)?\b', lambda m: self._number_to_words(int(m.group(1))), normalized)
        
        # Zkratky - POUZE pokud jsou obklopeny mezerou a mají tečku
        # To předchází zničení běžných slov
        zkratky_regex = [
            (r'\s+atd\.\s+', ' a tak dále ', re.IGNORECASE),
            (r'\s+apod\.\s+', ' a podobně ', re.IGNORECASE),
            (r'\s+tj\.\s+', ' to jest ', re.IGNORECASE),
            (r'^atd\.\s+', 'a tak dále ', re.IGNORECASE),
            (r'^apod\.\s+', 'a podobně ', re.IGNORECASE),
        ]
        
        for pattern, replacement, flags in zkratky_regex:
            normalized = re.sub(pattern, replacement, normalized, flags=flags)
        
        # Malá optimalizace: "+" -> "plus", "&" -> "a"
        normalized = normalized.replace(' + ', ' plus ')
        normalized = normalized.replace(' & ', ' a ')
        
        return normalized
    
    def _time_to_words(self, hours, minutes):
        """Konvertuje čas 14:30 na 'čtrnáct hodin třicet minut'"""
        hours_words = self._number_to_words(int(hours))
        
        if minutes == '00':
            return f"{hours_words} hodin"
        elif minutes == '30':
            return f"v půl {self._number_to_words(int(hours) + 1)}"
        else:
            minutes_words = self._number_to_words(int(minutes))
            return f"{hours_words} hodin {minutes_words} minut"
    
    def _number_to_words(self, num):
        """Konvertuje číslo na slova (základní)"""
        ones = ["nula", "jedna", "dva", "tři", "čtyři", "pět", "šest", "sedm", "osm", "devět"]
        teens = ["deset", "jedenáct", "dvanáct", "třináct", "čtrnáct", "patnáct", "šestnáct", "sedmnáct", "osmnáct", "devatenáct"]
        tens = ["", "", "dvacet", "třicet", "čtyřicet", "padesát", "šedesát", "sedmdesát", "osmdesát", "devadesát"]
        
        if num < 10:
            return ones[num]
        elif num < 20:
            return teens[num - 10]
        elif num < 100:
            return tens[num // 10] + ("" if num % 10 == 0 else " " + ones[num % 10])
        else:
            return str(num)  # Fallback pro větší čísla
    
    def generate(self, text, use_cache=True):
        """Vygeneruje audio z textu"""
        print(f"\n[TTSEngine] generate('{text[:50]}...')")
        
        try:
            # NORMALIZACE CESKEHO TEXTU
            normalized_text = self._normalize_czech_text(text)
            print(f"  Normalized: '{normalized_text[:60]}...'")
            
            cache_file = self._get_cache_path(normalized_text)
            
            if use_cache and os.path.exists(cache_file):
                print(f"  Cache hit: {cache_file}")
                return self._get_url_from_path(cache_file)
            
            print("  Generating audio...")
            
            # OPTIMALIZACE: Nizsi latence + streaming
            audio_gen = self.client.text_to_speech.convert(
                voice_id=Config.ELEVENLABS_VOICE_ID,
                optimize_streaming_latency="2",  # Nejrychlejší streaming (1-3, nižší = rychlejší)
                text=normalized_text,
                model_id="eleven_turbo_v2_5",  # Nejrychlejší model
                voice_settings=VoiceSettings(
                    stability=0.3,  # Nižší = méně detailů = rychlejší
                    similarity_boost=0.7,
                    style=0.0,
                    use_speaker_boost=False,  # Vypnuto = rychlejší
                ),
            )
            
            audio_bytes = b"".join(audio_gen)
            
            with open(cache_file, 'wb') as f:
                f.write(audio_bytes)
            
            print(f"  OK: Audio saved: {cache_file} ({len(audio_bytes)} bytes)")
            
            url = self._get_url_from_path(cache_file)
            print(f"  URL: {url}")
            return url
        
        except Exception as e:
            print(f"  ERROR: TTS: {e}")
            return None
    
    def _ensure_cache_dir(self):
        """Vytvori slozku pro cache"""
        os.makedirs(Config.AUDIO_CACHE_DIR, exist_ok=True)
        print(f"  Cache dir: {Config.AUDIO_CACHE_DIR}")
    
    def _get_cache_path(self, text):
        """Vrati cestu k cache souboru"""
        filename = f"tts_{abs(hash(text))}.mp3"
        return os.path.join(Config.AUDIO_CACHE_DIR, filename)
    
    def _get_url_from_path(self, path):
        """Prevede filepath na URL"""
        # OPRAV: Normalizuj cestu pro URL (pouzij forward slash)
        # Odeber prvni "static/" a pridej zpet s forward slash
        path_parts = path.replace(os.sep, '/').split('/')
        
        # Najdi 'static' a vezmi vse za nim
        if 'static' in path_parts:
            static_index = path_parts.index('static')
            relative_path = '/'.join(path_parts[static_index+1:])
            url = f"/static/{relative_path}"
        else:
            # Fallback
            url = f"/{path.replace(os.sep, '/')}"
        
        return url