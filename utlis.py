import re
import time
import logging
from datetime import datetime


_github_url_pattern = re.compile(r'http(s)?://github\.com/(?P<name>[a-zA-Z-_\d]+)/(?P<repo>[a-zA-z-_\d]+)')


def parse_url(raw_url):
    expr = _github_url_pattern.search(raw_url)
    if expr:
        return expr.groupdict()
    raise ValueError('Url parse failed')


def prepare_date(date_str):
    try:
        return date_to_str(str_to_datetime(date_str))
    except (ValueError, TypeError):
        logging.warning(f'cant convert "{date_str}" to datetime')


def date_to_str(date_time):
    return datetime.strftime(date_time, '%Y-%m-%dT%H:%M:%SZ')


def str_to_datetime(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        return datetime.strptime(date_str, '%Y-%m-%d')


def log_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        logging.info(f'call {func.__name__}')
        res = func(*args, **kwargs)
        logging.info(f'executed in {time.perf_counter() - start_time} sec')
        return res

    return wrapper
