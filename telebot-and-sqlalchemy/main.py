from sqlalchemy import select

from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from telebot import types

from database import authors, books, conn


class User:
    def __init__(self, first_name: str, last_name: str, age: int, chat_id: int):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.chat_id = chat_id

    def __repr__(self):
        return f'User(first name: {self.first_name}, last_name: {self.last_name}, age: {self.age})'


users: list[User | None] = []
new_user: User | None = None

WELCOME: str = '''Привет! Это телеграм бот мастерской по Python!
Советую нажать для начала на /something :)
А чтобы познакомиться, можешь нажать на /reg 
Если хочешь почитать что-нибудь по Python, нажми /all_books!'''

BOT_TOKEN: str = '6148944879:AAF1p6l8uZtQy8c1BDS_Q9kPorE8n06EvRs'

bot = TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['help', 'start', 'info', 'all_books'])
def send_welcome(message: Message):
    if message.text == '/help' or message.text == '/start':

        bot.send_message(chat_id=message.chat.id,
                         text=WELCOME)
    elif message.text == '/info':
        key_board = types.InlineKeyboardMarkup(
            [
                [types.InlineKeyboardButton(text='GitHub',
                                            url='https://github.com/arikmaster22/workshop-python'
                                            )
                 ],

                [types.InlineKeyboardButton(text='Notion',
                                            url='https://educated-ambert-8c7.notion.site/Python-f340b5dcdad248f2acc5a26afd79e7ec'
                                            )
                 ],
            ]
        )

        bot.send_message(chat_id=message.chat.id,
                         text='Ссылки на материалы', reply_markup=key_board)

    elif message.text == '/all_books':
        select_query = select(books)

        result = conn.execute(select_query).all()

        parsed_books = parse_books(result)

        for book in parsed_books:
            bot.send_message(chat_id=message.chat.id, text=book)


@bot.message_handler(commands=['something'])
def send_rick_roll(message: Message):
    bot.send_message(chat_id=message.chat.id,
                     text="<a href='https://www.youtube.com/watch?v=dQw4w9WgXcQ'>Тыкни!</a>", parse_mode='HTML',
                     disable_web_page_preview=True)


@bot.message_handler(commands=['reg'])
def reg(message: Message):
    bot.send_message(chat_id=message.chat.id,
                     text='Введи свое имя, фамилию и возраст в формате фамилия имя возраст. Например, Муниев Аркадий 30 лет')

    bot.register_next_step_handler(message=message, callback=signup)


@bot.message_handler(content_types=['text'])
def signup(message: Message):
    parse_message = message.text.split()

    if len(parse_message) <= 3:
        bot.send_message(chat_id=message.chat.id, text='Чего-то не хватает :(')
        bot.register_next_step_handler(message=message, callback=signup)
    elif len(parse_message) == 4:
        try:
            first_name, last_name, age = parse_message[0], parse_message[1], int(parse_message[2])

            global new_user

            new_user = User(first_name=first_name, last_name=last_name,
                            age=age, chat_id=message.chat.id)

            keyboard = types.InlineKeyboardMarkup()  # клавиатура
            key_yes = types.InlineKeyboardButton(
                text='Да', callback_data='yes')  # кнопка «Да»
            keyboard.add(key_yes)  # добавление кнопки в клавиатуру

            key_no = types.InlineKeyboardButton(
                text='Нет', callback_data='no')  # кнопка «Нет»
            keyboard.add(key_no)  # добавление кнопки в клавиатуру

            question = f'Тебя зовут {first_name}, {last_name} и тебе {age} лет?'
            bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
        except TypeError:
            bot.send_message(chat_id=message.chat.id, text='Неправильно ввел возраст')
            bot.register_next_step_handler(message=message, callback=signup)
    else:
        bot.send_message(chat_id=message.chat.id, text='Слишком много параметров')
        bot.register_next_step_handler(message=message, callback=signup)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call: CallbackQuery):
    if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
        users.append(new_user)
        print(users)
        bot.send_message(chat_id=call.message.chat.id, text='Запомню :)')
    elif call.data == "no":
        bot.send_message(chat_id=call.message.chat.id, text='Введи еще раз свое имя, фамилию и возраст')
        bot.register_next_step_handler_by_chat_id(
            call.message.chat.id, callback=signup)


def parse_books(data):
    parsed_books: list[str | None] = [None] * len(data)
    for i in range(len(data)):
        select_query_author_name = select(authors.c.name).where(data[i][2] == authors.c.id)

        author_name = conn.execute(select_query_author_name).scalar()

        parsed_books[i] = f'Title: {data[i][1]}\nAuthor: {author_name}\nPrice: {data[i][4]}\nGenre: {data[i][3]}'

    return parsed_books


if __name__ == '__main__':
    bot.infinity_polling()
