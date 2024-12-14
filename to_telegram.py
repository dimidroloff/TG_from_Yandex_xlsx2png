from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
import shutil
from downloads import download_files_from_yandex
from exl2img import process_excel_files
from config import ya_token, tg_token
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Память для хранения данных пользователей
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start."""
    await update.message.reply_text(
        "Привет! Я помогу скачать файлы с Яндекс.Диска и конвертировать их в PNG.\n"
        "Используй /setlink для установки ссылки на публичную папку Яндекс.Диска."
    )

async def set_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрашивает ссылку на публичную папку Яндекс.Диска."""
    await update.message.reply_text(
        "Пожалуйста, отправьте мне ссылку на вашу публичную папку Яндекс.Диска."
    )

async def save_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняет ссылку на Яндекс.Диск для пользователя."""
    link = update.message.text
    user_id = update.message.from_user.id
    user_data[user_id] = {'link': link}
    await update.message.reply_text(
        "Ссылка сохранена! Теперь вы можете использовать /process для обработки файлов."
    )

def clean_temp(user_id):
    """Удаляет временные файлы пользователя."""
    user_temp_path = f"temp/{user_id}"
    if os.path.exists(user_temp_path):
        shutil.rmtree(user_temp_path)

async def process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс скачивания и обработки файлов."""
    user_id = update.message.from_user.id
    if user_id not in user_data or 'link' not in user_data[user_id]:
        await update.message.reply_text(
            "Вы ещё не установили ссылку на папку. Используйте /setlink."
        )
        return

    link = user_data[user_id]['link']
    save_path = f"temp/{user_id}/downloads"
    output_path = f"temp/{user_id}/output"

    try:
        await update.message.reply_text("Скачиваю файлы с Яндекс.Диска...")
        download_files_from_yandex(link, ya_token, save_path)
        await update.message.reply_text("Файлы скачаны! Начинаю конвертацию...")

        process_excel_files(save_path, output_path)

        for file_name in os.listdir(output_path):
            file_folder = os.path.join(output_path, file_name)
            if os.path.isdir(file_folder):
                await update.message.reply_text(f"Файл: {file_name}")
                for img_file in os.listdir(file_folder):
                    img_path = os.path.join(file_folder, img_file)
                    with open(img_path, 'rb') as img:
                        await update.message.reply_photo(photo=img)

        await update.message.reply_text("Обработка завершена!")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Произошла ошибка при обработке файлов. Проверьте ссылку и попробуйте снова.")
    finally:
        clean_temp(user_id)

def main():
    """Основная функция для запуска бота."""
    application = ApplicationBuilder().token(tg_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setlink", set_link))
    application.add_handler(CommandHandler("process", process))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_link))

    application.run_polling()

if __name__ == "__main__":
    main()