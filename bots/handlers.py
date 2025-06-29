from io import BytesIO
import os, tempfile,requests,base64
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile, BotCommand
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          filters, ContextTypes, CallbackQueryHandler, CallbackContext)
import asyncio
from services.murf_tts import murf_websocket_tts
from services.murf_translate import translate_text
from services.geoLocation import reverse_geocode
from services.tour_guide_llm import generate_tour_guide_reply,extract_destination_from_query
from bot.global_state import get_user_location, set_user_location, get_user_cleaned_location, get_user_location_coordinates, get_user_language, get_user_preferences
from Variables import MURF_LANGUAGES
from cfg import TELEGRAM_BOT_TOKEN
from bot.global_state import locations_collection
import time
from services.routing import get_directions, geocode_search
import assemblyai as aai




async def get_user_or_warn(update: Update) -> dict | None:
    user_id = update.effective_user.id
    user = locations_collection.find_one({"user_id": user_id})

    if not user:
        if update.message:
            await update.message.reply_text("⚠️ Please start the bot first by sending /start.")
        elif update.callback_query:
            await update.callback_query.answer("⚠️ Send /start before using the bot.", show_alert=True)
        return None

    return user

# ========== COMMAND HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    locations_collection.update_one(
        {"user_id": user_id},
        {"$setOnInsert": {"user_id": user_id, "username": username, "language": "en-US", "message_type": "default"}},
        upsert=True
    )
    welcome_message = (
        f"👋 Hello {username}!\n\n"

        "🗺️ Welcome to the Murf Virtual Tour Guide Bot!\n\n"
        "With me, you can:\n"
        "🎤 Speak or type your travel questions\n"
        "📍 Share your location to get local guidance\n"
        "🗣️ Receive spoken answers in your preferred language\n"
        "🚏 Ask for directions to nearby spots\n\n"
        "To get started:\n"
        "1️⃣ Share your location 📍\n"
        "2️⃣ Choose message type with /setmsgtype\n"
        "3️⃣ Set your language with /setlanguage\n\n"
        "Then just ask away! (e.g. 'Where is the ticket counter?', 'What's nearby?')\n"
        "Let’s explore together! 🌏"
    )
    await update.message.reply_text(
        f"{welcome_message}",
        reply_markup=language_keyboard()
    )

def language_keyboard():
    buttons = [
        [InlineKeyboardButton(name, callback_data=code)]
        for code, name in MURF_LANGUAGES.items()
    ]
    return InlineKeyboardMarkup(buttons)

async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_lang = query.data
    user_id = query.from_user.id
    locations_collection.update_one(
        {"user_id": user_id},
        {"$set": {"language": selected_lang}}
    )
    await query.edit_message_text(f"✅ Language set to {MURF_LANGUAGES[selected_lang]}\n")

async def set_message_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_or_warn(update)
    if not user:
        return
    keyboard = [
        [InlineKeyboardButton("✅ Audio", callback_data="type_audio")],
        [InlineKeyboardButton("✅ Text", callback_data="type_text")],
        [InlineKeyboardButton("✅ Default (Both)", callback_data="type_default")]
    ]
    await update.message.reply_text("Select the type of message you'd like to receive:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_type = query.data.replace("type_", "")
    locations_collection.update_one({"user_id": query.from_user.id}, {"$set": {"message_type": selected_type}})
    await query.edit_message_text(f"✅ Message type set to: {selected_type}")

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = await get_user_or_warn(update)
    if not user:
        return
    
    await update.message.reply_text(
        "🌐 Choose your preferred language:",
        reply_markup=language_keyboard()
    )


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user_or_warn(update)
    if not user:
        return
    user_id = update.effective_user.id
    locations_collection.delete_one({"user_id": user_id})
    await update.message.reply_text("🗑️ Your data has been permanently deleted.")

async def send_text_and_or_audio(context, chat_id, text, user_id):
    """
    Helper to send text and/or audio based on user message_type preference.
    Splits long text messages to fit Telegram's 4096 character limit.
    """
    lang, message_type = get_user_preferences(user_id)
    sent = False
    def split_message(msg, max_len=4096):
        return [msg[i:i+max_len] for i in range(0, len(msg), max_len)]
    if message_type in ("text", "default"):
        for part in split_message(text):
            await context.bot.send_message(chat_id=chat_id, text=f"📝 {part}")
        sent = True
    if message_type in ("audio", "default"):
        audio_path = await murf_websocket_tts(text, lang)
        if audio_path:
            with open(audio_path, 'rb') as audio_file:
                await context.bot.send_voice(chat_id=chat_id, voice=audio_file)
            sent = True
        else:
            await context.bot.send_message(chat_id=chat_id, text="❌ TTS failed.")
    if not sent:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ No valid message type set.")

async def handle_tour_guide_reply(context, chat_id, user_id, translated_text):
    print(f"[ handle_tour_guide_reply ] Translated text for handle_tour_guide_reply : {translated_text}")
    destination = extract_destination_from_query(translated_text)
    print(f"[ handle_tour_guide_reply ] Destination extracted: {destination}")
    if destination:
        await context.bot.send_message(chat_id=chat_id, text=f"📍 Getting directions to {destination}...")
        try:
            start_lat, start_lon = get_user_location_coordinates(user_id)
            dest_lat, dest_lon = geocode_search(destination,start_lat, start_lon)
            if dest_lat is None or dest_lon is None:
                await context.bot.send_message(chat_id=chat_id, text="❓ Couldn't find the destination on the map.")
                return
            reply = get_directions(start_lat, start_lon, dest_lat, dest_lon)
            await send_text_and_or_audio(context, chat_id, reply, user_id)
            return
        except Exception as e:
            print(f"[ROUTING ERROR] {e}")
            await context.bot.send_message(chat_id=chat_id, text="❌ Error while fetching directions.")
            return
    try:
        lat, lon = get_user_location_coordinates(user_id)
        location_hint = get_user_location(user_id)
    except Exception as e:
        print(f"[LOCATION ERROR] {e}")
        await context.bot.send_message(chat_id=chat_id, text="❓ Unable to retrieve your location. Please share your location again.")
        return
    if location_hint is None:
        await context.bot.send_message(chat_id=chat_id, text="❓ Unable to retrieve your location. Please share your location again.")
        return
    reply = generate_tour_guide_reply(translated_text, lat, lon, location_hint)
    await context.bot.send_message(chat_id=chat_id, text="🎤 Generating audio...")
    translated_reply = translate_text(reply, get_user_language(user_id))
    await send_text_and_or_audio(context, chat_id, translated_reply, user_id)

async def handle_telegram_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # if update.message.text.startswith("/"):
    #     await update.message.reply_text("❗Please use the provided buttons or valid commands.")
    #     return  # Ignore command text (already handled elsewhere)

    user = await get_user_or_warn(update)
    if not user:
        return
    print(f"[UPDATE] Received update from user {user['user_id']} ({user['username']})")
    print(update)

    # 👇 Handling live location updates
    if update.edited_message and update.edited_message.location:
        user_id = update.edited_message.from_user.id
        last_update = user.get("last_location_time", 0)
        print("Time difference:", time.time() - last_update)
        if time.time() - last_update < 30:
            return

        # Save new timestamp in DB
        locations_collection.update_one(
            {"user_id": user_id},
            {"$set": {"last_location_time": time.time()}}
        )

        lat = update.edited_message.location.latitude
        lon = update.edited_message.location.longitude

        location_name = reverse_geocode(lat, lon)
        if location_name:
            parts = location_name.split(", ")
            cleaned_location = ", ".join(parts[:3])
            set_user_location(user_id, cleaned_location, lat, lon)
            print(f"[LIVE LOCATION] Updated user {user_id}: {cleaned_location}")
        return

    if update.message:
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id
        if update.message.text:
            text = update.message.text
            await context.bot.send_message(chat_id=chat_id, text="🧠 Thinking...")
            translated_text = translate_text(text, "en-US")
            if not translated_text:
                await context.bot.send_message(chat_id=chat_id, text="⚠️ Translation failed. Using original text.")
                translated_text = text
            await handle_tour_guide_reply(context, chat_id, user_id, translated_text)
        elif update.message.voice:
            user_id = update.message.from_user.id
            chat_id = update.message.chat_id
            await context.bot.send_message(chat_id=chat_id, text="🎤 Voice message received. Processing... \n 🧠 Thinking...")
            voice = await context.bot.get_file(update.message.voice.file_id)
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, f"{voice.file_id}.ogg")
            await voice.download_to_drive(file_path)
            
            try:
                transcribe_result = azure_transcribe_audio(file_path)
                if transcribe_result and "text" in transcribe_result:
                    transcribed_text = transcribe_result["text"]
                else:
                    transcribed_text = None
                if not transcribed_text:
                    await context.bot.send_message(chat_id=chat_id, text="❌ Transcription failed.")
                    return
                # Now use transcribed_text for further processing
                print(f"[VOICE] transcribed_text: {transcribed_text}")
                translated_text = translate_text(transcribed_text, "en-US")
                if not translated_text:
                    await context.bot.send_message(chat_id=chat_id, text="⚠️ Translation failed. Using original text.")
                    translated_text = transcribed_text
                
                await handle_tour_guide_reply(context, chat_id, user_id, translated_text)
            except Exception as e:
                print(f"[VOICE ERROR] {e}")
                await context.bot.send_message(chat_id=chat_id, text="⚠️ Something went wrong during voice processing.")
        elif update.message.photo:
            await context.bot.send_message(chat_id=chat_id, text="🖼️ Photo received. Landmark detection soon!")
        elif update.message.location:
            chat_id = update.message.chat_id
            user_id = update.message.from_user.id
            lat = update.message.location.latitude
            lon = update.message.location.longitude
            await context.bot.send_message(chat_id=chat_id, text="📍 Getting your location...")
            location_name = reverse_geocode(lat, lon)
            if not location_name:
                await context.bot.send_message(chat_id=chat_id, text="❓ Unable to identify your location.")
                return
            set_user_location(user_id, location_name, lat, lon)
            cleaned_location = get_user_cleaned_location(user_id)
            reply_text = f"You are currently near {cleaned_location}."
            await context.bot.send_message(chat_id=chat_id, text=f"📍 Got your location: {cleaned_location}")
            # await context.bot.send_message(chat_id=chat_id, text="🗣 Generating audio...")
            translated_reply = translate_text(reply_text, get_user_language(user_id))
            await send_text_and_or_audio(context, chat_id, translated_reply, user_id)

def azure_transcribe_audio(file_path):
    """
    Send audio file to Azure OpenAI transcription endpoint and return the transcription text.
    """
    import requests
    url = "https://ironk-mcg85dcf-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-4o-transcribe/audio/transcriptions?api-version=2025-03-01-preview"
    api_key = "3mZxBeyiQ446wX38qbiv1CkHqJ18gBhXFQjoBzavJ9tXRL3FoqRDJQQJ99BFACHYHv6XJ3w3AAAAACOGI0eR"  # Replace with your actual key
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    files = {
        "file": open(file_path, "rb"),
    }
    data = {
        "model": "gpt-4o-transcribe"
    }
    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[AZURE TRANSCRIBE ERROR] {response.status_code}: {response.text}")
            return None
    finally:
        files["file"].close()

async def set_commands(app):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("setlanguage", "Set your preferred language"),
        BotCommand("setmsgtype", "Set output message type"),
        BotCommand("end", "Delete your data"),
    ]
    await app.bot.set_my_commands(commands)

    


if __name__ == "__main__":
    locations_collection.delete_many({})
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).post_init(set_commands).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(language_selection, pattern="^" + "|".join(MURF_LANGUAGES.keys()) + "$"))
    app.add_handler(CommandHandler("end", end))
    app.add_handler(CommandHandler("setmsgtype", set_message_type))
    app.add_handler(CallbackQueryHandler(handle_type_selection, pattern="^type_"))
    app.add_handler(CommandHandler("setlanguage", set_language))
    app.add_handler(MessageHandler(filters.TEXT | filters.VOICE | filters.LOCATION, handle_telegram_update))
    # app.add_handler(MessageHandler(filters.TEXT | filters.VOICE | filters.PHOTO | filters.LOCATION, handle_telegram_update))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, handle_telegram_update))  # for live location
    print("🤖 Bot is running...")
    app.run_polling()
