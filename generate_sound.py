import wave, struct, math
import os

os.makedirs('static/sounds', exist_ok=True)

# Generate a pleasant double-beep for notifications
sampleRate = 44100.0 
frequency1 = 880.0  # A5
frequency2 = 1108.73 # C#6

wavef = wave.open('static/sounds/notification.wav', 'w')
wavef.setnchannels(1) # mono
wavef.setsampwidth(2) 
wavef.setframerate(sampleRate)

def add_tone(freq, duration_sec, volume=0.5):
    for i in range(int(duration_sec * sampleRate)):
        # Apply an exponential decay envelope for a "ping" effect
        envelope = math.exp(-i / (sampleRate * duration_sec * 0.2))
        value = int(volume * 32767.0 * envelope * math.sin(2.0 * math.pi * freq * float(i) / sampleRate))
        data = struct.pack('<h', value)
        wavef.writeframesraw(data)

# Beep 1
add_tone(frequency1, 0.15)
# Silence
def add_silence(duration_sec):
    for i in range(int(duration_sec * sampleRate)):
        wavef.writeframesraw(struct.pack('<h', 0))
add_silence(0.05)
# Beep 2
add_tone(frequency2, 0.3)

wavef.writeframes(b'')
wavef.close()
print("Sound generated at static/sounds/notification.wav")
