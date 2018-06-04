import requests
import lmdb
import json
from datetime import datetime


class OpenExchangeRatesClient(object):
    """This class is a client implementation for openexchangerate.org service
    with caching.

    """
    BASE_URL = 'https://openexchangerates.org/api'
    ENDPOINT_LATEST = BASE_URL + '/latest.json'
    ENDPOINT_HISTORICAL_TEMPLATE_1DATE = BASE_URL + '/historical/{0}.json'
    DB_NAME = 'exchange'.encode()
    DATE_FORMAT = '%Y-%m-%d'

    def __init__(self, db_path: str, api_key: str):
        env = lmdb.open(db_path, max_dbs=10)
        db = env.open_db(self.DB_NAME)

        self.db_env_ = env
        self.db_ = db
        self.client_ = requests.Session()
        self.client_.params.update({'app_id': api_key})

    def get_rates(self, base: str, date=datetime.today().now()):
        date_str = date.strftime(self.DATE_FORMAT)
        key_str = '{0}:{1}'.format(date_str, base)
        rate_db = self.__get_key(key_str.encode())
        if rate_db:
            rt = rate_db.decode()
            js = json.loads(rt)
            return js['rates']

        resp = self.client_.get(self.ENDPOINT_HISTORICAL_TEMPLATE_1DATE.format(date_str), params={'base': base})
        http_error_msg = ''
        if isinstance(resp.reason, bytes):
            reason = resp.reason.decode('utf-8', 'ignore')
        else:
            reason = resp.reason

        if 400 <= resp.status_code < 500:
            http_error_msg = u'%s Client Error: %s for url: %s' % (resp.status_code, reason, resp.url)
        elif 500 <= resp.status_code < 600:
            http_error_msg = u'%s Server Error: %s for url: %s' % (resp.status_code, reason, resp.url)

        if http_error_msg:
            return None

        resp_json = resp.json(parse_int=float,
                              parse_float=float)

        rate_str = json.dumps(resp_json).encode()
        self.__set_key(key_str.encode(), rate_str)
        return resp_json['rates']

    def __get_key(self, key: bytes):
        with self.db_env_.begin() as txn:
            return txn.get(key, db=self.db_)

    def __set_key(self, key: bytes, value: bytes) -> bool:
        with self.db_env_.begin(write=True) as txn:
            return txn.put(key, value, db=self.db_)
