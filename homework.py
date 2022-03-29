# Описание:
# - раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет
#   статус отправленной на ревью домашней работы;
# - при обновлении статуса анализирует ответ API и отправляет
#   соответствующее уведомление в Telegram;
# - логирует свою работу и сообщает о важных проблемах в Telegram.
"""Бот-ассистент."""
import logging
import os
import sys
import time

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


def send_message(bot: Bot, message: str) -> None:
    """
    Отправляет сообщение в Telegram чат, определяемый
    переменной окруженияTELEGRAM_CHAT_ID.
    """
    try:
        bot.send_message(TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        raise _.SendMessageToTelegramFailed(logging.exception, e) from e
    else:
        logging.info(f'Отправлено в Telegram: {message}')


def get_api_answer(current_timestamp: int) -> dict:
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code == requests.codes.not_found:
            raise _.RequestToEndpointFailed(logging.exception,
                                            'Недоступен эндпойнт')
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            response.raise_for_status()
    except Exception as e:
        raise _.RequestToEndpointFailed(logging.exception, e) from e


def check_response(response: dict) -> list:
    """
    Проверяет ответ API на корректность. Если ответ API соответствует
    ожиданиям, то функция должна вернуть список домашних работ (он может
    быть и пустым), доступный в ответе API по ключу 'homeworks'.
    """
    logging.debug(f'Ответ API: {response}')
    if not response or not len(response):
        raise _.UncorrectTypeApiAnswer(logging.exception)
    if 'homeworks' not in response:
        logging.exception('Отсутствуют ожидаемые ключи в ответе API!'
                          'Ожидается "homeworks".')
        raise TypeError
    homeworks = response['homeworks']
    if type(homeworks) != list:
        raise _.HomeworksKeyNotValid(logging.exception)
    logging.debug(f'Список домашних работ: {homeworks}')
    return homeworks


def parse_status(homework: dict) -> str:
    """Извлекает из информации о конкретной домашней работе её статус."""
    logging.debug(f'Домашняя работа: {homework}')
    if type(homework) != dict:
        raise _.HomeworkTypeError(logging.exception, 'Ожидается словарь.')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        raise _.HomeworkTypeError(logging.exception,
                                  'Недокументированный статус домашней работы')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """
    Ппроверяет доступность переменных окружения,
    которые необходимы для работы программы.
    """
    return PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID


def init_bot(level: int) -> None:
    """Настройка бота."""
    global bot
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        level=level,
        stream=sys.stdout
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
            logging.debug('Отсутствуют новые статусы.')


def main():
    """Основная логика работы бота."""
    global bot
    init_bot(logging.INFO)
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
