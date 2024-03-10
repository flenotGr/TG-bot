from aiogram import Bot, Dispatcher, types, html
import asyncio
from aiogram import F
from aiogram.filters.command import Command
import pymysql
from utils.database import DataBaseChanger
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from random import shuffle
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from redis.asyncio.client import Redis


database = DataBaseChanger()
token = 'мой токен'


redis_client = Redis.from_url("redis://localhost:6379/0")
storage = RedisStorage(redis_client)
bot = Bot(token=token)
dp = Dispatcher(storage=storage)
hp = '❤️'


class BotState(StatesGroup):
    learning = State()
    level_change = State()
    change_amount = State()
    start = State()
    answers = State()


kb = [
    [types.InlineKeyboardButton(text='Учить слова')], 
    [types.InlineKeyboardButton(text="Показать список выученных слов")],
    [types.InlineKeyboardButton(text="Помощь")]
]

keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb, resize_keyboard=True)


@dp.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    kb = [[types.InlineKeyboardButton(text='начать изучение', callback_data='начать изучение')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb, resize_keyboard=True)
    text = """Привет! Я - бот, позволяющий быстрой изучать английские слова при помощи уникальной методики запоминания. \n

            Описание процесса изучений слов: \n
            Вы будете получать список слов выбранного уровня, каждое слово имеет жизни, когда вы лишите жизней все слова из списка,
            вы закончите изучение слов, а ваш прогресс сохранится.

            Список команд:
            /start - запустить бота
            /help - получить список команд
            /get_my_words - получить список всех изученных слов
            """
    await state.set_state(BotState.level_change)
    await message.answer(text, reply_markup=keyboard)



@dp.callback_query(F.data == "начать изучение", BotState.level_change)
async def learning(callback: types.CallbackQuery, state: FSMContext):
    kb = [[types.InlineKeyboardButton(text='B2', callback_data='b2')], [types.InlineKeyboardButton(text="B1", callback_data='b1')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb, resize_keyboard=True)
    await callback.message.answer("Слова какого уровня вы желаете изучить?", reply_markup=keyboard)
    await state.set_state(BotState.change_amount)




@dp.callback_query(F.data == 'b1', BotState.change_amount)
async def get(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BotState.learning)
    await state.update_data(level='b1')
    kb = [
        [types.InlineKeyboardButton(text="10 слов", callback_data='10')], 
        [types.InlineKeyboardButton(text="20 слов. А у вас неплохая память.)", callback_data='20')],
        [types.InlineKeyboardButton(text="30 слов. Вы гений?", callback_data='30')],
        [types.InlineKeyboardButton(text="40 слов. Удачи вам.", callback_data='40')]
    ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb, resize_keyboard=True)
    await callback.message.answer("Выберете кол-во слов, которое собирайтесь изучить за раз", reply_markup=keyboard)
    await callback.answer()
    
    try:
        await bot.delete_message(callback.message.chat.id, callback.message.message_id-1)
    except:
        pass



@dp.callback_query(F.data == 'b2', BotState.change_amount)
async def update(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BotState.learning)
    await state.update_data(level='b2')
    kb = [
        [types.InlineKeyboardButton(text="10 слов", callback_data='10')], 
        [types.InlineKeyboardButton(text="20 слов. А вас неплохая память.)", callback_data='20')],
        [types.InlineKeyboardButton(text="30 слов. Вы гений?", callback_data='30')],
        [types.InlineKeyboardButton(text="40 слов. Удачи вам.", callback_data='40')]
    ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb, resize_keyboard=True)

    await callback.message.answer("Выберете кол-во слов, которое собирайтесь изучить за раз", reply_markup=keyboard)
    await callback.answer()
    try:
        await bot.delete_message(callback.message.chat.id, callback.message.message_id-1)
    except:
        pass



@dp.callback_query(BotState.learning)
async def get_data(callback: types.CallbackQuery, state: FSMContext):
    global database
    amount = int(callback.data)
    await state.update_data(amount = amount)
    chat_id = str(callback.message.chat.id)
    #database.add_counter(chat_id, 10, 'b1')
    state_data = await state.get_data()
    table_name = f'eng_{state_data["level"]}'
    counter = database.get_counter(chat_id, state_data["level"])

    if counter == None:
        counter = 0
    else:
        counter = int(counter)

    await state.update_data(static_counter = counter)

    print(counter)

    kb = [
        [types.InlineKeyboardButton(text='Начать изучение', callback_data='start')]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb, resize_keyboard=True)



    data_json = []
    for i in database.get_data(amount, counter, table_name):
        i.update({'hp' : 3})
        data_json.append(i)

    dtj = data_json
    #shuffle(dtj)
    await state.update_data(data_json=data_json, dtj = dtj)

    answer = 'Список слов: \n'
    for i in data_json:
        word = i['eng_word'].replace(' ', '')
        answer += word + " | " + 'HP:' + hp*3  +'\n'
        

    await state.update_data(counter = 0)
    await callback.message.answer(answer, reply_markup=keyboard)
    await callback.answer()
    await state.set_state(BotState.start)



@dp.callback_query(F.data == 'start', BotState.start)
async def start_learning(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    builder = ReplyKeyboardBuilder()
    for i in data['dtj']:
        builder.add(types.KeyboardButton(text = i['ru_word']))

    keyboard_list = [types.KeyboardButton(text = i['ru_word']) for i in data['data_json']]
    builder.adjust(2)
    keyboard = builder.as_markup(resize_keyboard=True)
    await callback.message.answer(data['data_json'][data['counter']]['eng_word'], reply_markup=keyboard)
    await state.set_state(BotState.answers)


def check_hp(data_json):
    cheker = 0
    for i in data_json:
        if i['hp'] > 0:
            cheker = 1
    
    return cheker


@dp.message(BotState.answers)
async def learning(message: types.Message, state: FSMContext):
    data = await state.get_data()

    builder = ReplyKeyboardBuilder()
    for i in data['data_json']:
        builder.add(types.KeyboardButton(text = i['ru_word']))

    builder.adjust(2)
    keyboard = builder.as_markup(resize_keyboard=True)
    print(data)


    if message.text == data["data_json"][data["counter"]]["ru_word"]:
        data['data_json'][data['counter']]['hp'] -= 1
        data['counter'] += 1
        if data['counter'] == data['amount']:
            data['counter'] = 0
            k = data['data_json']
            shuffle(k)
            data['data_json'] = k

        if check_hp(data['data_json']):

            await message.answer('Вы ответили правильно')
            answer = ''
            for i in data['data_json']:
                word = i['eng_word'].replace(' ', '')
                if i['hp'] == 0:
                    view = '☠️'
                else:
                    view =  hp*i['hp']

                answer += word + " | " + 'HP:' + view  +'\n'

            await message.answer(answer)
            await message.answer(f'Следующее слово: {data["data_json"][data["counter"]]["eng_word"]}', reply_markup=keyboard)
            await state.update_data(data_json=data['data_json'], counter=data['counter'])
        else:
            database.add_counter(message.chat.id, data['static_counter'] + data['amount'], data['level'])
            kb = [[types.InlineKeyboardButton(text='Продолжить изучение', callback_data='начать изучение')]]
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb, resize_keyboard=True)
            await message.answer('Поздравляю! Вы выучили все слова из списка.', reply_markup=keyboard)
            await state.set_state(BotState.level_change)

            try:
                await bot.delete_message(callback.message.chat.id, callback.message.message_id-1)
            except:
                pass
            

    else:
        await message.answer(f'Вы ответили неправильно, перевод этого слова - {data["data_json"][data["counter"]]["ru_word"]}')
        data['data_json'].append(data["data_json"][data["counter"]])
        data['data_json'].pop(data["counter"])
        answer = ''
        for i in data['data_json']:
            word = i['eng_word'].replace(' ', '')
            if i['hp'] == 0:
                view = '☠️'
            else:
                view =  hp*i['hp']

            answer += word + " | " + 'HP:' + view  +'\n'

        await message.answer(answer)
        await message.answer(f'Следующее слово: {data["data_json"][data["counter"]]["eng_word"]}', reply_markup=keyboard)
        await state.update_data(data_json=data['data_json'], counter=data['counter'])


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())