import os
import chromadb
from chromadb.utils import embedding_functions

import config

print("📦 RAG Altyapısı Yükleniyor...")

embedding_model_name = "paraphrase-multilingual-MiniLM-L12-v2"
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embedding_model_name)

db_path = os.path.join(config.DB_FOLDER, "sera_rag_db")
client = chromadb.PersistentClient(path=db_path)

collection = client.get_or_create_collection(
    name="ev_bilgileri",
    embedding_function=sentence_transformer_ef
)

def veritabanina_veri_ekle():
    """Örnek ev verilerini ve IoT durumlarını veritabanına ekler."""
    
    dokumanlar = [
        "Sera, Utku tarafından geliştirilen, çevrimdışı çalışan akıllı ev ve IoT asistanıdır.",
        "Çalışma odasındaki ana aydınlatmalar saat 23:00'te enerji tasarrufu moduna geçer ve parlaklık %30'a düşer.",
        "Salon sıcaklığı 22 derecenin altına düştüğünde akıllı termostat otomatik olarak devreye girerek odayı ısıtır.",
        "Sistem güvenlik modu aktifken, gece 02:00 ile 06:00 arasında koridordaki hareket sensörleri tespit yaparsa uyarı verir.",
        "Mutfaktaki akıllı prizlere bağlı kahve makinesi hafta içi her sabah saat 08:00'de otomatik olarak çalışmaya ayarlıdır."
    ]
    
    idler = [f"bilgi_{i}" for i in range(len(dokumanlar))]
    
    print("🧠 Veriler vektöre çevriliyor ve veritabanına kaydediliyor...")
    collection.upsert(
        documents=dokumanlar,
        ids=idler
    )
    print("✅ Veriler başarıyla kaydedildi!")

def arama_testi_yap(soru):
    """Kullanıcının sorusuna en yakın 2 bilgiyi veritabanından bulur."""
    print(f"\n🔎 Test Sorusu: '{soru}'")
    sonuclar = collection.query(
        query_texts=[soru],
        n_results=2
    )
    
    print("Bulunan Bağlamlar (Context):")
    for i, dokuman in enumerate(sonuclar['documents'][0]):
        print(f" {i+1}. {dokuman}")

if __name__ == "__main__":
    veritabanina_veri_ekle()
    
    arama_testi_yap("Çalışma odasının ışıkları gece nasıl çalışıyor?")
    arama_testi_yap("Sera kim tarafından geliştirildi?")
