"""Обработка исключений бота-ассистента."""


class BotAssistantException(Exception):
    pass


class MissingEnvironmentVariables(BotAssistantException):
    def __init__(self, logging):
        msg = 'Отсутствуют необходимые переменные окружения!'
        super().__init__(msg)
        logging(msg)


class SendMessageToTelegramFailed(BotAssistantException):
    def __init__(self, logging, error):
        msg = f'Сбой при отправке сообщения в телеграм бот: {error}'
        super().__init__(msg)
        logging(msg)


class RequestToEndpointFailed(BotAssistantException):
    def __init__(self, logging, error):
        msg = f'Сбой при запросе к эндпойнту: {error}'
        super().__init__(msg)
        logging(msg)


class UncorrectTypeApiAnswer(BotAssistantException):
    def __init__(self, logging):
        msg = 'Некорректнй тип ответа API!'
        super().__init__(msg)
        logging(msg)


class HomeworksKeyNotValid(BotAssistantException):
    def __init__(self, logging):
        msg = 'Не найден ключ "homeworks" в ответе API!'
        super().__init__(msg)
        logging(msg)


class HomeworkTypeError(BotAssistantException):
    def __init__(self, logging, error):
        msg = f'Некорректный тип домашней работы в ответе API! {error}'
        super().__init__(msg)
        logging(msg)
