# HLTVBot

# Зміст

1. [Вступ](#introduction)
2. [Технічне завдання](#techtask)
3. [Використання](#howto)
4. [Висновки](#conclusion)


##  1. Вступ <a name="introduction"></a>
### 1.1 Ціль проекту

Телеграм-бот для спрощення процесу пошуку інформації про матчі CS.

### 1.2 Реалізація

1. Інтерфейс та функціонал боту (python3):
* [telebot](https://pypi.org/project/telebot/)

2. Парсинг інформації (python3):
*  [Selenium](https://selenium-python.readthedocs.io/)

## 2. Технічне завдання <a name="techtask"></a>

### 2.1 Загальне завдання

Розробити сервіс для відстежування статистики та матчів гри Counter-Strike GO, джерелом інформації виступає https://www.hltv.org/. 

### 2.2 Функціональність
 
 Бот має 4 основні функції:
 1. /live_matches 
 Відображення поточних матчів. Порівнявши зі списком з сайту, бачимо що інформація відображається коректно.
 
 ![Альтернативный текст](https://github.com/CLII412/ipz2/blob/master/screenshots/live_command.jpg?raw=true)
 ![Альтернативный текст](https://github.com/CLII412/ipz2/blob/master/screenshots/live_page.jpg?raw=true)
 
 2. /future_matches 
 Список матчів по дням, по київському часу.
 
 ![Альтернативный текст](https://github.com/CLII412/ipz2/blob/master/screenshots/future.jpg?raw=true)
 ![Альтернативный текст](https://github.com/CLII412/ipz2/blob/master/screenshots/future_page.jpg?raw=true)
 
 3. /my_fauvorite_teams 
 
 Команда для роботи з улюбленими командами.
 
 4. /append_my_fauvorite_teams  
 
 ![Альтернативный текст](https://github.com/CLII412/ipz2/blob/master/screenshots/append_command.jpg?raw=true)
 
 Після додавання команди до списку улюблених будуть приходити сповіщення про їхні матчі.

## 3. Розробка  <a name="development"></a>
Отримали новий токен в Father Bot в Телеграм.
Встановили pyTelegramBotAPI.
Підключили бібліотек


## 5. Висновки  <a name="conclusion"></a> 

За допомогою цього проекту покращили навички програмування на python3, а також набули досвіду роботи з такими бібліотеками як Selenium, requests, bs4.

