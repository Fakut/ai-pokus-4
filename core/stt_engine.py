"""
Speech-to-Text engine
Prevadi rec na text pomoci OpenAI Whisper
VYLEPŠENO: Voice Activity Detection, Noise Gate, Audio Enhancement
"""

import tempfile
import wave
import pyaudio
import numpy as np
from openai import OpenAI
from config import Config
import struct


class STTEngine:
    """Engine pro rozpoznavani reci s audio procesovani"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.rate = 16000
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        
        # Audio processing parameters
        self.noise_gate_threshold = -40  # dB (pokud je hlasitejsi = hluk)
        self.vad_sensitivity = 0.3  # 0-1 (0.3 = citlivy)
        self.min_speech_duration = 0.3  # sec (min doba reci)
        self.silence_threshold = 0.5  # sec (ticho = konec)
    
    def _bytes_to_np(self, audio_bytes):
        """Konvertuj raw bytes na numpy array (16-bit audio)"""
        audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
        # Normalizuj na -1 to 1
        audio_float = audio_data.astype(np.float32) / 32768.0
        return audio_float
    
    def _np_to_bytes(self, audio_np):
        """Konvertuj numpy array zpet na raw bytes"""
        # Normalizuj aby nevyslo moc 
        audio_np = np.clip(audio_np, -1.0, 1.0)
        audio_int16 = (audio_np * 32767.0).astype(np.int16)
        return audio_int16.tobytes()
    
    def _get_audio_level(self, audio_bytes):
        """Ziska aktualni hlasitost (RMS v dB)"""
        audio = self._bytes_to_np(audio_bytes)
        rms = np.sqrt(np.mean(audio ** 2))
        
        # Prevod na dB (20 * log10(RMS))
        if rms > 0:
            db = 20 * np.log10(rms)
        else:
            db = -100
        
        return db
    
    def _detect_voice_activity(self, audio_bytes):
        """
        Detekuje jestli je v audio hlasy/rec
        Vraci: True pokud je zrejme rec, False pokud je ticho/sumu
        """
        db = self._get_audio_level(audio_bytes)
        
        # Je to rec pokud je hlasitejsi nez noise gate
        is_speech = db > self.noise_gate_threshold
        
        return is_speech
    
    def _apply_noise_gate(self, audio_bytes):
        """
        Aplikuje noise gate - ticha audio pod threshold se ztlumi
        Pomaha odstranat:
        - Hum z mikrofonu
        - Tichy sumu
        - Pozadi hluk
        """
        audio = self._bytes_to_np(audio_bytes)
        db = self._get_audio_level(audio_bytes)
        
        if db < self.noise_gate_threshold:
            # Je to pod threshold - ztlum (nebo smaž)
            audio = audio * 0.1  # Zmen na 10% hlasitosti
        
        return self._np_to_bytes(audio)
    
    def _apply_noise_reduction(self, audio_bytes):
        """
        Jednoducha sumu redukce:
        - Detekuj tisty sumu
        - Odecti ho z signalu
        (Spectral Subtraction light version)
        """
        audio = self._bytes_to_np(audio_bytes)
        
        # Ziskej spektrum (jednoduche)
        # Spocitej RMS
        rms = np.sqrt(np.mean(audio ** 2))
        
        # Pokud je signal maly - zvys noise gate
        if rms < 0.1:
            # Velmi tiche - pravdepodobne hlavne sum
            # Zniz amplitudu
            audio = audio * 0.5
        
        return self._np_to_bytes(audio)
    
    def _amplify_quiet_audio(self, audio_bytes, target_db=-20):
        """
        Zesili tiche audio aby bylo lepe slysiie
        
        Args:
            audio_bytes: Raw audio
            target_db: Cilova hlasitost v dB
        """
        audio = self._bytes_to_np(audio_bytes)
        current_db = self._get_audio_level(audio_bytes)
        
        # Kolik DB potrebujem zvysit?
        gain_db = target_db - current_db
        
        # Prevod dB na multiplikator
        # 6 dB = 2x hlasitejsi, -6 dB = 0.5x
        gain_linear = 10 ** (gain_db / 20.0)
        
        # Aplikuj gain ale ne moc abys neporusil
        gain_linear = np.clip(gain_linear, 0.5, 4.0)  # Max 4x zesili
        
        audio = audio * gain_linear
        
        return self._np_to_bytes(audio)
    
    def _enhance_audio(self, audio_bytes):
        """
        Komplexni audio enhancement pipeline:
        1. Noise gate - odstrani sumu pod prahem
        2. Noise reduction - lehka spektralni subtrakce
        3. Amplifikace - zesli ticha audio
        """
        # 1. Zeni sumu
        enhanced = self._apply_noise_gate(audio_bytes)
        
        # 2. Lehka sumu redukce
        enhanced = self._apply_noise_reduction(enhanced)
        
        # 3. Zesili tiche audio
        enhanced = self._amplify_quiet_audio(enhanced, target_db=-20)
        
        return enhanced
    
    def listen(self, duration=5):
        """
        Nahraje audio a prevede na text
        VYLEPŠENO: Voice Activity Detection, Noise Processing
        
        Args:
            duration: Delka nahravani v sekundach
            
        Returns:
            str: Rozpoznany text
        """
        print(f"Listening {duration}s (with noise processing)...")
        
        audio_interface = pyaudio.PyAudio()
        
        try:
            # Nahravani
            stream = audio_interface.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            frames = []
            speech_detected_frames = 0
            max_frames = int(self.rate / self.chunk * duration)
            
            for i in range(0, max_frames):
                data = stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
                
                # VAD - detekuj kdy je rec
                is_speech = self._detect_voice_activity(data)
                
                if is_speech:
                    speech_detected_frames += 1
                    print(".", end="", flush=True)
                else:
                    print("-", end="", flush=True)
            
            print(" OK")
            
            stream.stop_stream()
            stream.close()
            
            # Ulozeni do docasneho souboru (s audio enhancement)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
                temp_path = temp.name
                
                wf = wave.open(temp_path, 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(audio_interface.get_sample_size(self.format))
                wf.setframerate(self.rate)
                
                # Aplikuj audio enhancement na kazdy frame
                enhanced_frames = []
                for frame in frames:
                    enhanced = self._enhance_audio(frame)
                    enhanced_frames.append(enhanced)
                
                wf.writeframes(b''.join(enhanced_frames))
                wf.close()
            
            # Prepis pomoci Whisper
            print("Processing with Whisper (Czech, no translation)...")
            
            with open(temp_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="cs",  # Czech!
                    temperature=0.0  # Presneji rozpoznavat
                )
            
            # Smazani docasneho souboru
            import os
            os.unlink(temp_path)
            
            text = transcript.text.strip()
            
            # Info o detekci
            speech_percentage = (speech_detected_frames / max_frames) * 100
            print(f"Speech detected: {speech_percentage:.1f}%")
            print(f"Recognized: '{text}'")
            
            # ✅ NOVÉ: Agresivní halucinace prevence
            
            # 1. Pokud je málo řeči (<30%), vrátit None
            if speech_percentage < 30:
                print(f"  ⚠️  Málo řeči ({speech_percentage:.1f}%) - ignoruji")
                return None
            
            # 2. Pokud je výstup nesmyslný - detekuj halucinaci
            # Halucinace znaky: krátký text, anglické slova bez diakritiky
            if text and len(text) < 5:
                # Příliš krátko - pravděpodobně halucinace
                print(f"  ⚠️  Text příliš krátký '{text}' - ignoruji")
                return None
            
            # 3. Detekuj anglické halucinace (slova bez diakritiky v českém kontextu)
            czech_chars = set('áčďéěíľňóôřšťůúýž')
            english_keywords = ['hello', 'thank', 'ok', 'yes', 'no', 'bye', 'call', 'please']
            
            if text:
                text_lower = text.lower()
                # Pokud obsahuje anglické slovo + žádné české znaky = halucinace
                has_czech = any(c in text_lower for c in czech_chars)
                has_english = any(keyword in text_lower for keyword in english_keywords)
                
                if has_english and not has_czech and len(text) < 20:
                    print(f"  ⚠️  Anglická halucinace '{text}' - ignoruji")
                    return None
            
            return text if text else None
            
        except Exception as e:
            print(f"ERROR STT: {e}")
            return None
            
        finally:
            audio_interface.terminate()