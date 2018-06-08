INCOMES_CATEGORIES = ['Award', 'Gifts', 'Interest Money', 'Others', 'Salary', 'Selling']
EXPENSES_CATEGORIES = [
    'Bills & Utilities', 'Education', 'Entertainment', 'Family', 'Fees & Charges', 'Food & Beverage', 'Friends & Lover',
    'Gifts & Donations', 'Health & Fitness', 'Insurances', 'Investment', 'Others', 'Shopping', 'Transportation',
    'Travel']

DEFAULT_CURRENCY = 'USD'
AVAILABLE_CURRENCIES = {
    "AED": "United Arab Emirates Dirham",
    "AFN": "Afghan Afghani",
    "ALL": "Albanian Lek",
    "AMD": "Armenian Dram",
    # "ANG": "Netherlands Antillean Guilder",
    "AOA": "Angolan Kwanza",
    "ARS": "Argentine Peso",
    "AUD": "Australian Dollar",
    "AWG": "Aruban Florin",
    "AZN": "Azerbaijani Manat",
    "BAM": "Bosnia-Herzegovina Convertible Mark",
    "BBD": "Barbadian Dollar",
    "BDT": "Bangladeshi Taka",
    "BGN": "Bulgarian Lev",
    "BHD": "Bahraini Dinar",
    "BIF": "Burundian Franc",
    "BMD": "Bermudan Dollar",
    "BND": "Brunei Dollar",
    "BOB": "Bolivian Boliviano",
    "BRL": "Brazilian Real",
    "BSD": "Bahamian Dollar",
    # "BTC": "Bitcoin",
    "BTN": "Bhutanese Ngultrum",
    "BWP": "Botswanan Pula",
    "BYN": "Belarusian Ruble",
    "BZD": "Belize Dollar",
    "CAD": "Canadian Dollar",
    "CDF": "Congolese Franc",
    "CHF": "Swiss Franc",
    "CLF": "Chilean Unit of Account (UF)",
    "CLP": "Chilean Peso",
    # "CNH": "Chinese Yuan (Offshore)",
    "CNY": "Chinese Yuan",
    "COP": "Colombian Peso",
    "CRC": "Costa Rican Colón",
    # "CUC": "Cuban Convertible Peso",
    "CUP": "Cuban Peso",
    "CVE": "Cape Verdean Escudo",
    "CZK": "Czech Republic Koruna",
    "DJF": "Djiboutian Franc",
    "DKK": "Danish Krone",
    "DOP": "Dominican Peso",
    "DZD": "Algerian Dinar",
    "EGP": "Egyptian Pound",
    "ERN": "Eritrean Nakfa",
    "ETB": "Ethiopian Birr",
    "EUR": "Euro",
    "FJD": "Fijian Dollar",
    "FKP": "Falkland Islands Pound",
    "GBP": "British Pound Sterling",
    "GEL": "Georgian Lari",
    # "GGP": "Guernsey Pound",
    "GHS": "Ghanaian Cedi",
    # "GIP": "Gibraltar Pound",
    "GMD": "Gambian Dalasi",
    "GNF": "Guinean Franc",
    "GTQ": "Guatemalan Quetzal",
    "GYD": "Guyanaese Dollar",
    "HKD": "Hong Kong Dollar",
    "HNL": "Honduran Lempira",
    "HRK": "Croatian Kuna",
    "HTG": "Haitian Gourde",
    "HUF": "Hungarian Forint",
    "IDR": "Indonesian Rupiah",
    "ILS": "Israeli New Sheqel",
    "IMP": "Manx pound",
    "INR": "Indian Rupee",
    "IQD": "Iraqi Dinar",
    "IRR": "Iranian Rial",
    "ISK": "Icelandic Króna",
    "JEP": "Jersey Pound",
    "JMD": "Jamaican Dollar",
    "JOD": "Jordanian Dinar",
    "JPY": "Japanese Yen",
    "KES": "Kenyan Shilling",
    "KGS": "Kyrgystani Som",
    "KHR": "Cambodian Riel",
    "KMF": "Comorian Franc",
    "KPW": "North Korean Won",
    "KRW": "South Korean Won",
    "KWD": "Kuwaiti Dinar",
    "KYD": "Cayman Islands Dollar",
    "KZT": "Kazakhstani Tenge",
    "LAK": "Laotian Kip",
    "LBP": "Lebanese Pound",
    "LKR": "Sri Lankan Rupee",
    "LRD": "Liberian Dollar",
    "LSL": "Lesotho Loti",
    "LYD": "Libyan Dinar",
    "MAD": "Moroccan Dirham",
    "MDL": "Moldovan Leu",
    "MGA": "Malagasy Ariary",
    "MKD": "Macedonian Denar",
    "MMK": "Myanma Kyat",
    "MNT": "Mongolian Tugrik",
    "MOP": "Macanese Pataca",
    "MRO": "Mauritanian Ouguiya (pre-2018)",
    # "MRU": "Mauritanian Ouguiya",
    "MUR": "Mauritian Rupee",
    "MVR": "Maldivian Rufiyaa",
    "MWK": "Malawian Kwacha",
    "MXN": "Mexican Peso",
    "MYR": "Malaysian Ringgit",
    "MZN": "Mozambican Metical",
    "NAD": "Namibian Dollar",
    "NGN": "Nigerian Naira",
    "NIO": "Nicaraguan Córdoba",
    "NOK": "Norwegian Krone",
    "NPR": "Nepalese Rupee",
    "NZD": "New Zealand Dollar",
    "OMR": "Omani Rial",
    "PAB": "Panamanian Balboa",
    "PEN": "Peruvian Nuevo Sol",
    "PGK": "Papua New Guinean Kina",
    "PHP": "Philippine Peso",
    "PKR": "Pakistani Rupee",
    "PLN": "Polish Zloty",
    "PYG": "Paraguayan Guarani",
    "QAR": "Qatari Rial",
    "RON": "Romanian Leu",
    "RSD": "Serbian Dinar",
    "RUB": "Russian Ruble",
    "RWF": "Rwandan Franc",
    "SAR": "Saudi Riyal",
    "SBD": "Solomon Islands Dollar",
    "SCR": "Seychellois Rupee",
    "SDG": "Sudanese Pound",
    "SEK": "Swedish Krona",
    "SGD": "Singapore Dollar",
    "SHP": "Saint Helena Pound",
    "SLL": "Sierra Leonean Leone",
    "SOS": "Somali Shilling",
    "SRD": "Surinamese Dollar",
    "SSP": "South Sudanese Pound",
    "STD": "São Tomé and Príncipe Dobra (pre-2018)",
    # "STN": "São Tomé and Príncipe Dobra",
    "SVC": "Salvadoran Colón",
    "SYP": "Syrian Pound",
    "SZL": "Swazi Lilangeni",
    "THB": "Thai Baht",
    "TJS": "Tajikistani Somoni",
    "TMT": "Turkmenistani Manat",
    "TND": "Tunisian Dinar",
    "TOP": "Tongan Pa'anga",
    "TRY": "Turkish Lira",
    "TTD": "Trinidad and Tobago Dollar",
    "TWD": "New Taiwan Dollar",
    "TZS": "Tanzanian Shilling",
    "UAH": "Ukrainian Hryvnia",
    "UGX": "Ugandan Shilling",
    DEFAULT_CURRENCY: "United States Dollar",
    "UYU": "Uruguayan Peso",
    "UZS": "Uzbekistan Som",
    "VEF": "Venezuelan Bolívar Fuerte",
    "VND": "Vietnamese Dong",
    "VUV": "Vanuatu Vatu",
    "WST": "Samoan Tala",
    "XAF": "CFA Franc BEAC",
    # "XAG": "Silver Ounce",
    # "XAU": "Gold Ounce",
    "XCD": "East Caribbean Dollar",
    # "XDR": "Special Drawing Rights",
    "XOF": "CFA Franc BCEAO",
    # "XPD": "Palladium Ounce",
    "XPF": "CFP Franc",
    # "XPT": "Platinum Ounce",
    "YER": "Yemeni Rial",
    "ZAR": "South African Rand",
    "ZMW": "Zambian Kwacha",
    "ZWL": "Zimbabwean Dollar"
}

DATE_JS_FORMAT = '%m/%d/%Y %H:%M:%S'


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
