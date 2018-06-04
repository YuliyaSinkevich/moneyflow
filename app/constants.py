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


AVAILIBLE_CHART_COLORS = ['#000000', '#c0c0c0', '#808080', '#ffffff', '#800000', '#ff0000', '#800080', '#ff00ff',
                          '#008000', '#00ff00', '#808000', '#ffff00', '#000080', '#0000ff', '#008080', '#00ffff',
                          '#ffa500', '#f0f8ff', '#faebd7', '#7fffd4', '#f0ffff', '#f5f5dc', '#ffe4c4', '#ffebcd',
                          '#8a2be2', '#a52a2a', '#deb887', '#5f9ea0', '#7fff00', '#d2691e', '#ff7f50', '#6495ed',
                          '#fff8dc', '#dc143c', '#00ffff', '#00008b', '#008b8b', '#b8860b', '#a9a9a9', '#006400',
                          '#a9a9a9', '#bdb76b', '#8b008b', '#556b2f', '#ff8c00', '#9932cc', '#8b0000', '#e9967a',
                          '#8fbc8f', '#483d8b', '#2f4f4f', '#2f4f4f', '#00ced1', '#9400d3', '#ff1493', '#00bfff',
                          '#696969', '#696969', '#1e90ff', '#b22222', '#fffaf0', '#228b22', '#dcdcdc', '#f8f8ff',
                          '#ffd700', '#daa520', '#adff2f', '#808080', '#f0fff0', '#ff69b4', '#cd5c5c', '#4b0082',
                          '#fffff0', '#f0e68c', '#e6e6fa', '#fff0f5', '#7cfc00', '#fffacd', '#add8e6', '#f08080',
                          '#e0ffff', '#fafad2', '#d3d3d3', '#90ee90', '#d3d3d3', '#ffb6c1', '#ffa07a', '#20b2aa',
                          '#87cefa', '#778899', '#778899', '#b0c4de', '#ffffe0', '#32cd32', '#faf0e6', '#ff00ff',
                          '#66cdaa', '#0000cd', '#ba55d3', '#9370db', '#3cb371', '#7b68ee', '#00fa9a', '#48d1cc',
                          '#c71585', '#191970', '#f5fffa', '#ffe4e1', '#ffe4b5', '#ffdead', '#fdf5e6', '#6b8e23',
                          '#ff4500', '#da70d6', '#eee8aa', '#98fb98', '#afeeee', '#db7093', '#ffefd5', '#ffdab9',
                          '#cd853f', '#ffc0cb', '#dda0dd', '#b0e0e6', '#bc8f8f', '#4169e1', '#8b4513', '#fa8072',
                          '#f4a460', '#2e8b57', '#fff5ee', '#a0522d', '#87ceeb', '#6a5acd', '#708090', '#708090',
                          '#fffafa', '#00ff7f', '#4682b4', '#d2b48c', '#d8bfd8', '#ff6347', '#40e0d0', '#ee82ee',
                          '#f5deb3', '#f5f5f5', '#9acd32', '#663399']
