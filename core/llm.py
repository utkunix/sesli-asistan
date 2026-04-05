import os
import sys
import datetime
import re 
from llama_cpp import Llama
import chromadb
from chromadb.utils import embedding_functions

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from core.iot import IoTManager

class LLMEngine:
    def __init__(self):
        print("\n⚙️  Sera AI Motoru (GGUF) Yükleniyor...")
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.model_path = os.path.join(base_dir, "models", "sera_v2.gguf") 
        
        if not os.path.exists(self.model_path):
            print(f"❌ HATA: Model bulunamadı: {self.model_path}")
            sys.exit(1)

        try:
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=4096,
                n_threads=6,
                n_batch=512,
                verbose=False
            )
            print("✅ Sera Zihni Açıldı!")
        except Exception as e:
            print(f"❌ Model Yükleme Hatası: {e}")
            sys.exit(1)

        print("🧠 RAG Hafızasına Bağlanılıyor...")
        embedding_model_name = "paraphrase-multilingual-MiniLM-L12-v2"
        self.sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embedding_model_name)
        
        db_path = os.path.join(config.DB_FOLDER, "sera_rag_db")
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name="ev_bilgileri",
            embedding_function=self.sentence_transformer_ef
        )
        print("✅ RAG Hafızası Hazır!\n")
        
        self.iot = IoTManager()

    def search_rag(self, query):
        """Kullanıcı sorusuna en uygun bilgiyi RAG veritabanından çeker."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=1 
            )
            if results['documents'] and results['documents'][0]:
                return results['documents'][0][0] 
        except Exception as e:
            print(f"⚠️ RAG Arama Hatası: {e}")
        return ""

    def generate_response(self, user_input, context=""):
        now = datetime.datetime.now()
        tarih_saat = now.strftime("%d %B %Y, Saat %H:%M")

        rag_bilgisi = self.search_rag(user_input)
        cihaz_durumlari = self.iot.get_device_states_str()

        system_prompt = (
            f"Tarih: {tarih_saat}.\n"
            "Senin adın Sera. Sen Türkçe konuşan, zeki, yardımsever ve çevrimdışı çalışan bir akıllı ev asistanısın.\n"
            "Kullanıcının adı Utku Kalender.\n"
            "Kurallar:\n"
            "1. Sadece Türkçe cevap ver.\n"
            "2. Cevapların doğal, kibar ve kısa olsun.\n"
            "3. Gramer kurallarına uy.\n"
            "4. Kullanıcı ev hakkında bir şey sorarsa, 'Ev Hakkında Bilgi' kısmını kullan.\n"
            "5. ÇOK ÖNEMLİ: Eğer kullanıcı senden bir cihazı açmanı veya kapatmanı isterse, konuşmanın sonuna ŞU GİZLİ KOMUTU ekle: [KONTROL:cihaz_id:Açık] veya [KONTROL:cihaz_id:Kapalı]. "
            "Sadece kullanıcının bahsettiği cihazı değiştir. Anlık durumları aşağıda verilmiştir.\n"
            f"\n--- SİSTEMDEKİ CİHAZLAR VE ANLIK DURUMLARI ---\n{cihaz_durumlari}"
            "Örnek Kullanım:\n"
            "Kullanıcı: Mutfak prizini aç.\n"
            "Asistan: Mutfaktaki akıllı prizi hemen açıyorum. [KONTROL:plug_mutfak:Açık]\n"
            "Kullanıcı: Çalışma odasının ışıklarını kapat.\n"
            "Asistan: Çalışma odasının ışıklarını kapattım. [KONTROL:light_calisma:Kapalı]"
        )

        if rag_bilgisi:
            system_prompt += f"\n\nEv Hakkında Bilgi:\n{rag_bilgisi}"

        if context:
            system_prompt += f"\n\nGeçmiş Konuşmalar:\n{context}"

        prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"

        try:
            output = self.model(
                prompt,
                max_tokens=250,
                stop=["<|im_end|>", "User:", "Utku:", "Sistem:"], 
                temperature=0.1,
                top_p=0.9,
                repeat_penalty=1.1,
                echo=False
            )
            
            response = output["choices"][0]["text"].strip()
            
            match = re.search(r'\[KONTROL:(.*?):(Açık|Kapalı)\]', response)
            if match:
                device_id = match.group(1).strip()
                yeni_durum = match.group(2).strip()
                
                basarili_mi = self.iot.update_device_status(device_id, yeni_durum)
                if basarili_mi:
                    print(f"\n🔌 IoT BAŞARILI: {device_id} cihazı {yeni_durum} yapıldı.")
                else:
                    print(f"\n⚠️ IoT BAŞARISIZ: {device_id} güncellenemedi.")
                
                response = re.sub(r'\[KONTROL:.*?\]', '', response).strip()

            response = response.replace("Sera'sın", "Sera'yım")
            response = response.replace("OpenAI", "Utku Kalender")
            
            return response
            
        except Exception as e:
            print(f"❌ Cevap Üretme Hatası: {e}")
            return "Şu an odaklanamıyorum Utku, bir hata oluştu."

if __name__ == "__main__":
    motor = LLMEngine()
    print("\n--- TEST BAŞLIYOR ---")
    
    soru = "Sera, çalışma odasının ışıklarını kapatır mısın?"
    print(f"Soru: {soru}")
    cevap = motor.generate_response(soru)
    print(f"Sera'nın Cevabı: {cevap}")
    
    print("\n--- SON DURUM ---")
    print(motor.iot.get_device_states_str())
