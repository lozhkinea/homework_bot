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


class UnavailableEndpoint(BotAssistantException):
    def __init__(self, logging):
        msg = 'Недоступен эндпойнт!'
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


class UnexpectedHomeworkStatus(BotAssistantException):
    def __init__(self, logging):
        msg = 'Недокументированный статус домашней работы в ответе API!'
        super().__init__(msg)
        logging(msg)
