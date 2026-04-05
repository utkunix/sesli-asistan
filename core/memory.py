import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class MemorySystem:
    def __init__(self):
        self.db_path = config.MEMORY_DB_PATH
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        self.create_tables()

    def create_tables(self):
        """Sohbet geçmişi ve IoT cihazları tablolarını oluşturur."""
        # Mesajlar Tablosu
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # IoT Cihazları Tablosu
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS iot_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT UNIQUE,
                name TEXT,
                room TEXT,
                status TEXT, -- 'Açık' veya 'Kapalı'
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
        
        self.cursor.execute("SELECT COUNT(*) FROM iot_devices")
        if self.cursor.fetchone()[0] == 0:
            varsayilan_cihazlar = [
                ("light_calisma", "Ana Aydınlatma", "Çalışma Odası", "Kapalı"),
                ("plug_mutfak", "Akıllı Priz (Kahve Makinesi)", "Mutfak", "Kapalı"),
                ("thermostat_salon", "Akıllı Termostat", "Salon", "Açık")
            ]
            self.cursor.executemany(
                "INSERT INTO iot_devices (device_id, name, room, status) VALUES (?, ?, ?, ?)", 
                varsayilan_cihazlar
            )
            self.conn.commit()
            print("🔌 Varsayılan IoT cihazları veritabanına eklendi.")
            
        print("💾 Hafıza ve IoT veritabanı sistemi hazır.")

    def add_message(self, role, content):
        try:
            self.cursor.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))
            self.conn.commit()
        except Exception as e:
            print(f"⚠️ Hafıza Yazma Hatası: {e}")

    def get_context(self, limit=5):
        try:
            self.cursor.execute("SELECT role, content FROM messages ORDER BY id DESC LIMIT ?", (limit,))
            rows = self.cursor.fetchall()
            
            history = []
            for role, content in reversed(rows):
                isim = "Utku" if role == "user" else "Sera"
                history.append(f"{isim}: {content}")
            
            return "\n".join(history)
        except Exception as e:
            print(f"⚠️ Hafıza Okuma Hatası: {e}")
            return ""

if __name__ == "__main__":
    mem = MemorySystem()
    print("Sistem başarıyla test edildi.")
