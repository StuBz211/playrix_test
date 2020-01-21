import unittest   # cant use pytests module, then use unittest
import unittest.mock
import datetime
import urllib.error

import utlis
from github_client import Client
from github_client import GithubAPIClient

from playrix import StatisticInformation


class TestClient(unittest.TestCase):
    def test_client_has_methods(self):
        self.assertTrue(hasattr(Client, 'get'), ' has no method "get"')

    def test_normal_requests(self):
        client = Client()
        res = client.get('http://python.org/')

        self.assertTrue(hasattr(res, 'json'), ' has no method "json"')
        self.assertTrue(hasattr(res, 'status'), ' has no method "status"')
        self.assertTrue(hasattr(res, 'page'), ' has no attribute "page"')

        self.assertEqual(res.status, 200, 'OK')

        self.assertIn('html', res.page)
        self.assertIn('Python', res.page)
        self.assertNotIn('Barbara', res.page)

    def test_fail_requests(self):
        client = Client()
        # incorect url
        self.assertRaises(urllib.error.URLError, client.get, 'http://dpython.org/')

        # empty url
        self.assertRaises(ValueError, client.get, '')
        # params not dict
        self.assertRaises(ValueError, client.get, '', True)
        # params not dict
        self.assertRaises(ValueError, client.get, '', '{page:1}')


class TestGitHubClient(unittest.TestCase):

    def test_methods(self):
        self.assertTrue(hasattr(GithubAPIClient, 'get_authors_commits'))
        self.assertTrue(hasattr(GithubAPIClient, 'get_pull_requests'))
        self.assertTrue(hasattr(GithubAPIClient, 'get_issues'))

    def test_author_commits(self):
        ghc = GithubAPIClient('StuBz211', 'ticker_app')

        author, commit_count = ghc.get_authors_commits(5)[0]
        self.assertEqual(author, 'StuBz211')
        self.assertEqual(commit_count, 3)

    def test_pull_requests(self):
        ghc = GithubAPIClient('StuBz211', 'ticker_app')

        stats = ghc.get_pull_requests(30)
        self.assertEqual(stats['open'], 1)
        self.assertEqual(stats['closed'], 0)
        self.assertEqual(stats['old'], 1)

    def test_issues(self):
        ghc = GithubAPIClient('StuBz211', 'ticker_app')

        stats = ghc.get_issues(14)
        self.assertEqual(stats['open'], 1)
        self.assertEqual(stats['closed'], 0)
        self.assertEqual(stats['old'], 1)


class TestStaticInformation(unittest.TestCase):
    def mock_github_client(self):
        cl = GithubAPIClient(None, None)
        cl.get_authors_commits = unittest.mock.MagicMock()
        cl.get_authors_commits.return_value = [("1", 56), ('2', 23), ('3', 5)]
        cl.get_pull_requests = unittest.mock.MagicMock()
        cl.get_pull_requests.return_value = {'open': 3, 'closed': 5, 'old': 2}
        cl.get_issues = unittest.mock.MagicMock()
        cl.get_issues.return_value = {'open': 6, 'closed': 9, 'old': 1}
        return cl

    def test_methods(self):
        self.assertTrue(hasattr(StatisticInformation, 'load_information'))
        self.assertTrue(hasattr(StatisticInformation, 'output'))

    def test_load(self):
        github_client = self.mock_github_client()

        si = StatisticInformation(github_client)
        si.load_information()

        stats = si._stats

        authors_list = stats['authors']
        self.assertEqual(authors_list[0][0], '1')
        self.assertEqual(authors_list[0][1], 56)
        self.assertEqual(authors_list[1][0], '2')
        self.assertEqual(authors_list[1][1], 23)
        self.assertEqual(authors_list[2][0], '3')
        self.assertEqual(authors_list[2][1], 5)

        pulls = stats['pull']
        self.assertEqual(pulls['open'], 3)
        self.assertEqual(pulls['closed'], 5)
        self.assertEqual(pulls['old'], 2)

        issues = stats['issues']
        self.assertEqual(issues['open'], 6)
        self.assertEqual(issues['closed'], 9)
        self.assertEqual(issues['old'], 1)

    def test_output(self):
        github_client = self.mock_github_client()
        si = StatisticInformation(github_client)
        si.output()

        self.assertTrue(hasattr(si, '_stats'))
        self.assertNotEqual(si._stats, {})


class TestUtils(unittest.TestCase):
    def test_parse_public_url(self):
        res = utlis.parse_url('https://github.com/StuBz211/ticker_app')
        self.assertEqual(type(res), dict)
        self.assertEqual(res['name'], 'StuBz211')
        self.assertEqual(res['repo'], 'ticker_app')

        res = utlis.parse_url('https://github.com/sbt/tr-kd/test_project')
        self.assertEqual(res['name'], 'sbt')
        self.assertEqual(res['repo'], 'tr-kd')

    def test_str2date(self):
        d1 = utlis.str_to_datetime('2019-04-16')
        self.assertEqual(d1, datetime.datetime(2019,4, 16))
        d2 = utlis.str_to_datetime('2019-04-16T23:32:52Z')
        self.assertEqual(d2, datetime.datetime(2019, 4, 16, 23, 32, 52))
        # broken date
        self.assertRaises(ValueError, utlis.str_to_datetime, '2019-16-4')
        # empty date
        self.assertRaises(ValueError, utlis.str_to_datetime, '')

    def test_date2str(self):
        d1 = utlis.date_to_str(datetime.datetime(2020, 1, 15))
        self.assertEqual(d1, '2020-01-15T00:00:00Z')

        d2 = utlis.date_to_str(datetime.datetime(2020, 1, 15, 16, 25, 48))
        self.assertEqual(d2, '2020-01-15T16:25:48Z')

    def test_prepare_date(self):
        d1 = utlis.prepare_date('2019-04-16')
        self.assertEqual(d1, '2019-04-16T00:00:00Z')
        d2 = utlis.prepare_date('2019-04-16T23:32:52Z')
        self.assertEqual(d2, '2019-04-16T23:32:52Z')

        # fail str time
        d3 = utlis.prepare_date('2020-01-15T64:456:43')
        self.assertEqual(d3, None)
        d4 = utlis.prepare_date('')
        self.assertEqual(d3, None)


if __name__ == '__main__':
    unittest.main()

