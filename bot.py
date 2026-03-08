from telethon import TelegramClient, events
import os

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
alert_chat = os.getenv("ALERT_CHAT")

keywords = [

    # работа RU
    "мастер",
    "муж",
    "помощ",
    "рабоч",
    "подработ",
    "подсоб",
    "бригада",
    "работ",
    "исполнител",

    # работа UA
    "майстер",
    "робіт",
    "праців",
    "підроб",
    "допомог",
    "бригада",

    # ремонт
    "ремонт",
    "строит",
    "будів",
    "відділ",
    "шпаклев",
    "шпаклю",
    "штукатур",
    "штукатурк",
    "покрас",
    "фарб",
    "обо",
    "ламінат",
    "ламинат",
    "плит",
    "плитк",
    "стяж",
    "гіпсокартон",
    "гипсокартон",
    "сверл",
    "бур",
    "дрел",
    "перфоратор",

    # сантехника
    "сантех",
    "кран",
    "смесител",
    "змішувач",
    "унитаз",
    "засор",
    "каналіза",
    "канализац",
    "труб",
    "труба",
    "раковин",
    "мийк",
    "ванн",
    "душ",
    "бойлер",

    # электрика
    "електрик",
    "электрик",
    "електр",
    "электр",
    "провод",
    "проводк",
    "розет",
    "вимикач",
    "выключател",
    "люстр",
    "світиль",
    "светиль",
    "ламп",
    "щиток",
    "автомат",
    "кабел",

    # мебель
    "мебел",
    "мебл",
    "шкаф",
    "кухн",
    "гарнитур",
    "збірк",
    "сборк",

    # перевозки
    "перевез",
    "перевоз",
    "перевезт",
    "грузчик",
    "вантаж",
    "переезд",
    "переїзд",
    "разгруз",
    "розвантаж",
    "погруз",
    "завантаж",
    "мусор",
    "смітт",
    "вывоз",

    # техника
    "стиральн",
    "пральн",
    "холодиль",
    "посудомоеч",
    "посудомийн",
    "плит",
    "духовк",
    "кондиціонер",
    "кондиционер",
    "мікрохвиль",
    "микроволнов",

    # монтаж
    "полк",
    "полиц",
    "телевиз",
    "карниз",
    "кроват",
    "ліжк",
    "зеркал",
    "дзеркал",
    "двер",
    "дверц",
    "замок",
    "ручк",
    "навес",
    "установ",
    "встанов",

    # окна
    "окн",
    "вікн",
    "балкон",
    "скл",
    "жалюз",

    # срочность
    "срочн",
    "термін",
    "сьогодні",
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
