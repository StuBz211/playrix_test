import argparse
import logging
import time
import sys

from github_client import GithubAPIClient
from utlis import parse_url


def init_logger():
    logging.basicConfig(
        filename='logs.log',
        level=logging.INFO,
        format='%(asctime)s : %(levelname)s : %(message)s'
    )


class StatisticInformation:
    def __init__(self, client):
        logging.info(f'initial {self.__class__.__name__}')
        self.github_client = client
        self._stats = {}

    def load_information(self):
        self._stats['authors'] = self.github_client.get_authors_commits(authors_count=30)
        self._stats['pull'] = self.github_client.get_pull_requests(days_limit=30)
        self._stats['issues'] = self.github_client.get_issues(days_limit=14)

    def output(self, out=sys.stdout):
        if not self._stats:
            logging.debug(f'empty stats, start = {self.load_information.__name__}')
            self.load_information()

        out.write(f'30 most actives users:\n')
        out.write(f'author_login\tcommits\n')
        for author, commit_count in self._stats['authors']:
            out.write(f'{author}:\t{commit_count}\n')

        out.write('\n')
        out.write('PULL REQUESTS:\n')
        out.write(f'open:\t{self._stats["pull"]["open"]}\n')
        out.write(f'closed:\t{self._stats["pull"]["closed"]}\n')
        out.write(f'old:\t{self._stats["pull"]["open"]}\n')
        out.write('\n')
        out.write('ISSUES\n')
        out.write(f'open:\t{self._stats["pull"]["open"]}\n')
        out.write(f'closed:\t{self._stats["pull"]["closed"]}\n')
        out.write(f'old:\t{self._stats["pull"]["open"]}\n')
        out.write('\n')

        logging.info(f'Done: {self.output.__name__}')


def main():
    start_time = time.perf_counter()

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='public github url', type=str)
    parser.add_argument('-df', '--date_from', help='date since scan', type=str)
    parser.add_argument('-dt', '--date_to', help='date until scan', type=str)
    parser.add_argument('-b', '--branch', help='selected branch', type=str, default='master')
    parser.add_argument('-t', '--token', help='api github token', type=str)

    args = parser.parse_args()
    init_logger()

    owner, repo = parse_url(args.url).values()

    github_client = GithubAPIClient(
        owner=owner, repository=repo,
        branch_name=args.branch, token=args.token,
        date_from=args.date_from, date_to=args.date_to
    )
    statistics = StatisticInformation(github_client)
    statistics.load_information()
    statistics.output(out=sys.stdout)

    logging.info(f'total work time {round(time.perf_counter() - start_time, 3)}sec')


if __name__ == '__main__':
    main()



