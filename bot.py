import logging
import time
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import openai
import sqlite3
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import exceptions
from PIL import Image

zapomnit = "Запомни что ты UniroGPT-4, чат-бот с искуственным интеллектом разработанный в 2023 году компанией Uniro Lab"


# Set up the bot and OpenAI API credentials
bot_token = 'token'
api_key = 'token'

conn = sqlite3.connect('db.db')
logging.basicConfig(level=logging.INFO)
admins = [1902870641, 100000001]
bot = Bot(token=bot_token)
dp = Dispatcher(bot)

price_button = KeyboardButton("📄 Инструкция")
info_button = KeyboardButton("⚙️ Профиль")
works_button = KeyboardButton("💎 Наши проекты")
reg_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
reg_keyboard.add(price_button, info_button, works_button)

openai.api_key = api_key

messages = {}
alltokens = {}
new_topic_button = InlineKeyboardButton("Сбросить память", callback_data="new_topic")

# Создаем клавиатуру и добавляем на нее кнопку
keyboard = InlineKeyboardMarkup().add(new_topic_button)

# Command handler for /start
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
        try:
            cur = conn.cursor()
            useridblya = cur.execute(f"SELECT userid FROM users WHERE userid = {message.from_user.id};").fetchone()[0]
            print(useridblya)
        except:
            cur = conn.cursor()
            cur.execute(f"INSERT INTO users VALUES({message.from_user.id}, '{message.from_user.username}');")
            conn.commit()
        username = message.from_user.id
        username = str(username)
        messages[username] = []
        with open('hello.png', 'rb') as photo_file:
            photo = types.InputFile(photo_file)
        # отправка сообщения с фотографией и текстом
            await bot.send_photo(
                message.chat.id,
                photo,
                caption="Приветствую в боте Assistant Uniro, данный бот использует современную языковую модель UniroLab, а именно UniroGPT-4. \n\n<b> Вы можете задать свой вопрос, либо воспользоваться командами доступными по клавиатуре ниже:</b>",
                reply_markup=reg_keyboard,
                parse_mode="HTML"
            )

@dp.callback_query_handler(lambda c: c.data == 'new_topic')
async def process_new_topic(callback_query: types.CallbackQuery):
    try:
        userid = callback_query.from_user.id
        userid = str(userid)
        messages[userid] = []
        alltokens[userid] = [0]
        messages[userid].append({"role": "user", "content": zapomnit})
        messages[userid].append({"role": "assistant", "content": "Хорошо, я запомнил это!"})
        await bot.send_message(callback_query.message.chat.id, 'Память бота успешно обнулена!', parse_mode='Markdown')
    except Exception as e:
        logging.error(f'Error in process_new_topic: {e}')

# Command handler for /newtopic
@dp.message_handler(commands=['newtopic'])
async def new_topic_cmd(message: types.Message):
    try:
        userid = message.from_user.id
        userid = str(userid)
        messages[userid] = []
        alltokens[userid] = [0]
        messages[userid].append({"role": "user", "content": zapomnit})
        messages[userid].append({"role": "assistant", "content": "Хорошо, я запомнил это!"})
        await message.reply('Starting a new topic!  \n\nНачинаем новую тему! ', parse_mode='Markdown')
    except Exception as e:
        logging.error(f'Error in new_topic_cmd: {e}')

@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.chat.id not in admins:
        return
    cursor = conn.cursor()
    cursor.execute('SELECT userid FROM users')
    users = cursor.fetchall()
    await message.answer(f'Всего юзеров: {len(users)}\n/rassilka - рассылка')

class AdConversation(StatesGroup):
    get_text = State()
    get_photo = State()

@dp.message_handler(commands=['rassilka'])
async def admin_panel(message: types.Message, state: FSMContext):
    if message.chat.id not in admins:
        return
    await message.answer('Введите текст рекламы:')
    await AdConversation.get_text.set()
    
@dp.message_handler(state=AdConversation.get_text)
async def get_text(message: types.Message, state: FSMContext):
    text = message.text
    await message.answer('Пришлите картинку:')
    await AdConversation.get_photo.set()
    await state.update_data(text=text)

@dp.message_handler(content_types=['photo'], state=AdConversation.get_photo)
async def get_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()
    text = data['text']
    if not text:
        await message.answer('Вы не ввели текст рекламы.')
        return
    await send_ad(text, photo)
    await state.finish()


async def send_ad(text, photo):
    # Получаем список ID пользователей из таблицы users
    cursor = conn.cursor()
    cursor.execute('SELECT userid FROM users')
    users = cursor.fetchall()

    # Отправляем рекламную рассылку каждому пользователю из списка
    for user in users:
        try:
            await bot.send_photo(chat_id=user[0], photo=photo, caption=text)
        except exceptions.BotBlocked:
            print(f'Bot blocked by user with chat_id: {user[0]}')
        except exceptions.ChatNotFound:
            print(f'Chat not found for user with chat_id: {user[0]}')
        except exceptions.RetryAfter as e:
            print(f'Retry after {e.timeout} seconds.')
            await asyncio.sleep(e.timeout)
        except exceptions.TelegramAPIError:
            print(f'Telegram API error for user with chat_id: {user[0]}')
            continue

@dp.message_handler(text="📄 Инструкция")
async def send_instruction(message: types.Message):
    with open('instruct.png', 'rb') as photo_file:
        photo = types.InputFile(photo_file)
    await bot.send_photo(
        message.chat.id,
        photo,
        caption='<b>📊 Рекомендации по работе UNIRO GPT-4:</b>\n\n<b>• Список возможностей доступен по <a href="https://telegra.ph/Vozmozhnosti-Assistant-Uniro-03-30">данной ссылке</a></b>\n<b>• Рекомендации по созданию запросов <a href="https://telegra.ph/Gramotnye-zaprosy-dlya-Assistant-Uniro-03-30">доступны тут</a></b>\n<b>• Пользовательское соглашение <a href="https://telegra.ph/polzovatskoesoglashenie00">доступно тут</a></b>\n',
        reply_markup=reg_keyboard,
        parse_mode="HTML"
    )

@dp.message_handler(text="💎 Наши проекты")
async def send_projects(message: types.Message):
    with open('port.png', 'rb') as photo_file:
        photo = types.InputFile(photo_file)
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=photo,
        caption='<b>💎 Наши проекты доступны по ссылкам ниже:</b>\n\n<b>• Русскоязычный канал с работами студии: @UniroStudio</b>\n<b>• Наш бот для заказа в студии: @UniroStudioBot</b>\n<b>• Администрация проекта: @amvrluck и @flaxcode</b>',
        parse_mode='HTML',
        reply_markup=reg_keyboard
    )
@dp.message_handler(text="⚙️ Профиль")
async def send_profile(message: types.Message):
    user_id = message.from_user.id
    user = await bot.get_chat(user_id)
    photos = await bot.get_user_profile_photos(user_id)
    if len(photos.photos) > 0:
        photo = photos.photos[0][-1]
        file = await bot.get_file(photo.file_id)
        await bot.download_file(file.file_path, f'{message.from_user.id}.png')
        background = Image.open("Frame 30.png").convert("RGBA")
        overlay = Image.open(f'{message.from_user.id}.png').convert("RGBA")
        # Масштабируем наложенное изображение
        overlay = overlay.resize((329, 329))
        # Наложение изображения на фон
        background.paste(overlay, (780, 199), overlay)
        # Сохраняем результат
        background.save("result.png")
        with open('result.png', 'rb') as photo_file:
                photo = types.InputFile(photo_file)
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=photo,
                    caption=f'<b>⚙️ Ваш профиль</b>\n\n<b>✏️ Ваш юзернейм:</b> @{message.from_user.username}\n<b>🔒 Ваш айди:</b> {message.from_user.id}',
                    parse_mode='HTML',
                    reply_markup=reg_keyboard
                )
    else:
        background.save("Frame 30.png")
        with open('result.jpg', 'rb') as photo_file:
            photo = types.InputFile(photo_file)
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=photo,
                caption=f'<b>⚙️ Ваш профиль</b>\n\n<b>✏️ Ваш юзернейм:</b> @{message.from_user.username}\n<b>🔒 Ваш айди:</b> {message.from_user.id}',
                parse_mode='HTML',
                reply_markup=reg_keyboard
            )



# Message handler for all other messages
@dp.message_handler()
async def echo_msg(message: types.Message):


    chatgpt_task = asyncio.create_task(generate_chatgpt_response(message))
    await asyncio.gather(chatgpt_task)

                
                
async def generate_chatgpt_response(message):
            user_message = message.text
            user_id = str(message.from_user.id)

            
            user_message = message.text
            userid = message.from_user.id
            userid = str(userid)
            
            
            if userid not in messages:
                messages[userid] = []
                messages[userid].append({"role": "user", "content": zapomnit})
                messages[userid].append({"role": "assistant", "content": "Хорошо, я запомнил это!"})
            if userid not in alltokens:
                alltokens[userid] = [0]
            userid = message.from_user.id
            userid = str(userid)
            count = 0
            for i in message.text:
                count += 1
            new = int(alltokens[userid][0]) + count
            alltokens[userid][0] = new
            vcetok = int(alltokens[userid][0]) + 300
            if vcetok > 4000:
                await bot.send_message(message.from_user.id, "Память бота закончилась, вам необходимо, очистить ее, и повторить ваш запрос!", reply_markup=keyboard)
            messages[userid].append({"role": "user", "content": user_message})
            messages[userid].append({"role": "user", "content": f"chat: {message.chat} Сейчас {time.strftime('%d/%m/%Y %H:%M:%S')} user: {message.from_user.first_name} message: {message.text}"})
            logging.info(f'{userid}: {user_message}')
            
            
            should_respond = not message.reply_to_message or message.reply_to_message.from_user.id == bot.id

            if should_respond:
                
                processing_message = await message.reply(
                    'Ваш запрос обрабатывается, пожалуйста подождите ',
                    parse_mode='Markdown')

                
                await bot.send_chat_action(chat_id=message.chat.id, action="typing")

                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages[userid],
                    max_tokens=2048,
                    temperature=1.0,
                    frequency_penalty=0,
                    presence_penalty=0,
                    user=userid
                )
                            
                chatgpt_response = completion.choices[0]['message']
                messages[userid].append({"role": "assistant", "content": chatgpt_response['content']})
                logging.info(f'ChatGPT response: {chatgpt_response["content"]}')

                            
                await message.reply(chatgpt_response['content'], parse_mode='Markdown', reply_markup=keyboard)
                print(chatgpt_response['content'])
                count=0
                for i in chatgpt_response['content']:
                    count += 1
                    new = int(alltokens[userid][0]) + count
                    alltokens[userid][0] = new
                    print(alltokens[userid][0])
                            
                    await bot.delete_message(chat_id=processing_message.chat.id, message_id=processing_message.message_id)

            return




if __name__ == '__main__':
    executor.start_polling(dp)  
