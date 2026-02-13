import customtkinter as ctk
import sounddevice as sd
from faster_whisper import WhisperModel
import threading
import numpy as np
import torch
import time
import language_tool_python
import subprocess
from pynput import keyboard
from pynput.keyboard import Key
from collections import deque
import random

class SimpleApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WhisperDrop")
        self.geometry("160x210")
        self.attributes('-topmost', True)
        self.configure(fg_color="#111111")
        self.overrideredirect(True)

        # Make window draggable
        self.bind('<Button-1>', self.click_window)
        self.bind('<B1-Motion>', self.drag_window)

        # Set appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Position window in bottom right corner
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = screen_width - 200
        y = screen_height - 260
        self.geometry(f"+{x}+{y}")

        # Main frame - dark background
        self.main_frame = ctk.CTkFrame(self, fg_color="#111111", corner_radius=12,
                                        border_width=1, border_color="#2a2a2a")
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Title bar with close button
        self.title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=20)
        self.title_frame.pack(fill="x", padx=6, pady=(4, 0))
        self.title_frame.pack_propagate(False)

        self.title_label = ctk.CTkLabel(
            self.title_frame, text="WhisperDrop",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color="#505050"
        )
        self.title_label.pack(side="left")

        self.close_button = ctk.CTkButton(
            self.title_frame, text="x", width=16, height=16,
            font=ctk.CTkFont(size=9), fg_color="transparent",
            hover_color="#333333", text_color="#505050",
            command=self.on_closing, corner_radius=4
        )
        self.close_button.pack(side="right")

        # Status label
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Loading...",
            font=ctk.CTkFont(size=10),
            text_color="#606060"
        )
        self.status_label.pack(pady=(2, 4))

        # Waveform canvas
        self.canvas_width = 140
        self.canvas_height = 100
        self.canvas = ctk.CTkCanvas(
            self.main_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#0a0a0a",
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(pady=(0, 6))

        # Record button - compact pill shape
        self.record_button = ctk.CTkButton(
            self.main_frame,
            text="REC",
            command=self.toggle_recording,
            font=ctk.CTkFont(size=11, weight="bold"),
            height=30,
            width=100,
            corner_radius=15,
            fg_color="#1a1a2e",
            hover_color="#222244",
            text_color="#7a7aff",
            border_width=1,
            border_color="#2a2a4e"
        )
        self.record_button.pack(pady=(0, 6))

        # Waveform parameters
        self.num_bars = 15
        self.bar_width = 6
        self.bar_spacing = 3
        self.waveform_bars = []
        self.audio_levels = deque(maxlen=self.num_bars)
        
        # Initialize waveform
        self.init_waveform()
        
        # Recording state
        self.is_recording = False
        self.audio_frames = []
        self.samplerate = 16000
        self.channels = 1
        
        # Audio monitoring
        self.audio_level = 0
        self.last_levels = deque(maxlen=5)
        
        # Fixed settings
        self.model_name = "small"
        self.auto_insert = True
        self.grammar_correction = True
        self.immediate_insert = True
        
        # Initialize grammar tool
        self.grammar_tool = None
        
        # Global hotkey
        self.hotkey = Key.f8
        self.setup_global_hotkey()
        
        # Load model
        self.model = None
        threading.Thread(target=self.load_model, daemon=True).start()
        
    def init_waveform(self):
        """Initialize waveform bars"""
        self.waveform_bars = []
        self.audio_levels.clear()
        
        # Calculate starting position
        total_width = self.num_bars * self.bar_width + (self.num_bars - 1) * self.bar_spacing
        start_x = (self.canvas_width - total_width) // 2
        
        for i in range(self.num_bars):
            x = start_x + i * (self.bar_width + self.bar_spacing)
            
            # Create bar (initially flat)
            bar = self.canvas.create_rectangle(
                x, self.canvas_height // 2 - 1,
                x + self.bar_width, self.canvas_height // 2 + 1,
                fill="#1e1e3a",
                outline=""
            )
            self.waveform_bars.append(bar)
            self.audio_levels.append(0)
    
    def update_waveform(self, audio_level):
        """Update waveform bars based on audio level"""
        if not self.is_recording:
            return
            
        # Normalize audio level
        normalized_level = min(audio_level / 3000, 1.0)
        
        # Add some smoothing
        self.last_levels.append(normalized_level)
        smooth_level = sum(self.last_levels) / len(self.last_levels)
        
        # Shift existing levels and add new one
        self.audio_levels.append(smooth_level)
        
        # Update bars
        for i, (bar, level) in enumerate(zip(self.waveform_bars, self.audio_levels)):
            # Add some randomness for natural look
            random_factor = 0.7 + random.random() * 0.6
            display_level = level * random_factor
            
            # Calculate bar height (minimum 3 pixels, max based on canvas)
            bar_height = max(3, int(display_level * (self.canvas_height - 10)))
            
            # Calculate bar position
            start_x = (self.canvas_width - (self.num_bars * (self.bar_width + self.bar_spacing) - self.bar_spacing)) // 2
            x = start_x + i * (self.bar_width + self.bar_spacing)
            
            y1 = (self.canvas_height - bar_height) // 2
            y2 = y1 + bar_height
            
            # Update bar
            self.canvas.coords(bar, x, y1, x + self.bar_width, y2)
            
            # Color based on level - muted dark tones
            if display_level > 0.7:
                color = "#cc4455"  # Muted red
            elif display_level > 0.4:
                color = "#5b7fff"  # Soft blue
            elif display_level > 0.1:
                color = "#3a3a7a"  # Dark indigo
            else:
                color = "#1e1e3a"  # Very dark
                
            self.canvas.itemconfig(bar, fill=color)
    
    def reset_waveform(self):
        """Reset waveform to idle state"""
        self.audio_levels.clear()
        for i in range(self.num_bars):
            self.audio_levels.append(0)
            
        for bar in self.waveform_bars:
            # Reset to flat line
            start_x = (self.canvas_width - (self.num_bars * (self.bar_width + self.bar_spacing) - self.bar_spacing)) // 2
            i = self.waveform_bars.index(bar)
            x = start_x + i * (self.bar_width + self.bar_spacing)
            
            self.canvas.coords(bar, x, self.canvas_height // 2 - 1,
                             x + self.bar_width, self.canvas_height // 2 + 1)
            self.canvas.itemconfig(bar, fill="#1e1e3a")
    
    def click_window(self, event):
        self.offset_x = event.x
        self.offset_y = event.y
    
    def drag_window(self, event):
        x = self.winfo_pointerx() - self.offset_x
        y = self.winfo_pointery() - self.offset_y
        self.geometry(f'+{x}+{y}')
    
    def setup_global_hotkey(self):
        """Set up global hotkey"""
        try:
            self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
            self.keyboard_listener.start()
            print("✅ Global hotkey listener started (F8)")
        except Exception as e:
            print(f"❌ Failed to start hotkey listener: {e}")
    
    def on_key_press(self, key):
        """Handle key press events"""
        try:
            if key == self.hotkey:
                print("🎯 F8 hotkey detected!")
                self.after(0, self.toggle_recording)
        except:
            pass
    
    def load_model(self):
        """Load Whisper model"""
        try:
            print(f"Loading model: {self.model_name}")
            self.after(0, lambda: self.status_label.configure(text="Loading model..."))
            
            # Try CUDA first
            try:
                device = "cuda"
                compute_type = "float16"
                self.model = WhisperModel(self.model_name, device=device, compute_type=compute_type)
                self.device_used = "CUDA"
                print(f"Using CUDA with {self.model_name}")
            except:
                device = "cpu"
                compute_type = "int8"
                self.model = WhisperModel(self.model_name, device=device, compute_type=compute_type)
                self.device_used = "CPU"
                print(f"Using CPU with {self.model_name}")
            
            self.after(0, lambda: self.status_label.configure(text=f"Ready • {self.device_used}", text_color="#606060"))
            
            # Initialize grammar tool
            self.init_grammar_tool()
            
        except Exception as e:
            print(f"Error loading model: {e}")
            self.after(0, lambda: self.status_label.configure(text="Error", text_color="#cc4455"))
    
    def init_grammar_tool(self):
        """Initialize grammar correction tool"""
        try:
            print("🔧 Initializing grammar tool...")
            self.grammar_tool = language_tool_python.LanguageTool('en-US')
            # Warmup call - first call is slow (~3-4s) due to Java JVM startup
            self.grammar_tool.correct("warmup")
            print("✅ Grammar tool ready!")
        except Exception as e:
            print(f"Grammar tool error: {e}")
            self.grammar_correction = False
    
    def toggle_recording(self):
        """Toggle recording state"""
        if self.model is None:
            print("Model not loaded yet!")
            return
            
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """Start recording"""
        self.is_recording = True
        
        # Update button
        self.record_button.configure(
            text="STOP",
            fg_color="#2a1520",
            hover_color="#3a1a2a",
            text_color="#cc4455",
            border_color="#4a2030"
        )
        
        # Update status
        self.status_label.configure(text="Recording...", text_color="#cc4455")
        
        # Clear audio
        self.audio_frames = []
        self.last_levels.clear()
        
        # Start recording
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.start()
        
        # Start audio monitoring
        self.audio_monitor_thread = threading.Thread(target=self.monitor_audio_level)
        self.audio_monitor_thread.start()
    
    def stop_recording(self):
        """Stop recording"""
        self.is_recording = False
        
        # Update button
        self.record_button.configure(
            text="REC",
            fg_color="#1a1a2e",
            hover_color="#222244",
            text_color="#7a7aff",
            border_color="#2a2a4e"
        )
        
        # Reset waveform
        self.reset_waveform()
        
        # Update status
        self.status_label.configure(text="Processing...", text_color="#8a7a40")
        
        # Wait for recording to finish
        if hasattr(self, 'recording_thread'):
            self.recording_thread.join()
        
        # Process audio
        threading.Thread(target=self.process_audio, daemon=True).start()
    
    def record_audio(self):
        """Record audio from microphone"""
        print("🎧 Starting audio recording...")
        try:
            with sd.InputStream(samplerate=self.samplerate, channels=self.channels, dtype='int16') as stream:
                while self.is_recording:
                    audio_chunk, overflowed = stream.read(1024)
                    self.audio_frames.append(audio_chunk)
                    self.audio_level = np.abs(audio_chunk).mean()
        except Exception as e:
            print(f"Recording error: {e}")
            self.after(0, lambda: self.status_label.configure(text="Mic Error", text_color="#cc4455"))
    
    def monitor_audio_level(self):
        """Monitor audio level for waveform"""
        while self.is_recording:
            if self.audio_level > 0:
                self.after(0, lambda level=self.audio_level: self.update_waveform(level))
            time.sleep(0.05)  # 20 FPS
    
    def process_audio(self):
        """Process recorded audio"""
        if not self.audio_frames:
            self.after(0, lambda: self.status_label.configure(text="No audio", text_color="#cc4455"))
            return

        try:
            # Concatenate audio and convert to float32 normalized [-1, 1]
            audio_data = np.concatenate(self.audio_frames, axis=0)
            audio_float = audio_data.flatten().astype(np.float32) / 32768.0

            # Transcribe directly from numpy array (no file I/O)
            segments, info = self.model.transcribe(
                audio_float,
                beam_size=1,
                language="en",
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=300),
            )

            transcription = " ".join(segment.text.strip() for segment in segments).strip()

            if transcription:
                # Grammar correction
                if self.grammar_correction and self.grammar_tool:
                    transcription = self.correct_grammar(transcription)

                # Insert immediately
                self.after(0, lambda: self.status_label.configure(text="Inserting...", text_color="#3a7a5a"))
                self.after(0, lambda: self.insert_text(transcription))
            else:
                self.after(0, lambda: self.status_label.configure(text="No speech", text_color="#404040"))

        except Exception as e:
            print(f"Processing error: {e}")
            self.after(0, lambda: self.status_label.configure(text="Error", text_color="#cc4455"))
    
    def correct_grammar(self, text):
        """Apply grammar correction"""
        try:
            corrected = self.grammar_tool.correct(text)
            if corrected != text:
                print(f"Grammar: '{text}' → '{corrected}'")
            return corrected
        except Exception as e:
            print(f"Grammar error: {e}")
            return text
    
    def insert_text(self, text):
        """Insert text at cursor using xdotool (fast and reliable)"""
        try:
            # xdotool type with no delay - much faster than pyautogui char-by-char
            subprocess.run(
                ['xdotool', 'type', '--clearmodifiers', '--delay', '0', text + ' '],
                timeout=5
            )

            self.status_label.configure(text="Inserted!", text_color="#3a7a5a")
            print(f"✅ Inserted: {text}")

            # Reset status after 2 seconds
            self.after(2000, lambda: self.status_label.configure(
                text=f"Ready • {self.device_used}",
                text_color="#606060"
            ))
        except Exception as e:
            print(f"Insert error: {e}")
            self.status_label.configure(text="Insert failed", text_color="#cc4455")
    
    def cleanup(self):
        """Clean up resources"""
        self.is_recording = False
        
        if hasattr(self, 'keyboard_listener'):
            try:
                self.keyboard_listener.stop()
            except:
                pass
        
        if self.grammar_tool:
            try:
                self.grammar_tool.close()
            except:
                pass
        
    def on_closing(self):
        """Handle window closing"""
        self.cleanup()
        self.destroy()


if __name__ == "__main__":
    app = SimpleApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()