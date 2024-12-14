import os
import logging
import shutil
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from downloads import download_files_from_yandex
from exl2img import process_excel_files
from config import ya_token, tg_token

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            link TEXT
        )
        """
    )
    conn.commit()
    conn.close()

# Добавление или обновление ссылки пользователя
def save_user_link(user_id, link):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (user_id, link)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET link = ?
        """,
        (user_id, link, link)
    )
    conn.commit()
    conn.close()

# Получение ссылки пользователя
def get_user_link(user_id):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT link FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start."""
    update.message.reply_text(
        "Привет! Я помогу скачать файлы с Яндекс.Диска и конвертировать их в PNG.\n"
        "Используй /setlink для установки ссылки на публичную папку Яндекс.Диска."
    )

def set_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрашивает ссылку на публичную папку Яндекс.Диска."""
    update.message.reply_text(
        "Пожалуйста, отправьте мне ссылку на вашу публичную папку Яндекс.Диска."
    )

def save_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняет ссылку на Яндекс.Диск для пользователя."""
    link = update.message.text
    user_id = update.message.from_user.id
    save_user_link(user_id, link)
    update.message.reply_text(
        f"Ссылка сохранена! Теперь вы можете использовать /process для обработки файлов."
    )

def clean_temp(user_id):
    """Удаляет временные файлы пользователя."""
    user_temp_path = f"temp/{user_id}"
    if os.path.exists(user_temp_path):
        shutil.rmtree(user_temp_path)

def process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс скачивания и обработки файлов."""
    user_id = update.message.from_user.id
    link = get_user_link(user_id)
    if not link:
        update.message.reply_text(
            "Вы ещё не установили ссылку на папку. Используйте /setlink."
        )
        return

    save_path = f"temp/{user_id}/downloads"
    output_path = f"temp/{user_id}/output"

    try:
        update.message.reply_text("Скачиваю файлы с Яндекс.Диска...")
        download_files_from_yandex(link, ya_token, save_path)
        update.message.reply_text("Файлы скачаны! Начинаю конвертацию...")

        process_excel_files(save_path, output_path)

        for file_name in os.listdir(output_path):
            file_folder = os.path.join(output_path, file_name)
            if os.path.isdir(file_folder):
                update.message.reply_text(f"Файл: {file_name}")
                for img_file in os.listdir(file_folder):
                    img_path = os.path.join(file_folder, img_file)
                    with open(img_path, 'rb') as img:
                        update.message.reply_photo(photo=img)

        update.message.reply_text("Обработка завершена!")
    except Exception as e:
        logger.error(e)
        update.message.reply_text("Произошла ошибка при обработке файлов. Проверьте ссылку и попробуйте снова.")
    finally:
        clean_temp(user_id)

def main():
    """Основная функция для запуска бота."""
    init_db()
    application = ApplicationBuilder().token(tg_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setlink", set_link))
    application.add_handler(CommandHandler("process", process))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_link))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
