from telethon import TelegramClient, events
import os
import re
import time
import hashlib

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
alert_chat = os.getenv("ALERT_CHAT")

client = TelegramClient("session", api_id, api_hash)

# ---------------------------------
# 1. Признаки запроса / намерения
# ---------------------------------
intent_keywords = [
    # RU — прямой запрос
    "ищу", "нужен", "нужна", "нужно", "нужны",
    "требуется", "требуются",
    "посоветуйте", "подскажите",
    "кто может", "кто сможет", "кто делает", "кто занимается",
    "кто ремонтирует", "кто собирает", "кто устанавливает",
    "кто знает", "знает кто", "кто-нибудь знает",
    "может кто", "может кто-то",
    "есть мастер", "есть кто", "есть знакомый",
    "нужен мастер", "ищу мастера", "нужен специалист",
    "кого посоветуете", "кого можете посоветовать",

    # RU — бытовые формулировки
    "нужно починить", "надо починить", "хочу починить",
    "нужно сделать", "надо сделать", "нужно установить",
    "надо установить", "нужно собрать", "надо собрать",
    "нужно повесить", "надо повесить", "нужно заменить",
    "надо заменить", "помогите с", "помощь с",

    # UA — прямий запит
    "шукаю", "потрібен", "потрібна", "потрібно", "потрібні",
    "порадьте", "підкажіть",
    "хто може", "хто зможе", "хто робить", "хто займається",
    "хто ремонтує", "хто збирає", "хто встановлює",
    "хто знає", "знає хто", "хтось знає",
    "може хтось",
    "є майстер", "є хто", "є знайомий",
    "потрібен майстер", "шукаю майстра", "потрібен спеціаліст",
    "кого порадите",

    # UA — побутові формулювання
    "треба полагодити", "потрібно полагодити", "хочу полагодити",
    "треба зробити", "потрібно зробити",
    "треба встановити", "потрібно встановити",
    "треба зібрати", "потрібно зібрати",
    "треба повісити", "потрібно повісити",
    "треба замінити", "потрібно замінити",
    "допоможіть з", "допомога з",
]

# ---------------------------------
# 2. Признаки поломки / проблемы
# ---------------------------------
problem_keywords = [
    # RU
    "сломал", "сломалась", "сломалось", "сломались",
    "не работает", "не включается", "не выключается",
    "не открывается", "не закрывается",
    "плохо работает", "перестал работать", "перестала работать",
    "протекает", "течет", "засор", "выбивает",
    "искрит", "коротит", "отвалилось", "треснуло",
    "разбилось", "перегорело",

    # UA
    "зламався", "зламалась", "зламалося", "зламались",
    "не працює", "не вмикається", "не вимикається",
    "не відкривається", "не закривається",
    "погано працює", "перестав працювати", "перестала працювати",
    "протікає", "тече", "засмічення", "вибиває",
    "іскрить", "замкнуло", "відвалилось", "тріснуло",
    "розбилось", "перегоріло",
]

# ---------------------------------
# 3. Темы / услуги / профессии
# ---------------------------------
service_keywords = [
    # общие
    "мастер", "майстер", "бригад", "подсоб", "робіт", "рабоч",
    "ремонт", "будів", "строит", "отделк", "відділ",
    "специалист", "спеціаліст",

    # отделка / стройка
    "шпаклев", "шпаклю", "штукатур", "фарб", "покрас",
    "обои", "ламинат", "ламінат", "паркет",
    "плитк", "плиточ", "стяж",
    "гіпсокартон", "гипсокартон", "маляр",
    "сверл", "дрел", "бур", "перфоратор",

    # сантехника
    "сантех", "кран", "смесител", "змішувач", "унитаз",
    "канализац", "каналіза", "труб", "раковин", "мийк",
    "ванн", "душ", "бойлер", "сантехника", "сантехник",

    # электрика
    "электрик", "електрик", "электр", "електр",
    "розет", "выключател", "вимикач", "люстр", "светиль", "світиль",
    "щиток", "кабел", "проводк", "проводка", "автомат", "ламп",

    # мебель / сборка / дом
    "мебел", "мебл", "шкаф", "кухн", "сборк", "збірк", "гарнитур",
    "полк", "телевиз", "карниз", "кроват", "ліжк", "зеркал", "дзеркал",
    "двер", "замок", "навес", "установ", "встанов",

    # перевозка / грузчики
    "грузчик", "вантаж", "перевез", "перевоз", "переезд", "переїзд",
    "разгруз", "розвантаж", "погруз", "завантаж", "вывоз", "смітт", "мусор",

    # техника
    "стиральн", "пральн", "холодиль", "посудомоеч", "посудомийн",
    "духовк", "кондиционер", "кондиціонер", "микроволнов", "мікрохвиль",

    # окна / балкон
    "окн", "вікн", "балкон", "стекл", "скл", "жалюз",
]

# ---------------------------------
# 4. Явная реклама / спам
# ---------------------------------
negative_keywords = [
    "акция", "знижка", "скидка",
    "прайс", "прайс-лист",
    "портфолио", "портфоліо",
    "запись", "запис",
    "приглашаю", "пропоную",
    "предлагаю услуги", "пропоную послуги",
    "сертифицирован", "сертифік",
    "инстаграм", "instagram",
    "whatsapp", "viber",
]

negative_patterns = [
    r"https?://",
]

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
    # Игнор своих сообщений
    if event.out:
        return

    # Игнор пересланных
    if event.fwd_from:
        return

    raw_text = event.raw_text or ""
    if not raw_text.strip():
        return

    text = normalize_text(raw_text)

    # Слишком короткие сообщения игнорируем
    if len(text) < 5:
        return

    # Явный рекламный мусор
    negative_word = contains_any(text, negative_keywords)
    if negative_word:
        return

    if matches_negative_pattern(text):
        return

    # Ищем признаки
    intent_word = contains_any(text, intent_keywords)
    problem_word = contains_any(text, problem_keywords)
    service_word = contains_any(text, service_keywords)

    # Обязательно должна быть тема/услуга
    if not service_word:
        return

    # И должно быть либо намерение, либо проблема
    if not intent_word and not problem_word:
        return

    # Антидубликат
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

    trigger_info = []
    if intent_word:
        trigger_info.append(f"Намерение: {intent_word}")
    if problem_word:
        trigger_info.append(f"Проблема: {problem_word}")
    trigger_info.append(f"Тема: {service_word}")

    msg = "НАЙДЕН ЗАКАЗ\n\n"
    msg += "\n".join(trigger_info)
    msg += f"\nГруппа: {chat_name}"
    msg += f"\nАвтор: {author_tag}"
    msg += f"\nВремя: {msg_time}"

    if message_link:
        msg += f"\nСсылка: {message_link}"

    msg += f"\n\nСообщение:\n{raw_text}"

    await client.send_message(alert_chat, msg)


client.start()
print("Бот запущен и слушает сообщения...")
client.run_until_disconnected()
