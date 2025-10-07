#!/usr/bin/env python3
# migrations/update_regeneration_system.py
# Міграція для переходу на єдину систему регенерації

import sqlite3
import json
from datetime import datetime
from pathlib import Path


def find_database():
    """Знаходить файл бази даних"""
    # Шукаємо в різних місцях
    possible_paths = [
        'game.db',
        'src/game.db',
        '../game.db',
        'data/game.db'
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            return path
    
    # Шукаємо рекурсивно
    for db_file in Path('.').rglob('*.db'):
        try:
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='players'")
            if cursor.fetchone():
                conn.close()
                return str(db_file)
            conn.close()
        except:
            continue
    
    return None


def migrate_regeneration_system():
    """Мігрує базу даних на нову систему регенерації"""
    
    print("=" * 60)
    print("🔄 МІГРАЦІЯ СИСТЕМИ РЕГЕНЕРАЦІЇ")
    print("=" * 60)
    
    # Знаходимо базу даних
    db_path = find_database()
    
    if not db_path:
        print("❌ База даних не знайдена!")
        print("   Переконайтеся, що файл game.db існує")
        return False
    
    print(f"✅ Знайдено базу даних: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Перевіряємо структуру таблиці
        cursor.execute("PRAGMA table_info(players)")
        columns = {col[1]: col for col in cursor.fetchall()}
        
        print("\n📊 Поточні колонки в таблиці players:")
        for col_name in columns:
            print(f"   - {col_name}")
        
        # 2. Додаємо нове поле last_regeneration якщо його немає
        if 'last_regeneration' not in columns:
            print("\n➕ Додаємо колонку 'last_regeneration'...")
            cursor.execute("ALTER TABLE players ADD COLUMN last_regeneration TEXT")
            conn.commit()
            print("   ✅ Колонка додана")
        else:
            print("\n✅ Колонка 'last_regeneration' вже існує")
        
        # 3. Мігруємо дані з last_login в last_regeneration
        if 'last_login' in columns:
            print("\n🔄 Мігруємо дані з last_login → last_regeneration...")
            
            # Копіюємо дані
            cursor.execute("""
                UPDATE players 
                SET last_regeneration = COALESCE(last_regeneration, last_login)
                WHERE last_regeneration IS NULL AND last_login IS NOT NULL
            """)
            
            affected_rows = cursor.rowcount
            conn.commit()
            print(f"   ✅ Оновлено {affected_rows} записів")
        
        # 4. Встановлюємо поточний час для NULL значень
        current_time = datetime.now().isoformat()
        cursor.execute("""
            UPDATE players 
            SET last_regeneration = ?
            WHERE last_regeneration IS NULL
        """, (current_time,))
        
        affected_rows = cursor.rowcount
        if affected_rows > 0:
            conn.commit()
            print(f"\n⏰ Встановлено поточний час для {affected_rows} записів")
        
        # 5. Перевіряємо та виправляємо формат часу
        print("\n🔍 Перевіряємо формат часових міток...")
        
        cursor.execute("SELECT user_id, last_regeneration FROM players")
        players = cursor.fetchall()
        
        fixed_count = 0
        for user_id, last_regen in players:
            if last_regen:
                try:
                    # Пробуємо парсити час
                    datetime.fromisoformat(last_regen.split('.')[0])
                except:
                    # Якщо не вдається - встановлюємо поточний
                    cursor.execute(
                        "UPDATE players SET last_regeneration = ? WHERE user_id = ?",
                        (current_time, user_id)
                    )
                    fixed_count += 1
        
        if fixed_count > 0:
            conn.commit()
            print(f"   ✅ Виправлено {fixed_count} некоректних записів")
        else:
            print(f"   ✅ Всі записи мають коректний формат")
        
        # 6. Статистика
        print("\n📈 Статистика міграції:")
        cursor.execute("SELECT COUNT(*) FROM players")
        total_players = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM players WHERE last_regeneration IS NOT NULL")
        with_regeneration = cursor.fetchone()[0]
        
        print(f"   Всього гравців: {total_players}")
        print(f"   З last_regeneration: {with_regeneration}")
        print(f"   Успішність: {(with_regeneration/total_players*100):.1f}%")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ МІГРАЦІЯ УСПІШНО ЗАВЕРШЕНА!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Помилка міграції: {e}")
        return False


def verify_player_model():
    """Перевіряє, чи правильно працює модель Player"""
    
    print("\n🔬 Перевірка моделі Player...")
    
    try:
        from src.models.player import Player
        
        # Створюємо тестового гравця
        test_player = Player(
            user_id=999999,
            username="test_user",
            character_name="Test Hero",
            character_class="warrior"
        )
        
        # Перевіряємо наявність нового поля
        if hasattr(test_player, 'last_regeneration_time'):
            print("   ✅ Поле last_regeneration_time присутнє")
        else:
            print("   ❌ Поле last_regeneration_time відсутнє!")
            return False
        
        # Перевіряємо метод регенерації
        if hasattr(test_player, 'apply_regeneration'):
            result = test_player.apply_regeneration(force_update=False)
            if isinstance(result, dict) and all(k in result for k in ['hp', 'mana', 'seconds', 'ticks']):
                print("   ✅ Метод apply_regeneration працює коректно")
                print(f"      Результат: {result}")
            else:
                print("   ⚠️ Метод apply_regeneration повертає некоректні дані")
        else:
            print("   ❌ Метод apply_regeneration відсутній!")
            return False
        
        # Перевіряємо серіалізацію
        player_dict = test_player.to_dict()
        if 'last_regeneration' in player_dict or 'last_login' in player_dict:
            print("   ✅ Серіалізація включає поля регенерації")
        else:
            print("   ⚠️ Серіалізація не включає поля регенерації")
        
        # Перевіряємо десеріалізацію
        restored_player = Player.from_dict(player_dict)
        if hasattr(restored_player, 'last_regeneration_time'):
            print("   ✅ Десеріалізація відновлює поля регенерації")
        else:
            print("   ⚠️ Десеріалізація не відновлює поля регенерації")
        
        print("\n✅ Модель Player готова до роботи!")
        return True
        
    except ImportError as e:
        print(f"   ❌ Не вдалося імпортувати Player: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Помилка перевірки: {e}")
        return False


def main():
    """Головна функція"""
    
    print("\n🚀 ЗАПУСК МІГРАЦІЇ СИСТЕМИ РЕГЕНЕРАЦІЇ\n")
    
    # Крок 1: Міграція бази даних
    if not migrate_regeneration_system():
        print("\n❌ Міграція не вдалася. Перевірте помилки вище.")
        return
    
    # Крок 2: Перевірка моделі
    if not verify_player_model():
        print("\n⚠️ Модель Player потребує оновлення.")
        print("   Замініть файл src/models/player.py на оновлену версію.")
    
    print("\n" + "=" * 60)
    print("📝 ІНСТРУКЦІЇ ПІСЛЯ МІГРАЦІЇ:")
    print("=" * 60)
    print()
    print("1. Замініть src/models/player.py на оновлену версію")
    print("2. Оновіть обробники (start.py, city.py, battle.py)")
    print("3. Перезапустіть бота")
    print("4. Протестуйте регенерацію:")
    print("   - Зачекайте 1+ хвилину")
    print("   - Використайте /start або відкрийте персонажа")
    print("   - Перевірте, чи відновилось HP/мана")
    print()
    print("✨ Формула регенерації:")
    print("   HP за хвилину = stamina + 1")
    print("   Мана за хвилину = intelligence + 1")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()