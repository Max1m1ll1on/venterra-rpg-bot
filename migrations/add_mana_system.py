# migrations/add_mana_system.py
# Запустіть цей скрипт один раз для оновлення БД

import sqlite3
import os
import glob

def find_database():
    """Знаходить файл бази даних"""
    # Шукаємо всі .db файли
    db_files = glob.glob('*.db') + glob.glob('**/*.db', recursive=True)
    
    if not db_files:
        print("❌ Файл бази даних не знайдено!")
        print("Шукав файли: *.db")
        return None
    
    print(f"Знайдено бази даних: {db_files}")
    
    # Перевіряємо кожен файл на наявність таблиці players
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
    
    print("❌ Не знайдено БД з таблицею 'players'")
    return None


def migrate_database():
    """Додає поля мани до існуючої бази даних"""
    db_path = find_database()
    
    if not db_path:
        print("\n💡 Можливо база даних ще не створена.")
        print("Запустіть бота командою: python main.py")
        print("Після чого виконайте /start у боті для створення персонажа")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Перевіряємо чи є колонка mana
    cursor.execute("PRAGMA table_info(players)")
    columns = [column[1] for column in cursor.fetchall()]
    
    print(f"\nПоточні колонки: {columns}\n")
    
    changes_made = False
    
    if 'mana' not in columns:
        print("Додаємо колонку 'mana'...")
        cursor.execute("ALTER TABLE players ADD COLUMN mana INTEGER DEFAULT 0")
        changes_made = True
    else:
        print("Колонка 'mana' вже існує")
    
    if 'max_mana' not in columns:
        print("Додаємо колонку 'max_mana'...")
        cursor.execute("ALTER TABLE players ADD COLUMN max_mana INTEGER DEFAULT 0")
        changes_made = True
    else:
        print("Колонка 'max_mana' вже існує")
    
    if 'ability_cooldowns' not in columns:
        print("Додаємо колонку 'ability_cooldowns'...")
        cursor.execute("ALTER TABLE players ADD COLUMN ability_cooldowns TEXT DEFAULT '{}'")
        changes_made = True
    else:
        print("Колонка 'ability_cooldowns' вже існує")
    
    if changes_made:
        # Оновлюємо ману для існуючих гравців
        print("\nОновлюємо ману для існуючих гравців...")
        cursor.execute("SELECT user_id, intelligence FROM players WHERE max_mana = 0 OR max_mana IS NULL")
        players = cursor.fetchall()
        
        for user_id, intelligence in players:
            max_mana = intelligence * 5 if intelligence else 15
            cursor.execute(
                "UPDATE players SET mana = ?, max_mana = ? WHERE user_id = ?",
                (max_mana, max_mana, user_id)
            )
            print(f"  Гравець {user_id}: мана {max_mana}/{max_mana}")
        
        conn.commit()
        print("\n✅ Міграція завершена успішно!")
    else:
        print("\n✅ Всі поля вже існують, міграція не потрібна!")
    
    conn.close()


if __name__ == "__main__":
    print("🔍 Пошук бази даних...\n")
    migrate_database()