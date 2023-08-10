import openai
from aiogram import Bot, Dispatcher, executor, types
from data.data import CUISINES, get_all_cuisine_call_keys
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.files import JSONStorage
from pathlib import Path
from aiogram.contrib.middlewares.i18n import I18nMiddleware
import asyncio
from dotenv import load_dotenv
import os

# TODO: check user requests numbers in day and block if 10 and more

load_dotenv()

BOT_KEY = os.getenv('BOT_KEY')
OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
I18N_DOMAIN = 'mybot'

openai.api_key = OPEN_AI_KEY

BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'

bot = Bot(BOT_KEY)
storage = JSONStorage('cook-bot-stores')
dp = Dispatcher(bot, storage=storage)

# Setup i18n middleware
i18n = I18nMiddleware(I18N_DOMAIN, LOCALES_DIR)
dp.middleware.setup(i18n)

# Alias for gettext method
_ = i18n.gettext


# States
class Form(StatesGroup):
    calories = State()
    products = State()
    dish = State()
    process = State()
    free = State()


async def on_startup(_):
    print('Bot started')


@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message):
    lang = message.from_user.language_code
    await set_by_store_default(message.from_user.id, lang)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(_('Cuisine')),
               types.KeyboardButton(_('Calories')),
               types.KeyboardButton(_('Product list')),
               types.KeyboardButton(_('Dish')))
    markup.add(types.KeyboardButton(_('Get recipe')),
               types.KeyboardButton(_('Clear selected')))
    await message.answer(_("Hello, it's your cooking bot!"), reply_markup=markup)
    await Form.free.set()


@dp.message_handler(commands=['about'], state='*')
async def about(message: types.Message):
    text = _('1. Specify your preferences such as cuisine, calorie range, ingredients, or dish name.\n'
             '2. Click the "Get Recipe" button to generate your customized recipe.\n'
             '3. Wait a moment while Bot works its magic.\n'
             '4. Voila! Your personalized recipe is ready for you to explore and enjoy.\n'
             '5. Skip specifying parameters and let Bot surprise you with a random recipe.')
    await message.answer(text)


# ----Cuisine----
# Handle the cuisine button click
@dp.message_handler(lambda message: message.text == _('Cuisine'), state=Form.free)
async def button_cuisine_handler(message: types.Message):
    markup = types.InlineKeyboardMarkup(one_time_keyboard=True)
    btns_list = []
    for key in CUISINES:
        item = CUISINES[key]
        btn = types.KeyboardButton(item['name'], callback_data=key)
        btns_list.append(btn)
    markup.add(*btns_list)
    await message.answer(_('Select the cuisine type:'), reply_markup=markup)
    await message.delete()


@dp.callback_query_handler(lambda call: call.data in get_all_cuisine_call_keys(), state=Form.free)
async def callback_cuisine(call: types.CallbackQuery):
    cuisine = call.data
    await store_user_data(call.message.chat.id, {'cuisine': cuisine})
    request = await get_join_request_for_chat(call.message.chat.id)
    await call.message.answer(request)
    await call.answer('Nice')


# ----Calories----
# Handle the calories button click
@dp.message_handler(lambda message: message.text == _('Calories'), state=Form.free)
async def button_calories_handler(message: types.Message):
    await Form.calories.set()
    await message.answer(_('Enter the number of kCal:'))
    await message.delete()


@dp.message_handler(state=Form.calories)
async def handle_calories_input(message: types.Message):
    calories = message.text
    # TODO: check calories
    await store_user_data(message.from_user.id, {'calories': calories})
    request = await get_join_request_for_chat(message.from_user.id)
    await message.answer(request)
    await Form.free.set()


# ---- Product list ----
@dp.message_handler(lambda message: message.text == _('Product list'), state=Form.free)
async def button_product_handler(message: types.Message):
    await message.answer(_('Enter a set of products:'))
    await Form.products.set()
    await message.delete()


@dp.message_handler(state=Form.products)
async def handle_products_input(message: types.Message):
    products = message.text
    await store_user_data(message.from_user.id, {'productList': products})
    request = await get_join_request_for_chat(message.from_user.id)
    await message.answer(request)
    await Form.free.set()


# ---- Dish ----
@dp.message_handler(lambda message: message.text == _('Dish'), state=Form.free)
async def button_dish_handler(message: types.Message):
    await message.answer(_('Enter the name of the dish:'))
    await Form.dish.set()
    await message.delete()


@dp.message_handler(state=Form.dish)
async def handle_dish_input(message: types.Message):
    dish = message.text
    await store_user_data(message.from_user.id, {'dish': dish})
    request = await get_join_request_for_chat(message.from_user.id)
    await message.answer(request)
    await Form.free.set()


# ---- Get recipe -----
@dp.message_handler(lambda message: message.text == _('Get recipe'), state=Form.free)
async def button_get_recipe_handler(message: types.Message):
    await Form.process.set()
    await message.answer(_('Please wait!'))
    await bot.send_chat_action(message.chat.id, 'typing')

    # async def delay_msgs():
    #     await bot.send_chat_action(message.chat.id, 'typing')
    #     await asyncio.sleep(5)
    #     await message.answer(_('Processing the order!'))
    #     await bot.send_chat_action(message.chat.id, 'typing')
    #     await asyncio.sleep(10)
    #     await message.answer(_("It's coming up! Wait..."))
    #     await bot.send_chat_action(message.chat.id, 'typing')
    # task = asyncio.create_task(delay_msgs())

    request = await get_common_request_ai(message.from_user.id)

    # def res_task():
    #     return generate_response(request)

    response = generate_response(request)
    # task.cancel()
    if not response:
        await message.answer(_('Ops! Something wrong! Press /start'))
    else:
        await message.answer(response)
    await Form.free.set()


# ---- Clear ----
@dp.message_handler(lambda message: message.text == _('Clear selected'), state=Form.free)
async def button_clear_handler(message: types.Message):
    lang = message.from_user.language_code
    await set_by_store_default(message.from_user.id, lang)
    await message.answer(_('Cleared'))


# ---- help ----
async def get_join_request_for_chat(user_id):
    saved = await retrieve_user_data(user_id)
    request = _('Selected dish recommendations!') + " " + _('Cuisine') + f": {saved['cuisine']}. " + _('Calories') + \
              f": {saved['calories']}. " + _('Product list') + f": {saved['productList']}. " + _('Dish') + \
              f": {saved['dish']}."
    return request


async def get_common_request_ai(user_id):
    saved = await retrieve_user_data(user_id)
    lang = saved['lang']
    if lang == 'uk':
        lang = 'ua'
    if saved['productList'] == 'random' and saved['cuisine'] == 'random' and saved['calories'] == 'random':
        return f"Generate creative cooking recipe" \
               f"Keep the recipe short and without auxiliary sentences. Result language: {lang}"

    request = f"Find an existing one or invent one cooking recipe: " \
              f"products: {saved['productList']}. cuisine {saved['cuisine']}. " \
              f"calories: {saved['calories']}kcal. dish: {saved['dish']}" \
              f"Provide clear and straightforward steps with minimal wording while ensuring " \
              f"recipe aligns with user preferences." \
              f"Result language: {lang}"
    return request


def generate_response(text):
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                   messages=[{"role": "assistant", "content": text}])
    if chat_completion and chat_completion.choices:
        return chat_completion.choices[0].message.content
    else:
        return None


# ----Store----
async def set_by_store_default(user_id, lang):
    await dp.storage.set_data(chat=user_id, data={
        'cuisine': 'random',
        'calories': 'random',
        'productList': 'random',
        'dish': 'random',
        'lang': lang,
    })


# Store user-specific data
async def store_user_data(user_id, data):
    current = await retrieve_user_data(user_id)
    current.update(data)
    await dp.storage.set_data(chat=user_id, data=current)


# Retrieve user-specific data
async def retrieve_user_data(user_id):
    data = await dp.storage.get_data(chat=user_id)
    return data


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
