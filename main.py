import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import os
import sys
import json
import config
from core import audio, llm, system, memory
from core.iot import IoTManager

print("🚀 Sistem Başlatılıyor...")
try:
    sera = llm.LLMEngine()
    hafiza = memory.MemorySystem()
    iot = IoTManager()
except Exception as e:
    print(f"💥 Kritik Hata: {e}")
    sys.exit(1)

app = FastAPI()
SES_ACIK = True

@app.get("/")
async def get():
    template_path = os.path.join(config.BASE_DIR, "templates", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    global SES_ACIK
    
    cihazlar = iot.get_all_devices()
    await websocket.send_json({"type": "device_update", "data": cihazlar})
    
    while True:
        try:
            raw_data = await websocket.receive_text()
            try:
                data = json.loads(raw_data)
            except:
                data = {"type": "command", "action": raw_data}

            if data.get("type") == "config":
                SES_ACIK = data.get("voice_active", True)
                durum = "Açık" if SES_ACIK else "Kapalı"
                print(f"🔊 Ses Durumu: {durum}")
                continue

            if data.get("type") == "command" and data.get("action") == "start_listening":
                await websocket.send_json({"type": "info", "text": "Dinliyorum..."})
                user_text = audio.listen_mic()
                
                if user_text:
                    print(f"👤 Kullanıcı: {user_text}")
                    await websocket.send_json({"type": "user", "text": user_text})
                    
                    response_text = ""
                    text_lower = user_text.lower()
                    
                    if "not defteri" in text_lower:
                        response_text = system.open_application("notepad")
                    elif "hesap makinesi" in text_lower:
                        response_text = system.open_application("hesap_makinesi")
                    elif "ara" in text_lower or "bul" in text_lower:
                        query = text_lower.replace("ara", "").replace("bul", "").replace("bana", "").replace("internette", "").strip()
                        if query:
                            await websocket.send_json({"type": "info", "text": f"🔎 '{query}' aranıyor..."})
                            results = system.search_web(query)
                            if results:
                                await websocket.send_json({"type": "search_results", "data": results})
                                response_text = f"İnternette '{query}' hakkında bunları buldum."
                            else:
                                response_text = "Maalesef internette ilgili bir sonuç bulamadım."
                        else:
                            response_text = "Ne aramam gerektiğini anlamadım."
                    else:
                        await websocket.send_json({"type": "info", "text": "🧠 Düşünüyor..."})
                        context_data = hafiza.get_context(limit=6)
                        
                        response_text = sera.generate_response(user_text, context=context_data)
                        
                        hafiza.add_message("user", user_text)
                        hafiza.add_message("bot", response_text)

                        guncel_cihazlar = iot.get_all_devices()
                        await websocket.send_json({"type": "device_update", "data": guncel_cihazlar})

                    if response_text:
                        await websocket.send_json({"type": "bot", "text": response_text})
                    
                    if response_text and SES_ACIK:
                        audio.speak(response_text)

        except Exception as e:
            print(f"Bağlantı Koptu/Hata: {e}")
            break
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
