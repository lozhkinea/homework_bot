
# Описание:
# - раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет
#   статус отправленной на ревью домашней работы;
# - при обновлении статуса анализирует ответ API и отправляет
#   соответствующее уведомление в Telegram;
# - логирует свою работу и сообщает о важных проблемах в Telegram.
"""Бот-ассистент."""
import logging
import os
import time
from sys import stdout

import requests
from dotenv import load_dotenv
from telegram import Bot

import exceptions as _

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        raise _.SendMessageToTelegramFailed(logging.error, e) from e
    else:
        logging.info(f'{send_message.__doc__[:-1]}: "{message}"')


def get_api_answer(current_timestamp):
    """Возвращает ответ API по заданной метке current_timestamp."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code == requests.codes.not_found:
            raise _.UnavailableEndpoint(logging.error)
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            response.raise_for_status()
    except Exception as e:
        raise _.RequestToEndpointFailed(logging.error, e) from e


def check_response(response):
    """Возвращает список домашних работ, доступный в ответе API."""
    if not response or not len(response):
        raise UncorrectTypeApiAnswer
    if 'homeworks' not in response:
        logging.error('Отсутствие ожидаемых ключей в ответе API!')
        raise TypeError
    homeworks = response['homeworks']
    if type(homeworks) != list:
        raise UncorrectTypeApiAnswer
    return homeworks


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе её статус."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        raise _.UnexpectedHomeworkStatus(logging.error)
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения во время запуска бота."""
    return PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID

def init_bot():
    """Настройка бота."""
    global bot
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        level=logging.INFO,
        stream=stdout
    )
    if not check_tokens():
        raise _.MissingEnvironmentVariables(logging.critical)
    bot = Bot(token=TELEGRAM_TOKEN)
    logging.info('Запуск бота.')


def check_and_send(response):
    """Отправка сообщения о проверенной работе."""
    homeworks = check_response(response)
    if homeworks and len(homeworks):
        for homework in homeworks:
            message = parse_status(homework)
            send_message(bot, message)
        else:
            logging.debug('Отсутствие в ответе новых статусов.')


def main():
    """Основная логика работы бота."""
    global bot
    init_bot()
    current_timestamp = int(time.time())
    last_error = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            check_and_send(response)
            current_timestamp = response['current_date']
            time.sleep(RETRY_TIME)
        except Exception as error:
            if str(error) != last_error:
                last_error = str(error)
                message = f'Сбой в работе программы: {error}'
                send_message(bot, message)
            time.sleep(RETRY_TIME)
        else:
            pass


if __name__ == '__main__':
    main()
