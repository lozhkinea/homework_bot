"""
Бот-ассистент.

Реализует:
    - раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет
    статус отправленной на ревью домашней работы;
    - при обновлении статуса анализирует ответ API и отправляет
    соответствующее уведомление в Telegram;
    - логирует свою работу и сообщает о важных проблемах в Telegram.
"""
import logging
import os
import time
from sys import stdout
from urllib.error import HTTPError

import requests
from dotenv import load_dotenv
from telegram import Bot

from exceptions import (ExpectedApiKeyMissed, MissingEnvironmentVariables,
                        RequestToEndpointFailed, SendMessageToTelegram,
                        UnavailableEndpoint, UncorrectTypeApiAnswer,
                        UnexpectedHomeworkStatus)

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
    """Отправка сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        logging.error('Сбой при отправке сообщения: '.upper() + e)
        raise SendMessageToTelegram() from e
    else:
        logging.info(f'{send_message.__doc__[:-1]}: "{message}"')


def get_api_answer(current_timestamp):
    """Возвращает ответ API по заданной метке current_timestamp."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
        if not response:
            raise RequestToEndpointFailed
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            response.raise_for_status()
    except HTTPError as he:
        raise UnavailableEndpoint from he
    except Exception as e:
        raise RequestToEndpointFailed from e


def check_response(response):
    """Возвращает список домашних работ, доступный в ответе API."""
    if not response or not len(response):
        raise UncorrectTypeApiAnswer
    if 'homeworks' not in response:
        raise TypeError
    homeworks = response['homeworks']
    if type(homeworks) != list:
        raise UncorrectTypeApiAnswer
    return homeworks


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе её статус."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except KeyError as ke:
        raise UnexpectedHomeworkStatus() from ke
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения во время запуска бота."""
    return PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID


def main():
    """Основная логика работы бота."""
    global bot
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        level=logging.INFO,
        stream=stdout
    )
    check_tokens()
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            hwlist = check_response(response)
            if hwlist:
                for hw in hwlist:
                    message = parse_status(hw)
                    send_message(bot, message)
                else:
                    raise MissingEnvironmentVariables()
                current_timestamp = response['current_date']
            time.sleep(RETRY_TIME)
        except MissingEnvironmentVariables:
            logging.critical('Отсутствуют обязательные переменные окружения!')
        except RequestToEndpointFailed:
            logging.error('Сбой при запросе к эндпойнту!')
        except UnavailableEndpoint:
            logging.error('Недоступен эндпойнт!')
        except ExpectedApiKeyMissed:
            logging.error('Отсутствуют ожидаемые ключи в ответе api!')
        except UnexpectedHomeworkStatus:
            logging.error('Недокументированный статус домашней работы,'
                          'обнаруженный в ответе API: ')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)
        else:
            pass


if __name__ == '__main__':
    main()
