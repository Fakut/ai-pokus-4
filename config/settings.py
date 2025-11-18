"""
Hlavni konfigurace aplikace
Obsahuje nastaveni API klicu a globalnich parametru
OPTIMALIZOVANO PRO RAPID COLD CALLING (30 cisel)
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Zakladni konfigurace aplikace"""
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # ElevenLabs
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', 'pFZP5JQG7iQjIQuC4Bku')
    
    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # Databaze
    DB_PATH = 'data/calls.db'
    
    # Audio cache - OPTIMALIZOVANO PRO SPEED
    AUDIO_CACHE_DIR = 'static/audio'
    CACHE_ENABLED = True  # Vymeni se cache pro 30 cisel
    
    # Konverzace - KRATSI ODPOVEDI = RYCHLEJSI ZPRACOVANI
    MAX_HISTORY = 10
    MAX_TOKENS = 40  # Zkráceno z 60 na 40 - kratší odpovědi = rychlejší TTS
    TEMPERATURE = 0.7
    
    # Server
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 5000
    DEBUG = False  # Vypnuto pro zvýšení výkonu

class CallConfig:
    """Konfigurace pro cold calling - OPTIMALIZOVANO NA 30 CISEL"""
    
    # Rate limiting - PRO RYCHLOST
    CALLS_PER_MINUTE = 6  # Zvýšeno z 4 na 6 (10s delay místo 15s)
    MAX_CALL_DURATION = 120  # Zkráceno z 180 - cold call obvykle <= 2 min
    
    # Retry
    RETRY_FAILED = True
    MAX_RETRIES = 1  # Zkráceno z 2 - ekonomizujeme čas
    RETRY_DELAY = 180  # Zkráceno z 300
    
    # Volaci hodiny - PRO TESTOVANI
    START_HOUR = 8
    END_HOUR = 23
    WORK_DAYS = [0, 1, 2, 3, 4, 5, 6]
    
    # Recording
    RECORD_CALLS = True
    SAVE_TRANSCRIPTS = True
    
    # TTS OPTIMALIZACE - LEAN & MEAN
    TTS_CACHE = True  # Cachuj předem seznam frází
    TTS_BATCH_GENERATE = True  # Generuj TTS audiá v párkách pro 30 kontaktů