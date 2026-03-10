from telethon import TelegramClient, events
import os
import re
import time
import hashlib

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
alert_chat = os.getenv("ALERT_CHAT")

client = TelegramClient("session", api_id, api_hash)

# 1) Слова намерения: человек ищет исполнителя
intent_keywords = [
    # RU
    "нужен", "нужна", "нужно", "нужны",
    "ищу", "требуется", "требуются",
    "кто может", "кто сможет", "посоветуйте",
    "подскажите мастера", "нужен мастер", "ищу мастера",
    # UA
    "потрібен", "потрібна", "потрібно", "потрібні",
    "шукаю", "потрібен майстер", "шукаю майстра",
    "хто може", "хто зможе", "порадьте", "підкажіть майстра",
    "цікавить", "потрібна допомога",
]

# 2) Профессиональные/рабочие корни
service_keywords = [
    # общие
    "мастер", "майстер", "бригад", "подсоб", "робіт", "рабоч",
    "ремонт", "будів", "строит", "отделк", "відділ",

    # отделка / стройка
    "шпаклев", "шпаклю", "штукатур", "фарб", "покрас",
    "обои", "ламинат", "ламінат", "плитк", "плиточ", "стяж",
    "гіпсокартон", "гипсокартон", "маляр",

    # сантехника
    "сантех", "кран", "смесител", "змішувач", "унитаз",
    "засор", "канализац", "каналіза", "труб", "раковин", "мийк",
    "ванн", "бойлер", "сантехника", "сантехник",

    # электрика
    "электрик", "електрик", "электр", "електр",
    "розет", "выключател", "вимикач", "люстр", "светиль", "світиль",
    "щиток", "кабел", "проводк", "автомат",

    # мебель / сборка
    "мебел", "мебл", "шкаф", "кухн", "сборк", "збірк", "гарнитур",

    # перевозка / грузчики
    "грузчик", "вантаж", "перевез", "перевоз", "переезд", "переїзд",
    "разгруз", "розвантаж", "погруз", "завантаж", "вывоз", "смітт", "мусор",

    # техника
    "стиральн", "пральн", "холодиль", "посудомоеч", "посудомийн",
    "духовк", "кондиционер", "кондиціонер",

    # монтаж
    "полк", "телевиз", "карниз", "кроват", "ліжк", "зеркал", "дзеркал",
    "двер", "замок", "навес", "установ", "встанов",
]

# 3) Стоп-слова: реклама, новости, самопиар, болтовня
negative_keywords = [
    # реклама / продажа
    "приглашаю", "запись", "запис", "акция", "знижка", "скидка",
    "сертифицирован", "сертифік", "прайс", "прайс-лист", "цена", "ціна",
    "стоимость", "вартість", "услуги", "послуги", "предлагаю", "пропоную",
    "выполняю", "роблю", "делаю", "портфолио", "портфоліо",
    "инстаграм", "instagram", "whatsapp", "viber", "telegram:",
    "телеграм:", "салон", "записаться", "бронь", "бронювання",

    # разговоры / новости / не заказы
    "работают", "работает", "працює", "працюють",
    "кто-то", "хтось", "сегодня", "сьогодні", "завтра",
    "новость", "новини", "предупреждение", "попередження",
    "внимание", "увага", "купил", "купила", "выбросил", "викинув",
    "октоберфест", "психология", "психологія", "гондол", "мина",
]

# Дополнительные шаблоны мусора
negative_patterns = [
    r"https?://",
    r"@\w+",  # много рекламных постов с юзернеймами
    r"\binst\b",
    r"\bпрайс\b",
    r"\bпортфол",
]

# Защита от дублей
recent_messages = {}
DUPLICATE_TTL = 60 * 60 * 6  # 6 часов


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("ё", "е")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def contains_any(text: str, words: list[str]) -> str | None:
    for word in words:
        if word in text:
            return word
    return None


def matches_negative_pattern(text: str) -> bool:
    for pattern in negative_patterns:
        if re.search(pattern, text):
            return True
    return False


def is_duplicate(text: str) -> bool:
    now = time.time()

    # чистим старые записи
    expired = [k for k, v in recent_messages.items() if now - v > DUPLICATE_TTL]
    for k in expired:
        del recent_messages[k]

    digest = hashlib.md5(text.encode("utf-8")).hexdigest()
    if digest in recent_messages:
        return True

    recent_messages[digest] = now
    return False


def build_message_link(chat, message_id: int) -> str | None:
    username = getattr(chat, "username", None)
    if username:
        return f"https://t.me/{username}/{message_id}"

    chat_id = getattr(chat, "id", None)
    if chat_id:
        chat_id_str = str(chat_id)
        if chat_id_str.startswith("-100"):
            chat_id_str = chat_id_str[4:]
        return f"https://t.me/c/{chat_id_str}/{message_id}"

    return None


@client.on(events.NewMessage)
async def handler(event):
    # игнор своих сообщений
    if event.out:
        return

    # игнор пересланных
    if event.fwd_from:
        return

    # игнор сообщений без текста
    raw_text = event.raw_text or ""
    if not raw_text.strip():
        return

    text = normalize_text(raw_text)

    # слишком короткие сообщения игнорируем
    if len(text) < 8:
        return

    # сперва отсекаем явный мусор
    negative_word = contains_any(text, negative_keywords)
    if negative_word:
        return

    if matches_negative_pattern(text):
        return

    # должен быть хотя бы один признак намерения
    intent_word = contains_any(text, intent_keywords)
    if not intent_word:
        return

    # и хотя бы один рабочий/ремонтный корень
    service_word = contains_any(text, service_keywords)
    if not service_word:
        return

    # антидубль
    if is_duplicate(text):
        return

    sender = await event.get_sender()
    chat = await event.get_chat()

    chat_name = getattr(chat, "title", None) or "ЛС"

    username = getattr(sender, "username", None)
    if username:
        author_tag = f"@{username}"
    else:
        first_name = getattr(sender, "first_name", "") or ""
        last_name = getattr(sender, "last_name", "") or ""
        full_name = f"{first_name} {last_name}".strip()
        author_tag = full_name if full_name else "Без имени"

    msg_time = event.date.strftime("%Y-%m-%d %H:%M:%S")
    message_link = build_message_link(chat, event.message.id)

    msg = (
        f"НАЙДЕН ЗАКАЗ\n\n"
        f"Намерение: {intent_word}\n"
        f"Тема: {service_word}\n"
        f"Группа: {chat_name}\n"
        f"Автор: {author_tag}\n"
        f"Время: {msg_time}\n"
    )

    if message_link:
        msg += f"Ссылка: {message_link}\n"

    msg += f"\nСообщение:\n{raw_text}"

    await client.send_message(alert_chat, msg)


client.start()
print("Бот запущен и слушает сообщения...")
client.run_until_disconnected()
