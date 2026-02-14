import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import time
import random
import json

app = FastAPI()

# --- Configuration (Key variables for SR&ED experimentation) ---
# [Experiment Log] Lowered the PITCH_THRESHOLD for initial environment calibration
PITCH_THRESHOLD = 300.0  # Adjusted from 100.0 to 300.0 for better human voice detection
STRESS_LIMIT = 50
SAMPLING_RATE = 44100  
TALK_COOLDOWN = 3.0 # Reduced cooldown for more responsive testing

last_talk_time = 0

ANXIETY_RESPONSES = [
    "Are you feeling okay? Would you like a glass of water?",
    "Could you please speak a little more slowly?",
    "Don't worry, I'm here to help you.",
    "Try taking a deep breath.",
    "Is something bothering you? You look a bit uneasy."
]

def ask_fake_brain():
    return random.choice(ANXIETY_RESPONSES)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global last_talk_time
    await websocket.accept()
    print(f"✅ [{time.strftime('%H:%M:%S')}] Connection established with Unity")
    
    try:
        while True:
            data = await websocket.receive_bytes()
            if not data:
                continue
                
            # Convert binary data to float32
            audio_array = np.frombuffer(data, dtype=np.float32)
            if len(audio_array) == 0:
                continue

            # 3. Volume Calculation (RMS-based)
            volume = np.sqrt(np.mean(np.square(audio_array)))
            
            # [CRITICAL FIX] Debug print to see real-time volume levels in terminal
            # This helps to calibrate the sensitivity of our system.
            # print(f"DEBUG: Current Vol: {volume:.4f}") 

            # Noise Filtering: Lowered threshold from 0.02 to 0.005 for high sensitivity
            if volume > 0.005: 
                # 4. Frequency Analysis (FFT)
                fft_spectrum = np.fft.rfft(audio_array)
                freqs = np.fft.rfftfreq(len(audio_array), d=1.0/SAMPLING_RATE)
                magnitude = np.abs(fft_spectrum)
                
                peak_index = np.argmax(magnitude)
                detected_pitch = freqs[peak_index]
                
                # 5. Status Inference Logic
                status = "Relaxed"
                stress_score = 10
                
                # Logic for detecting anxiety based on pitch and volume
                if detected_pitch > PITCH_THRESHOLD:
                    status = "⚠️ ANXIETY"
                    stress_score = 85
                elif volume > 0.1: # Sensitive loud voice detection
                    status = "⚠️ LOUD"
                    stress_score = 70
                
                # 6. AI Feedback Decision (with Cooldown)
                ai_message = ""
                current_time = time.time()
                
                if (status != "Relaxed") and (current_time - last_talk_time > TALK_COOLDOWN):
                    ai_message = ask_fake_brain()
                    last_talk_time = current_time
                    print(f"   [EVENT] {status} (Pitch: {detected_pitch:.1f}Hz, Vol: {volume:.3f}) -> AI: {ai_message}")

                # 7. Send Results to Unity
                response = {
                    "stress_score": stress_score,
                    "pitch": round(float(detected_pitch), 2),
                    "status": status,
                    "volume": round(float(volume), 4),
                    "ai_message": ai_message 
                }
                await websocket.send_json(response)
            
    except WebSocketDisconnect:
        print("❌ Connection closed by Unity.")
    except Exception as e:
        print(f"⚠️ Error occurred: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)