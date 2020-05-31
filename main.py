import datetime
import os.path
from time import sleep

import requests
import telebot
from bs4 import BeautifulSoup
from selenium import webdriver
from telebot import types

token = '1245925386:AAFCCTqi6scyUsPo3BkyJ4e7YHpaGqs-NgU' # подключение токена
bot = telebot.TeleBot(token)


def get_html(url, proxy=None): #получение юрл страницы
    r = requests.get(url)
    return r.text


# In[2]:


@bot.message_handler(commands=["future_matches"])  # раздел с рассписанием матчей
def future_matches(message):
    h = 'https://www.hltv.org/matches'
    url = get_html(h)
    soup = BeautifulSoup(url, 'lxml')
    days = []
    for i in soup.find('div', class_='upcoming-matches').find_all('div', class_='match-day')[0:9]:
        days.append(i.find('span', class_='standard-headline').text)
    markup = types.InlineKeyboardMarkup(1)
    for i in days:
        if i.split(' ')[0] == datetime.date.today().strftime("%Y-%m-%d"):
            text = 'Сегодня'
        elif i.split(' ')[0] == (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"):
            text = 'Завтра'
        else:
            text = i
        button = types.InlineKeyboardButton(text=text, callback_data=i)
        markup.add(button)

    bot.send_message(chat_id=message.chat.id, text='Какая дата вас интересует', reply_markup=markup)


@bot.message_handler(commands=["live_matches"]) #раздел с лайв матчами
def live_matches(message):
    try:
        markup = types.InlineKeyboardMarkup(1)
        h = 'https://www.hltv.org/matches'
        url = get_html(h)
        soup = BeautifulSoup(url, 'lxml')
        global matches
        global links
        matches = []
        links = []
        for i in soup.find('div', class_='live-matches').find_all('div', class_="live-match"):
            try:
                teams = i.find_all('span', class_='team-name')
                team1 = str(teams[0]).split('">')[1].split('<')[0] #вибор 1 команды
                team2 = str(teams[1]).split('">')[1].split('<')[0] #вибор 2 команды
                vs = team1 + " против " + team2
                markup.add(types.InlineKeyboardButton(text=vs, callback_data=vs))
                matches.append(vs)
                links.append('https://www.hltv.org/' + str(i).split('href="')[1].split('">')[0])
            except:
                pass
        bot.send_message(message.chat.id, "Выбери интересующий тебя матч", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "На данный момент лайв матчи отсутствуют")


@bot.message_handler(commands=["my_fauvorite_teams"]) #раздел с интересующими командами
def my_fauvorite_teams(message):
    try:
        f = open(str(message.chat.id) + '.txt', 'r')
        teams = f.read()
        bot.send_message(message.chat.id, teams)
    except:
        bot.send_message(message.chat.id, 'Ваш список пуст')


@bot.message_handler(commands=["append_my_fauvorite_teams"])  #раздел с добавлением интересующих команд
def append_my_fauvorite_teams(message):
    if not os.path.exists(str(message.chat.id) + '.txt'):
        f = open(str(message.chat.id) + '.txt', 'w')
        f.close()
    bot.send_message(message.chat.id, "Введите название вашей любимой команды")

    @bot.message_handler(content_types=["text"])
    def search_team(message):
        bot.send_message(chat_id=message.chat.id, text='Ищем...')
        try:
            h = 'https://www.hltv.org/search?query=' + message.text
            url = get_html(h)
            soup = BeautifulSoup(url, 'lxml')
            for i in soup.find_all('table', class_='table'):
                if str(i).split('table-header">')[1].split('<')[0] == 'Team':
                    teams_soup = i
            global team_names
            team_names = []
            team_links = []
            for i in teams_soup.find_all('td', class_='')[0:5]:  #поиск команды с таким названием на сайте
                if i.text not in team_names:
                    team_names.append(i.text)
                    team_links.append(
                        'https://www.hltv.org' + str(i.find('a', href=True)).split('href="')[1].split('"><img')[0])
            team_members = []
            for i in team_links:
                url = get_html(i)
                soup = BeautifulSoup(url, 'lxml')
                team_members.append([j.text for j in soup.find_all('span', class_='text-ellipsis bold')])  #добавление всех членов команды
            markup = types.InlineKeyboardMarkup(1)
            text = ''
            for i, j in zip(team_names, team_members):
                text += i + ':\n-- ' + '\n-- '.join(j) + '\n\n'
                markup.add(types.InlineKeyboardButton(text=i, callback_data=i))

            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id + 1, text=text,
                                  reply_markup=markup)
        except:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id + 1,
                                  text='Не найдено ниодной команды')


@bot.callback_query_handler(func=lambda call: True)
def choose_scene(call):
    global zz
    zz = call.data   #Глобальная переменная колбекдаты кнопок бот
    try:
        if zz in team_names: #оформление раздела с любимыми командами
            f = open(str(call.message.chat.id) + '.txt', 'a')
            f.write('\n' + zz)
            f.close()

            if not os.path.exists(str(call.message.chat.id) + '.txt'):
                f = open(str(zz) + '.txt', 'w')
                f.write('\n' + call.message.chat.id)
                f.close()
            else:
                f = open(str(zz) + '.txt', 'a')
                f.write('\n' + str(call.message.chat.id))
                f.close()

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=zz + ' Добавлена в список ваших любимых команд\n\nЧтобы посмотреть список всех любимых команд, отправте /my_fauvorite_teams')
    except:
        pass
    try:
        if zz in matches: #оформление раздела с выбраным матчем
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Грузим...')
            global driver
            try:
                driver.get(links[matches.index(zz)])
            except:
                driver = webdriver.Chrome('C:/webdrivers/chromedriver.exe')
                driver.get(links[matches.index(zz)])
                driver.maximize_window()
            sleep(1)

            markup = types.InlineKeyboardMarkup(1)
            button1 = types.InlineKeyboardButton(text="Пики-баны", callback_data="1")
            button2 = types.InlineKeyboardButton(text="Информация о текущей карте", callback_data="2")
            button3 = types.InlineKeyboardButton(text="Статистика игроков", callback_data="3")
            button4 = types.InlineKeyboardButton(text="Письменная транслиция", callback_data="4")
            button5 = types.InlineKeyboardButton(text="Выйти", callback_data="5")
            markup.add(button1, button2, button3, button4, button5)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Что хотите узнать', reply_markup=markup)
    except:
        pass

    try:
        h = 'https://www.hltv.org/matches' #получение информации о предстоящих матчах
        url = get_html(h)
        soup = BeautifulSoup(url, 'lxml')
        days = []
        for i in soup.find('div', class_='upcoming-matches').find_all('div', class_='match-day')[0:9]:
            days.append(i.find('span', class_='standard-headline').text)
        if zz in days:
            markup = types.InlineKeyboardMarkup(1)
            button = types.InlineKeyboardButton(text="Вернуться к выбору дня", callback_data="89")
            markup.add(button)

            prev_text = ''
            text = soup.find('div', class_='upcoming-matches').find_all('div', class_='match-day')[days.index(zz)].find(
                'span', class_='standard-headline').text + '\n----------------------------------------\n'
            for i in soup.find('div', class_='upcoming-matches').find_all('div', class_='match-day')[
                days.index(zz)].find_all('div', class_='match'):
                match = i.text.split('\n')
                if match[6] == '' and match[13] == '':
                    match_line = match[4] + ' ' + match[17] + '\n' + match[8] + ' ' + match[11] + ' ' + match[
                        14] + ' ' + match[19]
                elif match[6] == '' and match[13] != '':
                    match_line = match[4] + ' ' + match[15] + '\n' + match[8] + ' ' + match[11] + ' ' + match[
                        13] + ' ' + match[19]
                else:
                    match_line = match[4] + ' ' + match[6]
                text += match_line + '\n\n'

            if text != prev_text:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                                      reply_markup=markup)
                prev_stat_text = stat_text
    except:
        pass
    if zz == "1": #оформление раздела с информацией о выбраном матче->пики баны
        try:
            prev_map_text = ''
            markup = types.InlineKeyboardMarkup(1)
            button2 = types.InlineKeyboardButton(text="Информация о текущей карте", callback_data="2")
            button3 = types.InlineKeyboardButton(text="Статистика игроков", callback_data="3")
            button4 = types.InlineKeyboardButton(text="Письменная транслиция", callback_data="4")
            button5 = types.InlineKeyboardButton(text="Выйти", callback_data="5")
            markup.add(button2, button3, button4, button5)

            maps = '\n'.join( #получение информации о матче с сайта
                driver.find_element_by_class_name('maps').find_element_by_class_name('standard-box').text.replace('\n',
                                                                                                                  '').split(
                    '*'))
            picks = driver.find_element_by_class_name('maps').find_elements_by_class_name('standard-box')[1].text
            map_text = maps + '\n' + picks + '\n'
            for i in (driver.find_elements_by_class_name('mapholder')):
                map_info = i.text.replace('\n', ' ').split(' ', 1)
                map_text += 'ᅠ' * 3 + map_info[0] + ':\n' + map_info[1] + '\n'

            if map_text != prev_map_text:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=map_text,
                                      reply_markup=markup)
                prev_map_text = map_text

            time_one = datetime.datetime.now().timestamp()
            while zz == "1":
                try:
                    time_two = datetime.datetime.now().timestamp()
                    if time_two - time_one > 3:
                        time_one = time_two
                        maps = '\n'.join(driver.find_element_by_class_name('maps').find_element_by_class_name(
                            'standard-box').text.replace('\n', '').split('*'))
                        picks = driver.find_element_by_class_name('maps').find_elements_by_class_name('standard-box')[
                            1].text
                        map_text = maps + '\n' + picks + '\n'
                        for i in (driver.find_elements_by_class_name('mapholder')):
                            map_info = i.text.replace('\n', ' ').split(' ', 1)
                            map_text += 'ᅠ' * 3 + map_info[0] + ':\n' + map_info[1] + '\n'

                        if map_text != prev_map_text:
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                  text=map_text, reply_markup=markup)

                            prev_map_text = map_text
                except:
                    break
        except: #оформление раздела с информацией о матче в случае если произошла ошибка и бот не смог отобразить какуето информацию
            markup = types.InlineKeyboardMarkup(1)
            button1 = types.InlineKeyboardButton(text="Пики-баны", callback_data="1")
            button2 = types.InlineKeyboardButton(text="Информация о текущей карте", callback_data="2")
            button3 = types.InlineKeyboardButton(text="Статистика игроков", callback_data="3")
            button4 = types.InlineKeyboardButton(text="Письменная транслиция", callback_data="4")
            button5 = types.InlineKeyboardButton(text="Выйти", callback_data="5")
            markup.add(button1, button2, button3, button4, button5)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Не получилось узнать информацию\n\nЧто хотите узнать', reply_markup=markup)
    elif zz == "2":
        try: #оформление раздела с информацией о выбраном матче->Информация о текущей карте
            prev_text = ''
            markup = types.InlineKeyboardMarkup(1)
            button1 = types.InlineKeyboardButton(text="Пики-баны", callback_data="1")
            button3 = types.InlineKeyboardButton(text="Статистика игроков", callback_data="3")
            button4 = types.InlineKeyboardButton(text="Письменная транслиция", callback_data="4")
            button5 = types.InlineKeyboardButton(text="Выйти", callback_data="5")
            markup.add(button1, button3, button4, button5)
            time_one = datetime.datetime.now().timestamp()
            time_three = time_one

            round_line = driver.find_element_by_class_name('topbarBg').text.split('\n')#получение информации о матче с сайта
            teams = driver.find_element_by_class_name('content').find_elements_by_class_name('teamName')
            first_team = teams[0].text
            second_team = teams[1].text
            is_bomb = driver.find_element_by_xpath( #информация о наличии установленой бомбы
                '/html/body/div[3]/div/div[2]/div[1]/div[2]/div[6]/div/div[1]/div[2]/div/div[1]/div[3]/div[2]/img').get_attribute(
                'src').split('/')[-1]
            if is_bomb == 'bomb.png':
                bomb = ' '
            else:
                bomb = ' бомба '

            first_line = round_line[0] + bomb + round_line[4] + '\n' + first_team + ': ' + round_line[
                1] + '\n' + second_team + ': ' + round_line[3]

            raund_results = driver.find_elements_by_class_name('historyIcon')

            match_l = [] #информация о том как закончился раунд и отображение соответвующей иконки
            for i in raund_results[0:15]:
                j = str(i.find_element_by_tag_name('img').get_attribute('src'))
                if j == 'https://static.hltv.org/images/scoreboard2/emptyHistory.svg':
                    elem = 'ᅠ'
                elif j == 'https://static.hltv.org/images/scoreboard2/bomb_exploded.svg':
                    elem = '💣'
                elif j == 'https://static.hltv.org/images/scoreboard2/bomb_defused.svg':
                    elem = '✂'
                else:
                    elem = '💀'
                match_l.append(elem)

            for i in raund_results[30:45]:
                j = str(i.find_element_by_tag_name('img').get_attribute('src'))
                if j == 'https://static.hltv.org/images/scoreboard2/emptyHistory.svg':
                    elem = 'ᅠ'
                elif j == 'https://static.hltv.org/images/scoreboard2/bomb_exploded.svg':
                    elem = '💣'
                elif j == 'https://static.hltv.org/images/scoreboard2/bomb_defused.svg':
                    elem = '✂'
                else:
                    elem = '💀'
                match_l.append(elem)

            match_r = []

            for i in raund_results[15:30]:
                j = str(i.find_element_by_tag_name('img').get_attribute('src'))
                if j == 'https://static.hltv.org/images/scoreboard2/emptyHistory.svg':
                    elem = 'ᅠ'
                elif j == 'https://static.hltv.org/images/scoreboard2/bomb_exploded.svg':
                    elem = '💣'
                elif j == 'https://static.hltv.org/images/scoreboard2/bomb_defused.svg':
                    elem = '✂'
                else:
                    elem = '💀'
                match_r.append(elem)

            for i in raund_results[45:60]:
                j = str(i.find_element_by_tag_name('img').get_attribute('src'))
                if j == 'https://static.hltv.org/images/scoreboard2/emptyHistory.svg':
                    elem = 'ᅠ'
                elif j == 'https://static.hltv.org/images/scoreboard2/bomb_exploded.svg':
                    elem = '💣'
                elif j == 'https://static.hltv.org/images/scoreboard2/bomb_defused.svg':
                    elem = '✂'
                else:
                    elem = '💀'
                match_r.append(elem)

            line = ''
            for i, j in zip(match_l, match_r): #оформдение информации о том как закончился раунд и отображение соответвующей иконки в нужном месте
                line = line + '\n' + 'ᅠ' * (len(first_team) - 4) + i + 'ᅠ|ᅠ' + j

            second_line = 'ᅠ' + first_team + 'ᅠᅠ|ᅠᅠ' + second_team + line

            text = first_line + '\n\n' + second_line
            if text != prev_text:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                                      reply_markup=markup)
                prev_text = text

            while zz == "2":
                try:
                    time_three = datetime.datetime.now().timestamp()
                    if time_three - time_one > 1:
                        time_one = time_three
                        round_line = driver.find_element_by_class_name('topbarBg').text.split('\n')
                        teams = driver.find_element_by_class_name('content').find_elements_by_class_name('teamName')
                        first_team = teams[0].text
                        second_team = teams[1].text
                        is_bomb = driver.find_element_by_xpath(
                            '/html/body/div[3]/div/div[2]/div[1]/div[2]/div[6]/div/div[1]/div[2]/div/div[1]/div[3]/div[2]/img').get_attribute(
                            'src').split('/')[-1]
                        if is_bomb == 'bomb.png':
                            bomb = ' '
                        else:
                            bomb = ' бомба '

                        first_line = round_line[0] + bomb + round_line[4] + '\n' + first_team + ': ' + round_line[
                            1] + '\n' + second_team + ': ' + round_line[3]

                        raund_results = driver.find_elements_by_class_name('historyIcon')

                        time_four = datetime.datetime.now().timestamp()
                        if time_four - time_three > 20:
                            time_three = time_four
                            match_l = []
                            for i in raund_results[0:15]:
                                j = str(i.find_element_by_tag_name('img').get_attribute('src'))
                                if j == 'https://static.hltv.org/images/scoreboard2/emptyHistory.svg':
                                    elem = 'ᅠ'
                                elif j == 'https://static.hltv.org/images/scoreboard2/bomb_exploded.svg':
                                    elem = '💣'
                                elif j == 'https://static.hltv.org/images/scoreboard2/bomb_defused.svg':
                                    elem = '✂'
                                else:
                                    elem = '💀'
                                match_l.append(elem)

                            for i in raund_results[30:45]:
                                j = str(i.find_element_by_tag_name('img').get_attribute('src'))
                                if j == 'https://static.hltv.org/images/scoreboard2/emptyHistory.svg':
                                    elem = 'ᅠ'
                                elif j == 'https://static.hltv.org/images/scoreboard2/bomb_exploded.svg':
                                    elem = '💣'
                                elif j == 'https://static.hltv.org/images/scoreboard2/bomb_defused.svg':
                                    elem = '✂'
                                else:
                                    elem = '💀'
                                match_l.append(elem)

                            match_r = []

                            for i in raund_results[15:30]:
                                j = str(i.find_element_by_tag_name('img').get_attribute('src'))
                                if j == 'https://static.hltv.org/images/scoreboard2/emptyHistory.svg':
                                    elem = 'ᅠ'
                                elif j == 'https://static.hltv.org/images/scoreboard2/bomb_exploded.svg':
                                    elem = '💣'
                                elif j == 'https://static.hltv.org/images/scoreboard2/bomb_defused.svg':
                                    elem = '✂'
                                else:
                                    elem = '💀'
                                match_r.append(elem)

                            for i in raund_results[45:60]:
                                j = str(i.find_element_by_tag_name('img').get_attribute('src'))
                                if j == 'https://static.hltv.org/images/scoreboard2/emptyHistory.svg':
                                    elem = 'ᅠ'
                                elif j == 'https://static.hltv.org/images/scoreboard2/bomb_exploded.svg':
                                    elem = '💣'
                                elif j == 'https://static.hltv.org/images/scoreboard2/bomb_defused.svg':
                                    elem = '✂'
                                else:
                                    elem = '💀'
                                match_r.append(elem)

                        line = ''
                        for i, j in zip(match_l, match_r):
                            line = line + '\n' + 'ᅠ' * (len(first_team) - 4) + i + 'ᅠ|ᅠ' + j

                        second_line = 'ᅠ' + first_team + 'ᅠᅠ|ᅠᅠ' + second_team + line

                        text = first_line + '\n\n' + second_line
                        if text != prev_text:
                            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                  text=text, reply_markup=markup)
                            prev_text = text

                except:
                    break

        except:  #оформление раздела с информацией о матче в случае если произошла ошибка и бот не смог отобразить какуето информацию
            markup = types.InlineKeyboardMarkup(1)
            button1 = types.InlineKeyboardButton(text="Пики-баны", callback_data="1")
            button2 = types.InlineKeyboardButton(text="Информация о текущей карте", callback_data="2")
            button3 = types.InlineKeyboardButton(text="Статистика игроков", callback_data="3")
            button4 = types.InlineKeyboardButton(text="Письменная транслиция", callback_data="4")
            button5 = types.InlineKeyboardButton(text="Выйти", callback_data="5")
            markup.add(button1, button2, button3, button4, button5)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='Не получилось узнать информацию\n\nЧто хотите узнать', reply_markup=markup)

    elif zz[0] == "3":  #информация об игроках и их статистике,наличие брони,бомбы ,здоровья...,для первой команды
        prev_stat_text = ''
        try:

            if zz[1] == '1':

                teams = driver.find_element_by_class_name('content').find_elements_by_class_name('teamName')
                first_team = teams[0].text
                second_team = teams[1].text

                markup = types.InlineKeyboardMarkup(1)
                button3 = types.InlineKeyboardButton(text=second_team, callback_data="32")
                button4 = types.InlineKeyboardButton(text='Назад', callback_data="0")
                markup.add(button3, button4)

                round_line = driver.find_element_by_class_name('topbarBg').text.split('\n')
                is_bomb = driver.find_element_by_xpath(
                    '/html/body/div[3]/div/div[2]/div[1]/div[2]/div[6]/div/div[1]/div[2]/div/div[1]/div[3]/div[2]/img').get_attribute(
                    'src').split('/')[-1]
                if is_bomb == 'bomb.png':
                    bomb = ' '
                else:
                    bomb = ' бомба '

                first_line = round_line[0] + bomb + round_line[4] + '\n' + first_team + ': ' + round_line[
                    1] + '\n' + second_team + ': ' + round_line[3]

                stat_text = first_line + '\n\nScoreboard'
                i = driver.find_element_by_class_name('content').find_elements_by_class_name("team")[0]
                stat_text += '\n' + \
                             driver.find_element_by_class_name('content').find_elements_by_class_name('teamName')[
                                 driver.find_element_by_class_name('content').find_elements_by_class_name("team").index(
                                     i)].text + ':\nPlayer K A D ADR\nHP Armor Kits Weapon Money' + '\n'
                for j in i.find_elements_by_tag_name("tr"):
                    if i.find_elements_by_tag_name("tr").index(j) != 0:
                        info = j.text.replace('\n', ' ').split(' ')
                        stat_text += '\n' + info[0] + ' ' + info[3] + '/' + info[4] + '/' + info[5] + '/' + info[
                            6] + '\nHealth: ' + info[1] + '\n'
                        try:
                            j.find_elements_by_tag_name("td")[1].find_element_by_tag_name('img').get_attribute('src')
                            kits = 'kits'
                        except:
                            kits = '-'

                        try:
                            gun = str(
                                j.find_elements_by_tag_name("td")[2].find_element_by_tag_name('img').get_attribute(
                                    'src')).split('.png')[0].split('/')[-1]
                        except:
                            gun = '-'

                        try:
                            armor_png = str(
                                j.find_elements_by_tag_name("td")[4].find_element_by_tag_name('img').get_attribute(
                                    'src')).split('.png')[0].split('/')[-1]
                            if armor_png == 'kevlar_helmet':
                                armor = 'жилет + шлем'
                            if armor_png == 'kevlar':
                                armor = 'жилет'
                        except:
                            armor = '-'

                        stat_text += 'Броня: ' + armor + '\nДефуза: ' + kits + '\nОружие: ' + gun + '\nДеньги: ' + info[
                            2] + '\n'

                if stat_text != prev_stat_text:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text=stat_text, reply_markup=markup)
                    prev_stat_text = stat_text

                while zz[0] == '3' and zz[1] == '1':

                    teams = driver.find_element_by_class_name('content').find_elements_by_class_name('teamName')
                    first_team = teams[0].text
                    second_team = teams[1].text
                    raund = driver.find_element_by_xpath(
                        '/html/body/div[3]/div/div[2]/div[1]/div[1]/div[6]/div/div[1]/div[2]/div/div[1]/div[1]/span').text
                    ct_score = first_team + ' ' + driver.find_element_by_xpath(
                        '/html/body/div[3]/div/div[2]/div[1]/div[1]/div[6]/div/div[1]/div[2]/div/div[1]/div[2]/div[1]').text
                    t_score = driver.find_element_by_xpath(
                        '/html/body/div[3]/div/div[2]/div[1]/div[1]/div[6]/div/div[1]/div[2]/div/div[1]/div[2]/div[3]').text + ' ' + second_team
                    time = driver.find_element_by_xpath(
                        '/html/body/div[3]/div/div[2]/div[1]/div[1]/div[6]/div/div[1]/div[2]/div/div[1]/div[3]/div[1]/span').text
                    is_bomb = driver.find_element_by_xpath(
                        '/html/body/div[3]/div/div[2]/div[1]/div[1]/div[6]/div/div[1]/div[2]/div/div[1]/div[3]/div[2]/img').get_attribute(
                        'src').split('/')[-1]
                    if is_bomb == 'bomb.png':
                        bomb = ''
                    else:
                        bomb = 'бомба'
                    first_line = raund + ' ' + ct_score + ':' + t_score + ' ' + time + ' ' + bomb
                    stat_text = first_line + '\n\nScoreboard'
                    i = driver.find_element_by_class_name('content').find_elements_by_class_name("team")[0]
                    stat_text += '\n' + \
                                 driver.find_element_by_class_name('content').find_elements_by_class_name('teamName')[
                                     driver.find_element_by_class_name('content').find_elements_by_class_name(
                                         "team").index(
                                         i)].text + ':\nPlayer K A D ADR\nHP Armor Kits Weapon Money' + '\n'
                    for j in i.find_elements_by_tag_name("tr"):
                        if i.find_elements_by_tag_name("tr").index(j) != 0:
                            info = j.text.replace('\n', ' ').split(' ')
                            stat_text += '\n' + info[0] + ' ' + info[3] + '/' + info[4] + '/' + info[5] + '/' + info[
                                6] + '\nHealth: ' + info[1] + '\n'
                            try:
                                j.find_elements_by_tag_name("td")[1].find_element_by_tag_name('img').get_attribute(
                                    'src')
                                kits = 'kits'
                            except:
                                kits = '-'

                            try:
                                gun = str(
                                    j.find_elements_by_tag_name("td")[2].find_element_by_tag_name('img').get_attribute(
                                        'src')).split('.png')[0].split('/')[-1]
                            except:
                                gun = '-'

                            try:
                                armor_png = str(
                                    j.find_elements_by_tag_name("td")[4].find_element_by_tag_name('img').get_attribute(
                                        'src')).split('.png')[0].split('/')[-1]
                                if armor_png == 'kevlar_helmet':
                                    armor = 'жилет + шлем'
                                if armor_png == 'kevlar':
                                    armor = 'жилет'
                            except:
                                armor = '-'

                            stat_text += 'Броня: ' + armor + '\nДефуза: ' + kits + '\nОружие: ' + gun + '\nДеньги: ' + \
                                         info[2] + '\n'

                    if stat_text != prev_stat_text:
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text=stat_text, reply_markup=markup)
                        prev_stat_text = stat_text





            elif zz[1] == '2':#информация об игроках и их статистике,наличие брони,бомбы ,здоровья...,для второй команды

                teams = driver.find_element_by_class_name('content').find_elements_by_class_name('teamName')
                first_team = teams[0].text
                second_team = teams[1].text

                markup = types.InlineKeyboardMarkup(1)
                button2 = types.InlineKeyboardButton(text=first_team, callback_data="31")
                button4 = types.InlineKeyboardButton(text='Назад', callback_data="0")
                markup.add(button2, button4)

                round_line = driver.find_element_by_class_name('topbarBg').text.split('\n')
                is_bomb = driver.find_element_by_xpath(
                    '/html/body/div[3]/div/div[2]/div[1]/div[2]/div[6]/div/div[1]/div[2]/div/div[1]/div[3]/div[2]/img').get_attribute(
                    'src').split('/')[-1]
                if is_bomb == 'bomb.png':
                    bomb = ' '
                else:
                    bomb = ' бомба '

                first_line = round_line[0] + bomb + round_line[4] + '\n' + first_team + ': ' + round_line[
                    1] + '\n' + second_team + ': ' + round_line[3]

                stat_text = first_line + '\n\nScoreboard'
                i = driver.find_element_by_class_name('content').find_elements_by_class_name("team")[1]
                stat_text += '\n' + \
                             driver.find_element_by_class_name('content').find_elements_by_class_name('teamName')[
                                 driver.find_element_by_class_name('content').find_elements_by_class_name("team").index(
                                     i)].text + ':\nPlayer K A D ADR\nHP Armor Kits Weapon Money' + '\n'
                for j in i.find_elements_by_tag_name("tr"):
                    if i.find_elements_by_tag_name("tr").index(j) != 0:
                        info = j.text.replace('\n', ' ').split(' ')
                        stat_text += '\n' + info[0] + ' ' + info[3] + '/' + info[4] + '/' + info[5] + '/' + info[
                            6] + '\nHealth: ' + info[1] + '\n'
                        try:
                            j.find_elements_by_tag_name("td")[1].find_element_by_tag_name('img').get_attribute('src')
                            kits = 'kits'
                        except:
                            kits = '-'

                        try:
                            gun = str(
                                j.find_elements_by_tag_name("td")[2].find_element_by_tag_name('img').get_attribute(
                                    'src')).split('.png')[0].split('/')[-1]
                        except:
                            gun = '-'

                        try:
                            armor_png = str(
                                j.find_elements_by_tag_name("td")[4].find_element_by_tag_name('img').get_attribute(
                                    'src')).split('.png')[0].split('/')[-1]
                            if armor_png == 'kevlar_helmet':
                                armor = 'жилет + шлем'
                            if armor_png == 'kevlar':
                                armor = 'жилет'
                        except:
                            armor = '-'

                        stat_text += 'Броня: ' + armor + '\nДефуза: ' + kits + '\nОружие: ' + gun + '\nДеньги: ' + info[
                            2] + '\n'

                if stat_text != prev_stat_text:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text=stat_text, reply_markup=markup)
                    prev_stat_text = stat_text

                while zz[0] == '3' and zz[1] == '2':

                    round_line = driver.find_element_by_class_name('topbarBg').text.split('\n')
                    teams = driver.find_element_by_class_name('content').find_elements_by_class_name('teamName')
                    first_team = teams[0].text
                    second_team = teams[1].text
                    is_bomb = driver.find_element_by_xpath(
                        '/html/body/div[3]/div/div[2]/div[1]/div[2]/div[6]/div/div[1]/div[2]/div/div[1]/div[3]/div[2]/img').get_attribute(
                        'src').split('/')[-1]
                    if is_bomb == 'bomb.png':
                        bomb = ' '
                    else:
                        bomb = ' бомба '

                    first_line = round_line[0] + bomb + round_line[4] + '\n' + first_team + ': ' + round_line[
                        1] + '\n' + second_team + ': ' + round_line[3]

                    stat_text = first_line + '\n\nScoreboard'
                    i = driver.find_element_by_class_name('content').find_elements_by_class_name("team")[0]
                    stat_text += '\n' + \
                                 driver.find_element_by_class_name('content').find_elements_by_class_name('teamName')[
                                     driver.find_element_by_class_name('content').find_elements_by_class_name(
                                         "team").index(
                                         i)].text + ':\nPlayer K A D ADR\nHP Armor Kits Weapon Money' + '\n'
                    for j in i.find_elements_by_tag_name("tr"):
                        if i.find_elements_by_tag_name("tr").index(j) != 0:
                            info = j.text.replace('\n', ' ').split(' ')
                            stat_text += '\n' + info[0] + ' ' + info[3] + '/' + info[4] + '/' + info[5] + '/' + info[
                                6] + '\nHealth: ' + info[1] + '\n'
                            try:
                                j.find_elements_by_tag_name("td")[1].find_element_by_tag_name('img').get_attribute(
                                    'src')
                                kits = 'kits'
                            except:
                                kits = '-'
                            try:
                                gun = str(
                                    j.find_elements_by_tag_name("td")[2].find_element_by_tag_name('img').get_attribute(
                                        'src')).split('.png')[0].split('/')[-1]
                            except:
                                gun = '-'

                            try:
                                armor_png = str(
                                    j.find_elements_by_tag_name("td")[4].find_element_by_tag_name('img').get_attribute(
                                        'src')).split('.png')[0].split('/')[-1]
                                if armor_png == 'kevlar_helmet':
                                    armor = 'жилет + шлем'
                                if armor_png == 'kevlar':
                                    armor = 'жилет'
                            except:
                                armor = '-'

                            stat_text += 'Броня: ' + armor + '\nДефуза: ' + kits + '\nОружие: ' + gun + '\nДеньги: ' + \
                                         info[2] + '\n'

                    if stat_text != prev_stat_text:
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              text=stat_text, reply_markup=markup)
                        # bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id+3, text=stat_text)
                        prev_stat_text = stat_text

        except:
            teams = driver.find_element_by_class_name('content').find_elements_by_class_name('teamName')
            first_team = teams[0].text
            second_team = teams[1].text

            markup = types.InlineKeyboardMarkup(1)
            button2 = types.InlineKeyboardButton(text=first_team, callback_data="31")
            button3 = types.InlineKeyboardButton(text=second_team, callback_data="32")
            button4 = types.InlineKeyboardButton(text='Назад', callback_data="0")
            markup.add(button2, button3, button4)
            stat_text = 'Статистику игроков какой команды хотите увидеть'
            if stat_text != prev_stat_text:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=stat_text,
                                      reply_markup=markup)
                prev_stat_text = stat_text

    elif zz == "4": #раздел с письменной статистикой
        markup = types.InlineKeyboardMarkup(1)
        button1 = types.InlineKeyboardButton(text="Пики-баны", callback_data="1")
        button2 = types.InlineKeyboardButton(text="Информация о текущей карте", callback_data="2")
        button3 = types.InlineKeyboardButton(text="Статистика игроков", callback_data="3")
        button5 = types.InlineKeyboardButton(text="Выйти", callback_data="5")
        markup.add(button1, button2, button3, button5)
        log_prev = 'грузим...'
        main_line = '\n\n'
        old_event = '\n\n'
        while zz == '4':
            try:
                event = driver.find_element_by_class_name('list').find_elements_by_class_name('topPadding')[0].text
                if event != old_event:
                    old_event = event
                    if event == 'Round started':
                        main_line = ''
                        old_line = '\n\n'
                        first_ln = driver.find_element_by_class_name('list').find_elements_by_class_name('topPadding')[
                            3].text
                        second_ln = driver.find_element_by_class_name('list').find_elements_by_class_name('topPadding')[
                            2].text
                        if first_ln.split(' ')[1] == 'planted' or first_ln.split(' ')[1] == 'defused' or \
                                first_ln.split(' ', 1)[1] == 'joined the game' or first_ln.split(' ', 1)[
                            1] == 'quit the game' or first_ln.split(' ', 1)[1] == 'committed suicide':
                            old_line = first_ln + '\n' + old_line
                        elif first_ln.split(' ')[0] == 'Round':
                            old_line = first_ln + '\n' + old_line
                        else:
                            old_line = " ".join(first_ln.split(' ')[:-1]) + ' kill ' + " ".join(
                                first_ln.split(' ')[-1:]) + '\n' + old_line
                        if second_ln.split(' ')[1] == 'planted' or second_ln.split(' ')[1] == 'defused' or \
                                second_ln.split(' ', 1)[1] == 'joined the game' or second_ln.split(' ', 1)[
                            1] == 'quit the game' or second_ln.split(' ', 1)[1] == 'committed suicide':
                            old_line = second_ln + '\n' + old_line
                        elif second_ln.split(' ')[0] == 'Round':
                            old_line = second_ln + '\n' + old_line
                        else:
                            old_line = " ".join(second_ln.split(' ')[:-1]) + ' kill ' + " ".join(
                                second_ln.split(' ')[-1:]) + '\n' + old_line

                        main_line = event + '\n\n\n' + old_line
                    elif event.split(' ')[0] == 'Round':
                        main_line = ''
                        old_line = '\n\n'
                        first_ln = driver.find_element_by_class_name('list').find_elements_by_class_name('topPadding')[
                            2].text
                        second_ln = driver.find_element_by_class_name('list').find_elements_by_class_name('topPadding')[
                            1].text
                        if first_ln.split(' ')[1] == 'planted' or first_ln.split(' ')[1] == 'defused' or \
                                first_ln.split(' ', 1)[1] == 'joined the game' or first_ln.split(' ', 1)[
                            1] == 'quit the game' or first_ln.split(' ', 1)[1] == 'committed suicide':
                            old_line = first_ln + '\n' + old_line
                        else:
                            old_line = " ".join(first_ln.split(' ')[:-1]) + ' kill ' + " ".join(
                                first_ln.split(' ')[-1:]) + '\n' + old_line
                        if second_ln.split(' ')[1] == 'planted' or second_ln.split(' ')[1] == 'defused' or \
                                second_ln.split(' ', 1)[1] == 'joined the game' or second_ln.split(' ', 1)[
                            1] == 'quit the game' or second_ln.split(' ', 1)[1] == 'committed suicide':
                            old_line = second_ln + '\n' + old_line
                        else:
                            old_line = " ".join(second_ln.split(' ')[:-1]) + ' kill ' + " ".join(
                                second_ln.split(' ')[-1:]) + '\n' + old_line

                        main_line = event + '\n\n\n' + old_line
                    elif event.split(' ')[1] == 'planted' or event.split(' ')[1] == 'defused' or event.split(' ', 1)[
                        1] == 'joined the game' or event.split(' ', 1)[1] == 'quit the game' or event.split(' ', 1)[
                        1] == 'committed suicide':
                        main_line = event + '\n\n' + main_line
                    else:
                        main_line = " ".join(event.split(' ')[:-1]) + ' kill ' + " ".join(
                            event.split(' ')[-1:]) + '\n\n' + main_line

                if main_line != log_prev:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text=main_line, reply_markup=markup)
                    log_prev = main_line
            except:
                pass
    #отображение главного меню
    elif zz == "0":
        markup = types.InlineKeyboardMarkup(1)
        button1 = types.InlineKeyboardButton(text="Пики-баны", callback_data="1")
        button2 = types.InlineKeyboardButton(text="Информация о текущей карте", callback_data="2")
        button3 = types.InlineKeyboardButton(text="Статистика игроков", callback_data="3")
        button4 = types.InlineKeyboardButton(text="Письменная транслиция", callback_data="4")
        button5 = types.InlineKeyboardButton(text="Выйти", callback_data="5")
        markup.add(button1, button2, button3, button4, button5)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Что хотите узнать', reply_markup=markup)

    elif zz == "5": #кнопка выхода
        try:
            driver.quit()
        except:
            pass
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif zz == "89": #выбор даты для просмотра матчей

        h = 'https://www.hltv.org/matches'
        url = get_html(h)
        soup = BeautifulSoup(url, 'lxml')
        days = []
        for i in soup.find('div', class_='upcoming-matches').find_all('div', class_='match-day')[0:9]:
            days.append(i.find('span', class_='standard-headline').text)
        markup = types.InlineKeyboardMarkup(1)
        for i in days:
            if i.split(' ')[0] == datetime.date.today().strftime("%Y-%m-%d"):
                text = 'Сегодня'
            elif i.split(' ')[0] == (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"):
                text = 'Завтра'
            else:
                text = i
            button = types.InlineKeyboardButton(text=text, callback_data=i)
            markup.add(button)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Какая дата вас интересует', reply_markup=markup)


# In[ ]:


if __name__ == '__main__':
    bot.polling(none_stop=True)

# In[ ]:
