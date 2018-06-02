REVENUES_CATEGORIES = ['salary', 'other']
EXPENSES_CATEGORIES = ['food', 'sport', 'other']

DEFAULT_CURRENCY = 'USD'
AVAILABLE_CURRENCIES = ['EUR', 'AUD', 'BGN', 'BRL', 'CAD', 'CHF', 'CNY', 'CZK', 'DKK', 'GBP', 'HKD', 'HRK', 'HUF',
                        'IDR', 'ILS', 'INR', 'ISK', 'JPY', 'KRW', 'MXN', 'MYR', 'NOK', 'NZD', 'PHP', 'PLN', 'RON',
                        'RUB', 'SEK', 'SGD', 'THB', 'TRY', DEFAULT_CURRENCY, 'ZAR']


class Language(object):
    def __init__(self, language: str, locale: str):
        self.language_ = language
        self.locale_ = locale

    def language(self):
        return self.language_

    def locale(self):
        return self.locale_


DEFAULT_LANGUAGE = Language('english', 'en')
AVAILABLE_LANGUAGES = [DEFAULT_LANGUAGE, Language('russian', 'ru')]


def get_language_by_name(language) -> Language:
    return next((x for x in AVAILABLE_LANGUAGES if x.language() == language), None)


AVAILIBLE_CHART_COLORS = ['rgba(255, 99, 132, 0.5)', 'rgba(255, 159, 64, 0.5)', 'rgba(255, 205, 86, 0.5)',
                          'rgba(75, 192, 192, 0.5)', 'rgba(54, 162, 235, 0.5)',
                          'rgba(153, 102, 255, 0.5)', 'rgba(201, 203, 207, 0.5)']
