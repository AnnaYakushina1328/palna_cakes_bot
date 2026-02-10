import telebot
import sqlite3
import json
import os
from datetime import datetime

# ===== НАСТРОЙКИ =====
BOT_TOKEN = '8384839588:AAGTR4bXgWe1LchAl18P6683frZOic0aMao'  # ← СЮДА ВСТАВЬТЕ СВОЙ ТОКЕН
ADMIN_CHAT_ID = '431584671'  # ← СЮДА ВСТАВЬТЕ ВАШ ID (узнать через @userinfobot)

bot = telebot.TeleBot(BOT_TOKEN)

# ===== БАЗА ДАННЫХ =====
def init_db():
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            items TEXT,
            total INTEGER,
            name TEXT,
            phone TEXT,
            address TEXT,
            delivery_date TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Инициализация при старте
init_db()

# ===== КНОПКИ =====
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add('🧁 Бенто-тортики', '🎂 Торты')
    markup.add('🥞 Панкейки', '🛒 Корзина')
    markup.add('📞 Связаться с кондитером')
    return markup

def catalog_buttons(category):
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    if category == 'bento':
        markup.add(
            telebot.types.InlineKeyboardButton('Классические (350₽)', callback_data='add_bento_classic'),
            telebot.types.InlineKeyboardButton('С персонажами (600₽)', callback_data='add_bento_char'),
            telebot.types.InlineKeyboardButton('Набор 4 шт (1200₽)', callback_data='add_bento_set4')
        )
    elif category == 'cakes':
        markup.add(
            telebot.types.InlineKeyboardButton('1-2 кг (2000₽)', callback_data='add_cake_small'),
            telebot.types.InlineKeyboardButton('3-5 кг (4000₽)', callback_data='add_cake_large')
        )
    elif category == 'pancakes':
        markup.add(
            telebot.types.InlineKeyboardButton('6 шт (400₽)', callback_data='add_pancakes_6'),
            telebot.types.InlineKeyboardButton('12 шт (700₽)', callback_data='add_pancakes_12')
        )
    markup.add(telebot.types.InlineKeyboardButton('← Назад в меню', callback_data='back_to_menu'))
    return markup

def cart_buttons(cart):
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    for idx, item in enumerate(cart):
        markup.add(telebot.types.InlineKeyboardButton(
            f'❌ Удалить: {item["name"]}',
            callback_data=f'remove_{idx}'
        ))
    markup.add(
        telebot.types.InlineKeyboardButton('✏️ Оформить заказ', callback_data='checkout'),
        telebot.types.InlineKeyboardButton('🔄 Очистить корзину', callback_data='clear_cart'),
        telebot.types.InlineKeyboardButton('← Назад в меню', callback_data='back_to_menu')
    )
    return markup

# ===== ХРАНЕНИЕ КОРЗИН =====
user_carts = {}  # {user_id: [{'name': '...', 'price': 350}, ...]}

def get_cart(user_id):
    if user_id not in user_carts:
        user_carts[user_id] = []
    return user_carts[user_id]

def add_to_cart(user_id, item):
    cart = get_cart(user_id)
    cart.append(item)

def clear_cart(user_id):
    if user_id in user_carts:
        user_carts[user_id] = []

# ===== КОМАНДЫ И ОБРАБОТЧИКИ =====
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        '✨ Добро пожаловать в мою кондитерскую!\n\n'
        'Здесь вы можете заказать:\n'
        '• 🧁 Бенто-тортики — мини-шедевры 100г\n'
        '• 🎂 Торты на любой повод\n'
        '• 🥞 Нежные панкейки с начинкой\n\n'
        '❗️Заказы принимаются за 3 дня до даты получения',
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: m.text == '🧁 Бенто-тортики')
def show_bento(message):
    bot.send_photo(
        message.chat.id,
        'https://i.imgur.com/5XJmZQl.jpg',  # ← можно заменить на своё фото
        caption='🧁 Бенто-тортики\n\n'
                '• Вес: 100-120 г каждый\n'
                '• Начинки: ванильная, шоколадная, творожный крем, фруктовый конфитюр\n'
                '• Украшение: свежие ягоды, фрукты, шоколадный декор',
        reply_markup=catalog_buttons('bento')
    )

@bot.message_handler(func=lambda m: m.text == '🎂 Торты')
def show_cakes(message):
    bot.send_photo(
        message.chat.id,
        'https://i.imgur.com/8GkR0fP.jpg',
        caption='🎂 Торты ручной работы\n\n'
                '• От 1 до 5 кг\n'
                '• Любая тематика: мультфильмы, хобби, фото\n'
                '• Коржи: бисквит, медовик, чизкейк',
        reply_markup=catalog_buttons('cakes')
    )

@bot.message_handler(func=lambda m: m.text == '🥞 Панкейки')
def show_pancakes(message):
    bot.send_photo(
        message.chat.id,
        'https://i.imgur.com/3WYV0dT.jpg',
        caption='🥞 Панкейки с начинкой\n\n'
                '• Мягкие, воздушные, диаметр 10 см\n'
                '• Начинки: сгущёнка, нутелла, ягоды, творог\n'
                '• Подача: в коробочке с сиропом',
        reply_markup=catalog_buttons('pancakes')
    )

@bot.message_handler(func=lambda m: m.text == '📞 Связаться с кондитером')
def contact(message):
    bot.send_message(
        message.chat.id,
        '💬 Напишите мне напрямую:\n@AnnaYakushina\n\n'
        'Или позвоните: +7 (XXX) XXX-XX-XX\n\n'
        'Работаю ежедневно с 9:00 до 20:00',
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: m.text == '🛒 Корзина')
def show_cart(message):
    cart = get_cart(message.chat.id)
    if not cart:
        bot.send_message(
            message.chat.id,
            '🛒 Ваша корзина пуста',
            reply_markup=main_menu()
        )
        return
    
    text = '🛒 ВАША КОРЗИНА:\n\n'
    total = 0
    for idx, item in enumerate(cart, 1):
        text += f'{idx}. {item["name"]} — {item["price"]}₽\n'
        total += item["price"]
    
    text += f'\nИТОГО: {total}₽'
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=cart_buttons(cart)
    )

# ===== ОБРАБОТКА КНОПОК =====
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.message.chat.id
    
    # Добавление в корзину
    if call.data.startswith('add_'):
        items = {
            'add_bento_classic': {'name': 'Бенто классическое', 'price': 350},
            'add_bento_char': {'name': 'Бенто с персонажем', 'price': 600},
            'add_bento_set4': {'name': 'Набор бенто 4 шт', 'price': 1200},
            'add_cake_small': {'name': 'Торт 1-2 кг', 'price': 2000},
            'add_cake_large': {'name': 'Торт 3-5 кг', 'price': 4000},
            'add_pancakes_6': {'name': 'Панкейки 6 шт', 'price': 400},
            'add_pancakes_12': {'name': 'Панкейки 12 шт', 'price': 700},
        }
        if call.data in items:
            add_to_cart(user_id, items[call.data])
            bot.answer_callback_query(call.id, '✅ Добавлено в корзину!', show_alert=True)
            bot.delete_message(user_id, call.message.message_id)
            bot.send_message(user_id, 'Товар добавлен в корзину!', reply_markup=main_menu())
    
    # Удаление из корзины
    elif call.data.startswith('remove_'):
        idx = int(call.data.split('_')[1])
        cart = get_cart(user_id)
        if 0 <= idx < len(cart):
            removed = cart.pop(idx)
            bot.answer_callback_query(call.id, f'❌ Удалено: {removed["name"]}')
            show_cart(call.message)
    
    # Очистка корзины
    elif call.data == 'clear_cart':
        clear_cart(user_id)
        bot.answer_callback_query(call.id, 'Корзина очищена')
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, '🛒 Корзина очищена', reply_markup=main_menu())
    
    # Назад в меню
    elif call.data == 'back_to_menu':
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, 'Выберите категорию:', reply_markup=main_menu())
    
    # Оформление заказа
    elif call.data == 'checkout':
        cart = get_cart(user_id)
        if not cart:
            bot.answer_callback_query(call.id, 'Корзина пуста!')
            return
        
        # Сохраняем корзину для следующего шага
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(
            user_id,
            '✏️ ОФОРМЛЕНИЕ ЗАКАЗА\n\n'
            'Напишите ваше имя:'
        )
        bot.register_next_step_handler(call.message, get_name)

# ===== ШАГИ ОФОРМЛЕНИЯ ЗАКАЗА =====
def get_name(message):
    user_id = message.chat.id
    user_data = {'name': message.text, 'cart': get_cart(user_id)}
    bot.send_message(user_id, '📱 Укажите телефон для связи:')
    bot.register_next_step_handler(message, get_phone, user_data)

def get_phone(message, user_data):
    user_data['phone'] = message.text
    bot.send_message(user_id=message.chat.id, text='📍 Адрес доставки или самовывоз?')
    bot.register_next_step_handler(message, get_address, user_data)

def get_address(message, user_data):
    user_data['address'] = message.text
    bot.send_message(
        message.chat.id,
        '📅 На какую дату нужен заказ? (например: 15 февраля)'
    )
    bot.register_next_step_handler(message, save_order, user_data)

def save_order(message, user_data):
    user_id = message.chat.id
    user_data['delivery_date'] = message.text
    
    # Считаем итог
    total = sum(item['price'] for item in user_data['cart'])
    items_text = '\n'.join(f'• {item["name"]} — {item["price"]}₽' for item in user_data['cart'])
    
    # Сохраняем в БД
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (user_id, username, items, total, name, phone, address, delivery_date, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        message.from_user.username or '',
        json.dumps(user_data['cart']),
        total,
        user_data['name'],
        user_data['phone'],
        user_data['address'],
        user_data['delivery_date'],
        datetime.now().strftime('%Y-%m-%d %H:%M')
    ))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Отправляем вам уведомление
    admin_text = (
        f'🔔 НОВЫЙ ЗАКАЗ #{order_id}\n\n'
        f'Имя: {user_data["name"]}\n'
        f'Телефон: {user_data["phone"]}\n'
        f'Адрес: {user_data["address"]}\n'
        f'Дата: {user_data["delivery_date"]}\n\n'
        f'Товары:\n{items_text}\n\n'
        f'ИТОГО: {total}₽'
    )
    bot.send_message(ADMIN_CHAT_ID, admin_text)
    
    # Отправляем клиенту подтверждение
    client_text = (
        f'✅ ЗАКАЗ ПРИНЯТ #{order_id}\n\n'
        f'Имя: {user_data["name"]}\n'
        f'Телефон: {user_data["phone"]}\n'
        f'Адрес: {user_data["address"]}\n'
        f'Дата получения: {user_data["delivery_date"]}\n\n'
        f'Ваш заказ:\n{items_text}\n\n'
        f'ИТОГО: {total}₽\n\n'
        f'❗️Я свяжусь с вами в течение часа для подтверждения деталей и оплаты.'
    )
    bot.send_message(user_id, client_text, reply_markup=main_menu())
    
    # Очищаем корзину
    clear_cart(user_id)

# ===== ЗАПУСК =====
# Вебхук-эндпоинт (обязательно для работы с Web Service)
@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return '403 Forbidden', 403

# Проверка работоспособности
@app.route('/')
def index():
    return '✅ Бот работает!'

# Установка вебхука при запуске
@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_URL', 'your-app.onrender.com')}/{BOT_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    
if __name__ == '__main__':
    # Устанавливаем вебхук при старте
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_URL', 'your-app.onrender.com')}/{BOT_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    print(f'✅ Вебхук установлен: {webhook_url}')
    
    # Запускаем Flask на порту из переменной окружения
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

