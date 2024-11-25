import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from yandex_cloud_ml_sdk import YCloudML
from fuzzywuzzy import process

# Настройки логирования
logging.basicConfig(level=logging.INFO)

# Настройки бота и API
TELEGRAM_TOKEN = "7655073751:AAGDQ2Pu8R_gfRIcAxBNGqbbUw87JJAEEtU"
YANDEX_FOLDER_ID = "b1gmabqgljp5vbjve7re"
YANDEX_API_KEY = "AQVN3MyWJEvb9W6HxDlirajmBBlXM9q9gbTZFg1r"
# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Инициализация Yandex Cloud SDK
sdk = YCloudML(folder_id=YANDEX_FOLDER_ID, auth=YANDEX_API_KEY)
model = sdk.models.completions('yandexgpt')
model = model.configure(temperature=0.5)

# Данные для работы
schools = ["Школа №1", "Школа №2", "Школа №3"]
children_registry = {}
knowledge_base = {
    "как записаться в школу": "Чтобы записаться в школу, напишите название школы и имя ребенка.",
    "расписание": "Расписание занятий вы можете узнать на сайте школы.",
}
forbidden_topics = ["взлом", "оскорбления", "нецензурные выражения"]

# Проверка на запрещенные темы
def is_forbidden_topic(message: str) -> bool:
    return any(topic in message.lower() for topic in forbidden_topics)

# Классификация запроса
def classify_request(message: str):
    if "школа" in message.lower():
        return "Запись в школу"
    elif any(key in message.lower() for key in ["услуга", "образование"]):
        return "Услуги образования"
    else:
        return "Неопределено"

# Поиск ответа в базе знаний
def find_answer_in_knowledge_base(question: str) -> str:
    question_normalized = question.lower()
    best_match, score = process.extractOne(question_normalized, knowledge_base.keys())
    return knowledge_base[best_match] if score > 70 else None

# Обработчик команды /start
@dp.message(Command(commands=["start"]))
async def start_command(message: Message):
    await message.answer("Привет! Я ваш помощник в вопросах образования. Чем могу помочь?")

# Обработчик текстовых сообщений
@dp.message(F.text)
async def handle_message(message: Message):
    try:
        user_message = message.text

        # Проверка на запрещенные темы
        if is_forbidden_topic(user_message):
            await message.answer("Эта тема запрещена.")
            return

        # Классификация запроса
        request_type = classify_request(user_message)

        if request_type == "Запись в школу":
            if "записать" in user_message.lower():
                # Уточнение данных
                await message.answer("Какого ребенка вы хотите записать? Укажите имя.")
            elif "в школу" in user_message.lower():
                await message.answer(f"Выберите школу: {', '.join(schools)}")
            elif user_message in schools:
                child_name = "Имя ребенка"  # Заменить на имя из контекста
                if child_name in children_registry:
                    current_school = children_registry[child_name]
                    await message.answer(f"Ребенок уже записан в {current_school}.")
                else:
                    children_registry[child_name] = user_message
                    await message.answer(f"Ребенок успешно записан в {user_message}.")

        elif request_type == "Услуги образования":
            await message.answer("Эта услуга пока не реализована.")

        else:
            # Попытка найти ответ в базе знаний
            answer = find_answer_in_knowledge_base(user_message)
            if answer:
                await message.answer(answer)
            else:
                await message.answer("Извините, я не понял ваш вопрос. Попробуйте переформулировать.")

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")

# Основная функция запуска
async def main():
    logging.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
