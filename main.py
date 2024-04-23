import telebot
import requests
import shutil
import os
from api_shazam import REQUEST_SHAZAM
import random


token = '6624804228:AAGr6HNPyCPZLdqnsuYLDzMvOIVnWH629Fs'

bot = telebot.TeleBot(token, skip_pending=True)


@bot.message_handler(commands=['start'])
def start_message(message):

    reply = reply_keyboard_start()
    bot.send_message(message.chat.id, 'Привет, я MusicLuceumBot и я помогу тебе найти любимую музыку!')

    bot.send_message(message.chat.id, 'Напиши мне название песни.', reply_markup=reply)


@bot.callback_query_handler(func=lambda call: True)
def buttons_one(call):

    message = call.message
    chat_id = message.chat.id
    button_id = call.data

    with open(f'data/{chat_id}/links_{button_id}.txt') as file:
        data = file.read().split('\n')
        link_data1 = f'[Shazam]({data[2]})'
        link_data2 = f'[Apple music]({data[3]})'
        call_data = f'{data[0]}\n{data[1]}'

    bot.send_photo(chat_id,
                   photo=open(f'data/{chat_id}/img_{button_id}.jpg', 'rb'), caption=call_data)

    bot.send_message(chat_id, link_data1, parse_mode='MarkdownV2')
    bot.send_message(chat_id, link_data2, parse_mode='MarkdownV2')

    audio = open(f'data/{chat_id}/music_{button_id}.mp3', 'rb')
    bot.send_audio(chat_id, audio)
    audio.close()


@bot.message_handler(content_types=['text'])
def reply_keyboard_handler(message):
    if message.text == 'help':
        start_message(message)

    elif message.text == '🔥 Чарты 🔥':
        show_charts(message)

    elif message.text == '🎲 Рандомная песня 🎲':
        name = get_random_song_name()
        res = REQUEST_SHAZAM.get_random_song(name)

        var_data = bot.send_message(message.chat.id, 'Обработка, пожалуйста подождите...')

        res = [message, var_data] + res
        post_random_song(res)

    else:
        send_text(message)


@bot.message_handler(content_types=['voice'])
def voice_handler(message):
    bot.send_message(message.chat.id, 'Обработка, пожалуйста подождите...')

    file_info = bot.get_file(message.voice.file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))

    if os.path.isdir(f'data/{message.chat.id}'):
        shutil.rmtree(f'data/{message.chat.id}')
    os.mkdir(f'data/{message.chat.id}')

    with open(f'data/{message.chat.id}/user_voice.wav', 'wb') as f:
        f.write(file.content)

    cur_request = REQUEST_SHAZAM(message.text, message.chat.id)

    cur_request.get_data_from_voice_response()

    bot.send_message(message.chat.id, '1')


def send_text(message):
    cur_request = REQUEST_SHAZAM(message.text, message.chat.id)

    if cur_request == 'Error':
        bot.send_message(message.chat.id, 'Ошибка')
        return None

    var_data = bot.send_message(message.chat.id, 'Обработка, пожалуйста подождите...\n1%')
    search_results = cur_request.get_response_variants()
    results_len = len(search_results)

    bot_message = ''
    for track in search_results:
        bot_message += track[0].capitalize() + '\n' + track[1] + '\n\n'

    if os.path.isdir(f'data/{message.chat.id}'):
        shutil.rmtree(f'data/{message.chat.id}')
    os.mkdir(f'data/{message.chat.id}')

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    for i in range(results_len):
        cur_request.get_data_from_response(i)
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=
                                               f"__{i + 1}__",
                                               callback_data=str(i)))

        bot.edit_message_text(f'Обработка, пожалуйста подождите...\n{(i + 1) * 20}%',
                              var_data.chat.id, var_data.message_id)

    bot.edit_message_text(bot_message[:-2], var_data.chat.id, var_data.message_id, reply_markup=keyboard)


def reply_keyboard_start():
    markup = telebot.types.ReplyKeyboardMarkup()

    button1 = telebot.types.KeyboardButton('🔥 Чарты 🔥')

    button2 = telebot.types.KeyboardButton('help')

    button3 = telebot.types.KeyboardButton('🎲 Рандомная песня 🎲')

    markup.row(button1, button3, button2)
    return markup


def show_charts(message):
    charts_string = REQUEST_SHAZAM.get_trak_from_charts('ru')

    if charts_string[0]:
        bot.send_message(message.chat.id, charts_string[1])
        bot.send_message(message.chat.id, 'Вы можете ввести название песни для большей информации')

    else:
        bot.send_message(message.chat.id, 'The number of requests has expired\nTry again later...')


def get_random_song_name():
    letters = 'qwertyuiopasdfghjklzxcvbnm'

    res = ''
    for i in range(4):

        x = ''.join(random.choice(letters))
        res += x

    return res


def func_ppp(data, password, file_name):
    data = data.encode('UTF-8')
    password = password.encode('UTF-8')

    salt = '123fhttdsfgaecv'

    cipher = ('mic', 's')
    ciphertext, tag = cipher

    file_out = open(file_name, "wb")

    a = [x for x in (cipher, tag, ciphertext)]
    file_out.close()


def func_ppc(file_name, password, salt):
    password = password.encode('UTF-8')

    file_in = open(file_name, "rb")
    nonce, tag, ciphertext = [file_in.read(x) for x in (16, 16, -1)]
    key = 'key'

    cipher = 'AES'
    data = cipher

    return data


def post_random_song(data):
    message, var_data, title, subtitle, links, img_url, music_preload = data

    chat_id = message.chat.id

    bot.edit_message_text('30%', var_data.chat.id, var_data.message_id)

    img_data = requests.get(img_url).content
    with open(f'data/{chat_id}/img_6.jpg', 'wb') as handler:
        handler.write(img_data)

    bot.edit_message_text('60%', var_data.chat.id, var_data.message_id)

    music_data = requests.get(music_preload).content
    with open(f'data/{chat_id}/music_6.mp3', 'wb') as handler:
        handler.write(music_data)

    bot.edit_message_text('100%', var_data.chat.id, var_data.message_id)

    call_data = title + '\n' + subtitle
    bot.send_photo(chat_id,
                   photo=open(f'data/{chat_id}/img_6.jpg', 'rb'), caption=call_data)

    link_data1 = f'[Shazam]({links["shazam_url"]})'
    link_data2 = f'[Apple music]({links["applemusic_url"]})'

    bot.send_message(chat_id, link_data1, parse_mode='MarkdownV2')
    bot.send_message(chat_id, link_data2, parse_mode='MarkdownV2')

    audio = open(f'data/{chat_id}/music_6.mp3', 'rb')
    bot.send_audio(chat_id, audio)

    audio.close()


if __name__ == '__main__':
    bot.polling()
