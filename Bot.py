import os
import logging
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Configura logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Claves desde entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configura OpenRouter (usando SDK de OpenAI)
openai.api_key = OPENAI_API_KEY
openai.base_url = "https://openrouter.ai/api/v1"

# Función para analizar mensajes
async def analizar_y_filtrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text
    chat_id = update.message.chat_id
    msg_id = update.message.message_id
    user = update.message.from_user.username or update.message.from_user.first_name

    if not mensaje:
        return

    prompt = f"""Responde únicamente con "sí" o "no".
¿Este mensaje está relacionado con geopolítica? 
Mensaje: "{mensaje}" """

    try:
        respuesta = openai.ChatCompletion.create(
            model="openai/o4-mini-high",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3,
            temperature=0
        )['choices'][0]['message']['content'].strip().lower()

        if respuesta != "sí":
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            logging.info(f"Mensaje eliminado: @{user} → \"{mensaje}\"")
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🛑 Mensaje eliminado por no estar relacionado con geopolítica."
            )

    except Exception as e:
        logging.error(f"Error al procesar mensaje: {e}")

# Ejecutar bot
if __name__ == "__main__":
    if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
        raise ValueError("Faltan TELEGRAM_TOKEN u OPENAI_API_KEY en variables de entorno.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), analizar_y_filtrar))

    logging.info("🤖 Bot de geopolítica iniciado.")
    app.run_polling()
