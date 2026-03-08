from telethon import TelegramClient, events
import os

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
alert_chat = os.getenv("ALERT_CHAT")

keywords = [
    # работа
    "мастер",
    "муж",
    "помощ",
    "рабоч",
    "подработ",
    "подсоб",
    "бригада",
    "работ",
    "исполнител",

    # ремонт
    "ремонт",
    "строит",
    "отделк",
    "шпаклев",
    "штукатур",
    "покрас",
    "обо",
    "ламинат",
    "паркет",
    "плит",
    "стяж",
    "гипсокартон",
    "сверл",
    "бур",
    "дрел",
    "перфоратор",

    # сантехника
    "сантех",
    "кран",
    "смесител",
    "унитаз",
    "засор",
    "канализац",
    "труб",
    "раковин",
    "ванн",
    "душ",
    "бойлер",

    # электрика
    "электрик",
    "электр",
    "провод",
    "розет",
    "выключател",
    "люстр",
    "светиль",
    "ламп",
    "щиток",
    "автомат",
    "кабел",

    # мебель
    "мебел",
    "шкаф",
    "кухн",
    "гарнитур",
    "собрат",
    "сборк",

    # переезд
    "перевез",
    "перевоз",
    "грузчик",
    "переезд",
    "разгруз",
    "погруз",
    "мусор",
    "вывоз",

    # техника
    "стиральн",
    "холодиль",
    "посудомоеч",
    "плит",
    "духовк",
    "кондиционер",
    "микроволнов",

    # монтаж
    "полк",
    "телевиз",
    "карниз",
    "кроват",
    "зеркал",
    "двер",
    "замок",
    "ручк",
    "навес",
    "установ",

    # окна
    "окн",
    "балкон",
    "стекл",
    "жалюз",

    # срочность
    "срочн",
    "сегодня",
    "завтра",
]

client = TelegramClient("session", api_id, api_hash)

@client.on(events.NewMessage)
async def handler(event):
    if event.out:
        return

    if event.fwd_from:
        return

    text = (event.raw_text or "").lower()

    matched_word = None
    for word in keywords:
        if word in text:
            matched_word = word
            break

    if matched_word:
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

        msg = f"""НАЙДЕНО СОВПАДЕНИЕ

Слово: {matched_word}
Группа: {chat_name}
Автор: {author_tag}
Время: {msg_time}

Сообщение:
{event.raw_text}
"""

        await client.send_message(alert_chat, msg)

client.start()
print("Бот запущен и слушает сообщения...")
client.run_until_disconnected()