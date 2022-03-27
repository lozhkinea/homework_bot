"""Обработка исключений бота-ассистента."""


class BotAssistantException(Exception):
    pass


class MissingEnvironmentVariables(BotAssistantException):
    def __init__(self):
        super().__init__('Отсутствуют необходимые переменные окружения!')


class SendMessageToTelegram(BotAssistantException):
    def __init__(self):
        super().__init__('Сбой при отправке сообщения в тедлеграм бот!')


class RequestToEndpointFailed(BotAssistantException):
    def __init__(self):
        super().__init__('Сбой при запросе к эндпойнту!')


class UnavailableEndpoint(BotAssistantException):
    def __init__(self):
        super().__init__('Недоступен эндпойнт!')


class ExpectedApiKeyMissed(BotAssistantException):
    def __init__(self):
        super().__init__('Отсутствуют ожидаемые ключи в ответе API')


class UncorrectTypeApiAnswer(BotAssistantException):
    def __init__(self):
        super().__init__('Некорректнй тип ответа API')


class UnexpectedHomeworkStatus(BotAssistantException):
    def __init__(self):
        super().__init__('Недокументированный статус домашней работы,'
                         'обнаруженный в ответе API')
