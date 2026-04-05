import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class IoTManager:
    def __init__(self):
        self.db_path = config.MEMORY_DB_PATH

    def get_all_devices(self):
        """Tüm cihazların anlık durumunu liste olarak döndürür."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT device_id, name, room, status FROM iot_devices")
            rows = cursor.fetchall()
            conn.close()
            
            devices = [{"device_id": r[0], "name": r[1], "room": r[2], "status": r[3]} for r in rows]
            return devices
        except Exception as e:
            print(f"⚠️ IoT Okuma Hatası: {e}")
            return []

    def update_device_status(self, device_id, new_status):
        """Belirtilen cihazın durumunu (Açık/Kapalı) günceller."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE iot_devices SET status = ?, last_updated = CURRENT_TIMESTAMP WHERE device_id = ?", 
                (new_status, device_id)
            )
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            print(f"⚠️ IoT Güncelleme Hatası: {e}")
            return False

    def get_device_states_str(self):
        """LLM'in anlayabileceği formatta cihaz durumlarını metin olarak verir."""
        devices = self.get_all_devices()
        if not devices:
            return "Sisteme kayıtlı cihaz bulunamadı."
        
        lines = []
        for d in devices:
            lines.append(f"- {d['room']} {d['name']} ({d['device_id']}): {d['status']}")
        return "\n".join(lines)

if __name__ == "__main__":
    iot = IoTManager()
    print("--- Mevcut Cihaz Durumları ---")
    print(iot.get_device_states_str())
    
    iot.update_device_status("light_calisma", "Açık")
    print("\n--- Güncelleme Sonrası ---")
    print(iot.get_device_states_str())
