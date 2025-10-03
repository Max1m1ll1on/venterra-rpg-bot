# migrations/add_offline_regen.py - ВИПРАВЛЕНА ВЕРСІЯ

import sqlite3
import glob
from datetime import datetime

def find_database():
    """Знаходить файл бази даних"""
    db_files = glob.glob('*.db') + glob.glob('**/*.db', recursive=True)
    
    if not db_files:
        print("❌ Файл бази даних не знайдено!")
        return None
    
    for db_file in db_files:
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='players'")
            if cursor.fetchone():
                conn.close()
                print(f"✅ Використовуємо БД: {db_file}")
                return db_file
            conn.close()
        except:
            continue
    
    return None


def migrate_offline_regen():
    """Додає поле last_login для офлайн регенерації"""
    db_path = find_database()
    
    if not db_path:
        print("❌ База даних не знайдена!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Перевіряємо чи є колонка last_login
    cursor.execute("PRAGMA table_info(players)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'last_login' not in columns:
        print("📅 Додаємо колонку 'last_login'...")
        
        # ✅ ВИПРАВЛЕНО: Без DEFAULT (SQLite не підтримує)
        cursor.execute("ALTER TABLE players ADD COLUMN last_login TEXT")
        
        # Встановлюємо поточний час для всіх існуючих гравців
        current_time = datetime.now().isoformat()
        cursor.execute("UPDATE players SET last_login = ? WHERE last_login IS NULL", (current_time,))
        
        conn.commit()
        print(f"✅ Міграція завершена! Встановлено last_login для всіх гравців: {current_time}")
    else:
        print("✅ Колонка 'last_login' вже існує")
    
    conn.close()


if __name__ == "__main__":
    migrate_offline_regen()