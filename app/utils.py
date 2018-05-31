from validate_email import validate_email
from urllib.request import urlopen
import json


def is_valid_email(email: str, check_mx: bool) -> bool:
    dns_valid = validate_email(email, check_mx=check_mx)
    if not dns_valid:
        return False

    validate_url = 'https://open.kickbox.com/v1/disposable/{0}' + email
    response = urlopen(validate_url)
    if response.status != 200:
        return False

    data = response.read()
    json_object = json.loads(data.decode("utf-8"))
    is_disposable = json_object['disposable']
    return not is_disposable
