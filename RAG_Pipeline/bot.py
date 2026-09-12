from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes
)

from dotenv import load_dotenv
import os

from generator import generate_answer


# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_question = update.message.text

    result = generate_answer(user_question)

    answer = result["answer"]

    await update.message.reply_text(answer)


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)

print("CEMK AI Assistant is running...")

app.run_polling()