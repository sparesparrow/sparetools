#!/usr/bin/env python3
"""
Enhanced Text-to-Speech Module with Multiple Free Options
Supports pyttsx3, espeak, festival, and gTTS for natural voice synthesis
"""

import os
import sys
import subprocess
import tempfile
import threading
import time

class EnhancedTTS:
    def __init__(self):
        self.available_engines = []
        self.current_engine = None
        self.init_engines()
    
    def init_engines(self):
        """Initialize available TTS engines in order of preference"""
        
        # 1. Try pyttsx3 (offline, good quality)
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            if voices:
                # Prefer female voices for better quality
                for voice in voices:
                    if any(keyword in voice.name.lower() for keyword in ['female', 'zira', 'susan', 'hazel']):
                        engine.setProperty('voice', voice.id)
                        break
                engine.setProperty('rate', 160)
                engine.setProperty('volume', 0.9)
                self.available_engines.append(('pyttsx3', engine))
                print("✅ pyttsx3 TTS engine loaded")
        except Exception as e:
            print(f"⚠️  pyttsx3 not available: {e}")
        
        # 2. Try espeak (offline, system command)
        if self.check_command('espeak'):
            self.available_engines.append(('espeak', None))
            print("✅ espeak TTS engine available")
        
        # 3. Try festival (offline, system command)
        if self.check_command('festival'):
            self.available_engines.append(('festival', None))
            print("✅ festival TTS engine available")
        
        # 4. Try gTTS (online, high quality)
        try:
            from gtts import gTTS
            import pygame
            self.available_engines.append(('gtts', None))
            print("✅ gTTS engine available (requires internet)")
        except Exception as e:
            print(f"⚠️  gTTS not available: {e}")
        
        # Set default engine
        if self.available_engines:
            self.current_engine = self.available_engines[0][0]
            print(f"🎤 Default TTS engine: {self.current_engine}")
        else:
            print("❌ No TTS engines available")
    
    def check_command(self, command):
        """Check if a system command is available"""
        try:
            subprocess.run([command, '--version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def speak_pyttsx3(self, text, engine):
        """Speak using pyttsx3"""
        try:
            engine.say(text)
            engine.runAndWait()
            return True
        except Exception as e:
            print(f"pyttsx3 error: {e}")
            return False
    
    def speak_espeak(self, text):
        """Speak using espeak"""
        try:
            # Use espeak with better voice settings
            cmd = [
                'espeak', 
                '-s', '160',  # Speed
                '-v', 'en+f3',  # Female voice
                '-a', '200',  # Amplitude
                text
            ]
            subprocess.run(cmd, check=True)
            return True
        except Exception as e:
            print(f"espeak error: {e}")
            return False
    
    def speak_festival(self, text):
        """Speak using festival"""
        try:
            # Use festival with better voice
            cmd = ['festival', '--tts']
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
            process.communicate(input=text.encode())
            return True
        except Exception as e:
            print(f"festival error: {e}")
            return False
    
    def speak_gtts(self, text):
        """Speak using gTTS (Google Text-to-Speech)"""
        try:
            from gtts import gTTS
            import pygame
            
            # Initialize pygame mixer if not already done
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            # Create TTS audio
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                
                # Play audio
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()
                
                # Wait for playback to complete
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                # Clean up
                os.unlink(tmp_file.name)
            
            return True
        except Exception as e:
            print(f"gTTS error: {e}")
            return False
    
    def speak(self, text, engine_name=None):
        """Speak text using the specified or best available engine"""
        if not text or not self.available_engines:
            return False
        
        # Use specified engine or current default
        target_engine = engine_name or self.current_engine
        
        # Find the engine
        engine_obj = None
        for name, obj in self.available_engines:
            if name == target_engine:
                engine_obj = obj
                break
        
        if not engine_obj and target_engine != 'espeak' and target_engine != 'festival':
            # Fallback to first available engine
            target_engine = self.available_engines[0][0]
            engine_obj = self.available_engines[0][1]
        
        # Try to speak with the selected engine
        success = False
        
        if target_engine == 'pyttsx3' and engine_obj:
            success = self.speak_pyttsx3(text, engine_obj)
        elif target_engine == 'espeak':
            success = self.speak_espeak(text)
        elif target_engine == 'festival':
            success = self.speak_festival(text)
        elif target_engine == 'gtts':
            success = self.speak_gtts(text)
        
        # If failed, try other engines
        if not success:
            for name, obj in self.available_engines:
                if name != target_engine:
                    if name == 'pyttsx3' and obj:
                        success = self.speak_pyttsx3(text, obj)
                    elif name == 'espeak':
                        success = self.speak_espeak(text)
                    elif name == 'festival':
                        success = self.speak_festival(text)
                    elif name == 'gtts':
                        success = self.speak_gtts(text)
                    
                    if success:
                        break
        
        return success
    
    def speak_async(self, text, engine_name=None):
        """Speak text asynchronously"""
        thread = threading.Thread(target=self.speak, args=(text, engine_name))
        thread.daemon = True
        thread.start()
        return thread
    
    def list_engines(self):
        """List available TTS engines"""
        return [name for name, _ in self.available_engines]
    
    def set_engine(self, engine_name):
        """Set the default TTS engine"""
        if any(name == engine_name for name, _ in self.available_engines):
            self.current_engine = engine_name
            return True
        return False

# Test function
if __name__ == "__main__":
    tts = EnhancedTTS()
    print(f"Available engines: {tts.list_engines()}")
    
    if tts.available_engines:
        print("Testing TTS...")
        tts.speak("Hello, this is a test of the enhanced text to speech system.")
    else:
        print("No TTS engines available")
