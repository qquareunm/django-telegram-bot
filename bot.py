import os
import django
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from asgiref.sync import sync_to_async

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tg_proj.settings')  # Замените 'tg_proj.settings' на ваш файл настроек
django.setup()

# Импорт моделей после настройки Django
from tg_app.models import Director, Movie, Review

# Создание клавиатуры
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [['Directors'], ['Movies'], ['Reviews']],
        resize_keyboard=True
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветственное сообщение с клавиатурой."""
    await update.message.reply_text(
        "Welcome to the Movie Info Bot! Use the buttons below to explore:",
        reply_markup=get_main_keyboard()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений."""
    text = update.message.text.lower()

    if text == "directors":
        await get_directors(update, context)
    elif text == "movies":
        await get_movies(update, context)
    elif text == "reviews":
        await get_reviews(update, context)
    else:
        await update.message.reply_text(
            "I didn't understand that. Please use the buttons.",
            reply_markup=get_main_keyboard()
        )

async def get_directors(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправка списка режиссёров."""
    directors = await sync_to_async(list)(Director.objects.all())
    if directors:
        response = "Directors:\n"
        for director in directors:
            response += f"{director.first_name} {director.last_name} (Born: {director.birth_date})\n"
    else:
        response = "No directors found in the database."
    await update.message.reply_text(response)

async def get_movies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправка списка фильмов."""
    movies = await sync_to_async(list)(Movie.objects.select_related('director').all())
    if movies:
        response = "Movies:\n"
        for movie in movies:
            response += (f"{movie.title} by {movie.director.first_name} {movie.director.last_name} "
                         f"(Released: {movie.release_date}, Genre: {movie.genre}, Rating: {movie.rating}/10)\n")
    else:
        response = "No movies found in the database."
    await update.message.reply_text(response)

async def get_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправка списка отзывов."""
    reviews = await sync_to_async(list)(Review.objects.select_related('movie__director').all())
    if reviews:
        response = "Reviews:\n"
        for review in reviews:
            response += (f"{review.reviewer_name} rated {review.movie.title} {review.rating}/5: "
                         f"{review.comment}\n")
    else:
        response = "No reviews found in the database."
    await update.message.reply_text(response)

def main():
    application = Application.builder().token("7992053210:AAF2wEOQqeoel19oK_bHyIaHjo6dCzFfCcA").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
