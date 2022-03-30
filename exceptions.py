"""Обработка исключений бота-ассистента."""


class BotAssistantException(Exception):
    pass


class MissingEnvironmentVariables(BotAssistantException):
    def __init__(self, logging):
        msg = 'Отсутствуют необходимые переменные окружения!'
        super().__init__(msg)
        logging(msg)


class RequestToEndpointFailed(BotAssistantException):
    def __init__(self, error):
        super().__init__(f'Сбой при запросе к эндпойнту: {error}')


class ApiAnswerTypeError(BotAssistantException):
    def __init__(self, error):
        super().__init__('Некорректнй тип ответа API! {error}')


class HomeworkTypeError(BotAssistantException):
    def __init__(self, error):
        super().__init__(f'Некорректный тип домашки в ответе API! {error}')
