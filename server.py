# server.py (무료 버전: 가짜 AI 탑재)
import numpy as np
from fastapi import FastAPI, WebSocket
import uvicorn
import time
import random

app = FastAPI()

# 설정값
PITCH_THRESHOLD = 300.0 
STRESS_LIMIT = 50

# AI가 너무 수다스럽지 않게 쿨타임 설정 (5초에 한 번만 말하기)
last_talk_time = 0
TALK_COOLDOWN = 5.0 

# [가짜 뇌] 미리 준비한 대사 리스트 (돈 안 듦)
ANSIETY_RESPONSES = [
    "손님, 괜찮으세요? 물 한 잔 드릴까요?",
    "조금만 천천히 말씀해 주시겠어요?",
    "너무 걱정하지 마세요, 제가 도와드릴게요.",
    "심호흡을 한번 해보세요.",
    "무슨 일 있으신가요? 표정이 안 좋아 보여요."
]

def ask_fake_brain():
    """
    GPT인 척하면서 랜덤으로 대사를 뽑아주는 함수
    """
    print("🧠 AI Thinking... (Simulation Mode)")
    time.sleep(0.5) # AI가 생각하는 척 0.5초 딜레이
    return random.choice(ANSIETY_RESPONSES)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global last_talk_time
    print("Waiting for connection...")
    await websocket.accept()
    print("✅ System Ready: Simulation Brain Connected")
    
    try:
        while True:
            data = await websocket.receive_bytes()
            audio_array = np.frombuffer(data, dtype=np.float32)
            
            volume = np.sqrt(np.mean(audio_array**2))
            
            if volume > 0.01: 
                # 주파수 분석
                fft_spectrum = np.fft.rfft(audio_array)
                freqs = np.fft.rfftfreq(len(audio_array), d=1.0/44100)
                magnitude = np.abs(fft_spectrum)
                peak_index = np.argmax(magnitude)
                detected_pitch = freqs[peak_index]
                
                status = "Relaxed"
                
                # 상황 판단
                if detected_pitch > PITCH_THRESHOLD:
                    status = "⚠️ ANXIETY"
                elif volume > 0.1:
                    status = "⚠️ LOUD"
                
                # [AI 두뇌 가동] 불안정한 상태이고, 쿨타임이 찼으면 가짜 AI 소환
                ai_message = ""
                current_time = time.time()
                
                if (status != "Relaxed") and (current_time - last_talk_time > TALK_COOLDOWN):
                    ai_message = ask_fake_brain() # 가짜 뇌 사용
                    print(f"🤖 AI Says: {ai_message}") 
                    last_talk_time = current_time

                # Unity로 데이터 전송
                response = {
                    "stress_score": 80 if status != "Relaxed" else 10,
                    "pitch": float(detected_pitch),
                    "status": status,
                    "volume": float(volume),
                    "ai_message": ai_message 
                }
                await websocket.send_json(response)
            
    except Exception as e:
        print(f"Connection closed: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)





# # server.py (립싱크 지원 버전)
# import numpy as np
# from fastapi import FastAPI, WebSocket
# import uvicorn
# from scipy.signal import find_peaks

# app = FastAPI()

# PITCH_THRESHOLD = 300.0 
# STRESS_LIMIT = 50

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     print("Waiting for connection...")
#     await websocket.accept()
#     print("✅ System Ready: Lip Sync & Stress Analysis")
    
#     try:
#         while True:
#             data = await websocket.receive_bytes()
#             audio_array = np.frombuffer(data, dtype=np.float32)
            
#             volume = np.sqrt(np.mean(audio_array**2))
            
#             if volume > 0.01: 
#                 fft_spectrum = np.fft.rfft(audio_array)
#                 freqs = np.fft.rfftfreq(len(audio_array), d=1.0/44100)
#                 magnitude = np.abs(fft_spectrum)
                
#                 peak_index = np.argmax(magnitude)
#                 detected_pitch = freqs[peak_index]
                
#                 stress_score = 0
#                 status = "Stable"
                
#                 if detected_pitch > PITCH_THRESHOLD:
#                     stress_score = 80
#                     status = "⚠️ ANXIETY"
#                 elif volume > 0.1:
#                     stress_score = 60
#                     status = "⚠️ LOUD"
#                 else:
#                     stress_score = 10
#                     status = "Relaxed"
                
#                 print(f"Pitch: {detected_pitch:.1f}Hz | Vol: {volume:.4f}")
                
#                 # [수정된 부분] volume 값을 Unity로 함께 보냅니다!
#                 response = {
#                     "stress_score": stress_score,
#                     "pitch": float(detected_pitch),
#                     "status": status,
#                     "volume": float(volume) 
#                 }
#                 await websocket.send_json(response)
            
#     except Exception as e:
#         print(f"Connection closed: {e}")

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)







# # server.py (업그레이드 버전)
# import numpy as np
# from fastapi import FastAPI, WebSocket
# import uvicorn

# app = FastAPI()

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     print("Waiting for connection...")
#     await websocket.accept()
#     print("Unity Connected! Ready to receive Audio 🎤")
    
#     try:
#         while True:
#             # 중요: 이제는 Text가 아니라 'bytes'(이진 데이터)를 받습니다.
#             data = await websocket.receive_bytes()
            
#             # 1. 받은 데이터를 Python이 이해하는 숫자(Float)로 변환
#             # Unity에서 float32로 보낼 것이므로 여기서도 float32로 풉니다.
#             audio_array = np.frombuffer(data, dtype=np.float32)
            
#             # 2. 데이터가 잘 오는지 확인 (소리 크기 출력)
#             # 볼륨(RMS)을 계산해서 출력해봅니다.
#             volume = np.sqrt(np.mean(audio_array**2))
            
#             if volume > 0.01: # 소리가 어느 정도 클 때만 로그 찍기
#                 print(f"🔊 Sound Detected! Volume: {volume:.4f} | Array Size: {len(audio_array)}")
            
#             # (옵션) 너무 조용하면 데이터만 받고 패스
            
#     except Exception as e:
#         print(f"Connection closed: {e}")

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)








# # # 파일명: server.py
# # # 설명: Unity와 통신하며 생체 신호를 분석할 기본 AI 서버

# # from fastapi import FastAPI, WebSocket
# # import uvicorn

# # app = FastAPI()

# # # Unity가 접속할 주소: ws://localhost:8000/ws
# # @app.websocket("/ws")
# # async def websocket_endpoint(websocket: WebSocket):
# #     print("Waiting for Unity connection... (연결 대기중)")
# #     await websocket.accept()
# #     print("Unity Connected! (연결 성공!) ✅")
    
# #     try:
# #         while True:
# #             # 1. Unity에서 보낸 메시지 받기
# #             data = await websocket.receive_text()
# #             print(f"[Received]: {data}")
            
# #             # 2. (나중에 여기에 감정 분석 AI 코드를 넣을 예정)
            
# #             # 3. Unity에게 응답 보내기 (JSON 형식)
# #             response = {"status": "ok", "stress_level": 45, "message": "Analyzed"}
# #             await websocket.send_json(response)
            
# #     except Exception as e:
# #         print(f"Connection closed: {e}")

# # if __name__ == "__main__":
# #     # 서버 실행 (IP: 0.0.0.0, Port: 8000)
# #     uvicorn.run(app, host="0.0.0.0", port=8000)