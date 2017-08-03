from ..abc import PaymentService


class Sberbank(PaymentService):
    """
    Класс для работы с API Сбербанка.
    """
    slug = 'sberbank'

    def __init__(self, init):
        super().__init__()

        # Параметры подключения
        self.__user = init['user']
        self.__mode = init['mode']  # ('test', 'prod',)

        self.__host = init[self.__mode]['host']
        self.__pswd = init[self.__mode]['pswd']
        self.__success_url = init[self.__mode]['success_url']
        self.__error_url = init[self.__mode]['error_url']

        # Дополнительные параметры
        # commission_included
        self.commission = init['commission']
        self.timeout = init['timeout']
        # description

    def __str__(self):
        return '{cls}({user}: {mode})'.format(
            cls=self.__class__.__name__,
            user=self.__user,
            mode=self.__mode,
        )
