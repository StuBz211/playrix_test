import json
import logging
from datetime import timedelta, datetime
from collections import Counter
from urllib.parse import urljoin, urlencode
from urllib.request import Request, urlopen


from utlis import str_to_datetime, prepare_date, log_decorator


class Response:
    """simple Response"""
    def __init__(self, response):
        self._resp = response
        self._page = response.read()
        self.encoding = 'utf-8'

    @property
    def page(self):
        return self._page.decode(self.encoding)

    def json(self, **kwargs):
        return json.loads(self.page, **kwargs)

    @property
    def status(self):
        return self._resp.status


class Client:
    """Simple HTTP client"""
    def __init__(self, token=None):
        self._token = token

        self._headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        }

        if not token:
            logging.warning(f'token is {token}, maybe request restrictions!')
        else:
            self._headers['Authorization'] = f'token {self._token}'

    @log_decorator
    def get(self, url, params=None):
        if params:
            if not isinstance(params, dict):
                raise ValueError(f"params may be {dict} no a {type(params)}")
            url = '?'.join([url, urlencode(params)])

        req = Request(url, headers=self._headers, method='GET')
        logging.info(f'try GET request by url:{url}')
        with urlopen(req) as resp:
            logging.info(f'status: {resp.status}')
            return Response(resp)


class GithubAPIClient:
    def __init__(self, owner, repository, branch_name='master', date_from=None, date_to=None, token=None):
        self._client = Client(token)

        self._owner = owner
        self._repository = repository
        self._date_from = prepare_date(date_from)
        self._date_to = prepare_date(date_to)

        self._per_page_load = 100
        self._branch_name = branch_name
        self.base_url = 'https://api.github.com/repos/{owner}/{repo}/'.format(owner=owner, repo=repository)

        logging.info(f'init {self.__class__.__name__}')
        logging.info(f'onwer: {owner}, repository: {repository}')
        logging.info(f'branch: {branch_name}')
        logging.info(f'date from: {date_from}, date to: {date_to}')
        if token:
            logging.info(f'token: {token[:6].ljust(len(token), "*")}')
        else:
            logging.info(f'token is None')

    def _get_params(self, page, **kwargs):
        params = {'page': page, 'per_page': self._per_page_load}

        if kwargs:
            params.update(kwargs)

        if self._date_from:
            params['since'] = self._date_from

        if self._date_to:
            params['until'] = self._date_to

        return params

    def _get_authors(self, authors_max_count=30):
        url = urljoin(self.base_url, 'contributors')
        send_count = 0
        page = 1
        while True:
            params = self._get_params(page, per_page=authors_max_count)
            page_authors = [i['login'] for i in self._client.get(url, params).json()]

            # yield authors and increment count, break after enough
            for author in page_authors:
                if send_count >= authors_max_count:
                    break
                send_count += 1
                yield author

            page += 1
            if len(page_authors) < self._per_page_load or send_count >= authors_max_count:
                break

    @log_decorator
    def get_authors_commits(self, authors_count):
        """
        collect authors commits count

        Returns:
            [(author_login: commit_count), ... ]
        """
        url = urljoin(self.base_url, 'commits')
        author_commits = Counter()
        for author in self._get_authors(authors_count):
            page = 1
            while True:
                params = self._get_params(page, author=author, sha=self._branch_name)
                page_commits = self._client.get(url, params).json()
                author_commits[author] += len(page_commits)
                page += 1

                if len(page_commits) < self._per_page_load:
                    break

        return author_commits.most_common(authors_count)

    def _collect_stats(self, url_part, days_limit):
        url = urljoin(self.base_url, url_part)
        page = 1
        state = {
            'closed': 0,
            'open': 0,
            'old': 0
        }

        while True:
            page_result = self._client.get(url, self._get_params(page, state='all')).json()
            page += 1
            for res in page_result:
                state[res['state']] += 1

                if (
                    datetime.today() - str_to_datetime(res['created_at'])> timedelta(days=days_limit)
                ):
                    state['old'] += 1

            if len(page_result) < self._per_page_load:
                break

        return state

    @log_decorator
    def get_pull_requests(self, days_limit):
        """
        Collect pull requests state counts

        Returns: {open: int, closed: int, old: int}
        """
        return self._collect_stats('pulls', days_limit)

    @log_decorator
    def get_issues(self, days_limit):
        """
        Collect issues states count (open, close, old).

        Returns: {open: int, closed: int, old: int}
        """

        return self._collect_stats('issues', days_limit)
