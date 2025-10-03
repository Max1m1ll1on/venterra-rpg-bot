import random
from typing import Dict, Tuple, Optional


class SkillCheck:
    """Система перевірок навичок у стилі D&D"""
    
    @staticmethod
    def roll_check(stat_value: int, dc: int = 10) -> Tuple[int, int, bool]:
        """
        Кидок на перевірку навички
        
        Args:
            stat_value: Значення характеристики гравця
            dc: Difficulty Class (складність)
            
        Returns:
            (d20_result, total, success)
        """
        d20 = random.randint(1, 20)
        modifier = (stat_value - 10) // 2  # D&D модифікатор
        total = d20 + modifier
        success = total >= dc
        
        return d20, total, success
    
    @staticmethod
    def get_check_description(d20: int, total: int, dc: int, success: bool) -> str:
        """Генерує опис результату перевірки"""
        if d20 == 20:
            return f"💫 **Критичний успіх!** (20 + мод = {total} проти DC {dc})"
        elif d20 == 1:
            return f"💀 **Критична невдача!** (1 + мод = {total} проти DC {dc})"
        elif success:
            return f"✅ **Успіх!** ({d20} + мод = {total} проти DC {dc})"
        else:
            return f"❌ **Провал.** ({d20} + мод = {total}, потрібно {dc}+)"


# ============================================================
# Випадкові події для кожної локації
# ============================================================

LOCATION_EVENTS = {
    "forest": [
        {
            "name": "🌿 Заросла стежка",
            "description": "Ви знайшли заросла стежку. Щось блищить у кущах.",
            "stat": "agility",
            "dc": 10,
            "success_reward": {"gold": 30, "message": "Ви спритно пробрались і знайшли схованку!"},
            "fail_penalty": {"message": "Ви зашарпались у кущах. Нічого не знайшли."}
        },
        {
            "name": "🦌 Дикий звір",
            "description": "Перед вами з'явився дикий звір. Спробуєте його приручити?",
            "stat": "charisma",
            "dc": 12,
            "success_reward": {"gold": 20, "message": "Звір довірився вам і показав шлях до скарбу!"},
            "fail_penalty": {"damage": 5, "message": "Звір злякався та втік, поцарапавши вас."}
        },
        {
            "name": "🍄 Дивні гриби",
            "description": "Ви знайшли незвичайні гриби. Які з них їстівні?",
            "stat": "intelligence",
            "dc": 11,
            "success_reward": {"heal": 15, "message": "Це лікувальні гриби! Ви відновили здоров'я."},
            "fail_penalty": {"damage": 10, "message": "Гриби виявились отруйними!"}
        }
    ],
    
    "mountains": [
        {
            "name": "🏔️ Крутий схил",
            "description": "Попереду крутий гірський схил. Спробуєте підійти?",
            "stat": "strength",
            "dc": 12,
            "success_reward": {"gold": 50, "message": "Ви піднялись і знайшли стародавню скриню!"},
            "fail_penalty": {"damage": 8, "message": "Ви зірвались зі схилу і отримали поранення."}
        },
        {
            "name": "🧗 Скельна стіна",
            "description": "Скельна стіна блокує прохід. Спробуєте подолати?",
            "stat": "stamina",
            "dc": 13,
            "success_reward": {"exp": 50, "message": "Ваша витривалість допомогла! Ви отримали досвід."},
            "fail_penalty": {"damage": 12, "message": "Ви виснажились і впали."}
        },
        {
            "name": "❄️ Холодна печера",
            "description": "Морозна печера. Ви чуєте щось всередині.",
            "stat": "intelligence",
            "dc": 12,
            "success_reward": {"item": "rare", "message": "Ви знайшли магічний артефакт!"},
            "fail_penalty": {"message": "Ви заблукали у темряві і вийшли назад."}
        }
    ],
    
    "ruins": [
        {
            "name": "🗿 Стародавні руни",
            "description": "На стіні вирізані магічні руни. Спробуєте прочитати?",
            "stat": "intelligence",
            "dc": 14,
            "success_reward": {"gold": 80, "exp": 30, "message": "Руни вказали на схований скарб!"},
            "fail_penalty": {"damage": 15, "message": "Ви активували пастку!"}
        },
        {
            "name": "🚪 Важкі двері",
            "description": "Масивні кам'яні двері. Потрібна сила щоб відкрити.",
            "stat": "strength",
            "dc": 13,
            "success_reward": {"gold": 60, "message": "Ви відкрили двері до скарбниці!"},
            "fail_penalty": {"message": "Двері не піддаються. Можливо пізніше."}
        },
        {
            "name": "🪤 Пастка з стрілами",
            "description": "Ви помітили натягнутий дріт. Пастка!",
            "stat": "agility",
            "dc": 13,
            "success_reward": {"message": "Ви спритно ухилились!"},
            "fail_penalty": {"damage": 20, "message": "Стріли влучили в вас!"}
        }
    ],
    
    "caves": [
        {
            "name": "🕳️ Темний тунель",
            "description": "Абсолютна темрява. Чуєте шурхіт.",
            "stat": "intelligence",
            "dc": 12,
            "success_reward": {"item": "uncommon", "message": "Ви знайшли дорогоцінні камені!"},
            "fail_penalty": {"damage": 10, "message": "Ви вдарились об стіну в темряві."}
        },
        {
            "name": "💎 Кристалева печера",
            "description": "Печера сяє кристалами. Який забрати?",
            "stat": "intelligence",
            "dc": 13,
            "success_reward": {"gold": 70, "message": "Ви обрали найцінніший кристал!"},
            "fail_penalty": {"message": "Кристал виявився підробкою."}
        },
        {
            "name": "🦇 Зграя кажанів",
            "description": "Кажани летять на вас!",
            "stat": "agility",
            "dc": 12,
            "success_reward": {"message": "Ви швидко ухилились!"},
            "fail_penalty": {"damage": 8, "message": "Кажани поцарапали вас!"}
        }
    ],
    
    "swamp": [
        {
            "name": "🐊 Трясовина",
            "description": "Перед вами небезпечна трясовина.",
            "stat": "stamina",
            "dc": 14,
            "success_reward": {"gold": 90, "message": "Ви витримали і знайшли затонулий скарб!"},
            "fail_penalty": {"damage": 15, "message": "Ви застрягли і ледве вибрались."}
        },
        {
            "name": "☠️ Отруйні випари",
            "description": "Болото випускає токсичні гази.",
            "stat": "stamina",
            "dc": 13,
            "success_reward": {"message": "Ваша витривалість врятувала вас!"},
            "fail_penalty": {"damage": 12, "message": "Ви отруїлись парами!"}
        },
        {
            "name": "🌫️ Густий туман",
            "description": "Густий туман. Легко заблукати.",
            "stat": "intelligence",
            "dc": 13,
            "success_reward": {"exp": 60, "message": "Ви знайшли правильний шлях!"},
            "fail_penalty": {"message": "Ви блукали годинами, але повернулись назад."}
        }
    ]
}


def get_random_event(location_id: str) -> Optional[Dict]:
    """Отримує випадкову подію для локації"""
    events = LOCATION_EVENTS.get(location_id, [])
    if not events:
        return None
    return random.choice(events)