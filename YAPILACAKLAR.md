# Sera AI - Proje İlerleme Planı: RAG Mimarisi ve IoT Entegrasyonu

Bu doküman, Sera AI projesinin statik fine-tuning yaklaşımından Offline RAG mimarisine geçişini ve nihai olarak sanal bir akıllı ev (IoT) sistemine dönüştürülmesini hedefleyen 5 haftalık sprint planını içermektedir. Her bir alt başlık ayrı bir GitHub Issue olarak açılıp takip edilecektir.

## Hafta 1: RAG Altyapısının Kurulması (Vektör Veritabanı)
- [ ] Projeye lokal çalışacak bir vektör veritabanının (ChromaDB veya FAISS) entegre edilmesi.
- [ ] Ev kuralları, cihaz durumları ve kullanım senaryoları gibi metinleri parçalara (chunk) ayırıp vektöre (embedding) dönüştürecek Python betiğinin (`rag_indexer.py`) yazılması.
- [ ] Vektör veritabanına veri ekleme ve benzerlik araması (similarity search) fonksiyonlarının test edilmesi.

## Hafta 2: Sera (LLM) ile RAG Entegrasyonu
- [ ] `llm.py` içerisindeki `generate_response` fonksiyonunun RAG mimarisine uygun olarak güncellenmesi.
- [ ] Kullanıcı sorusunun önce vektör veritabanında aranıp, bulunan bağlamın (context) sistem promptu ile birleştirilerek modele sunulması.
- [ ] Modelin halüsinasyon testlerinin yapılması (Cevapların sadece veritabanındaki bilgilerle sınırlandırıldığının doğrulanması).

## Hafta 3: IoT Veritabanı ve Temel Kontrol Mantığı
- [ ] `memory.py` içerisindeki veritabanına `iot_devices` (Cihaz ID, Adı, Odası, Durumu vb.) tablosunun eklenmesi.
- [ ] Yeni bir `iot.py` modülü oluşturularak cihaz durumlarını okuma ve değiştirme (CRUD) işlemlerini yapacak fonksiyonların yazılması.
- [ ] Sera'nın kullanıcı niyetini (intent) anlayıp `iot.py` üzerinden cihaz durumunu güncelleyebilmesi için kural tabanlı veya "Function Calling" benzeri bir tetikleme yapısının kurulması.

## Hafta 4: Sanal Ev Modelinin (Arayüz) Geliştirilmesi
- [ ] `index.html` arayüzüne basit bir "Sanal Ev Dashboard'u" eklenmesi (Mutfak, Oturma Odası gibi odalar ve cihazların Açık/Kapalı ikonları).
- [ ] FastAPI üzerinden frontend'in `iot_devices` tablosunu dinlemesini sağlayacak yapının (WebSocket veya REST) kurgulanması.
- [ ] Cihaz durumları değiştikçe arayüzdeki ikonların gerçek zamanlı (real-time) olarak güncellenmesi.

## Hafta 5: Uçtan Uca Test ve Optimizasyon
- [ ] Sesli komutların tam entegrasyonu: Mikrofon -> Intent Yakalama -> RAG Kontrolü -> IoT Tetikleme -> Arayüz Güncellemesi -> Sesli Yanıt döngüsünün test edilmesi.
- [ ] Ses işleme ve LLM yanıt süreleri arasındaki gecikmelerin (latency) optimize edilmesi.
- [ ] Proje dokümantasyonunun tamamlanması ve genel temizliğin yapılarak projenin sunuma hazır hale getirilmesi.
