""" DevHints Module """

import json
import os
import time

import requests

CACHE_TTL = 3600


class DevHints():
    """ Handles DevHints logic """

    def __init__(self, url, logger, cache_dir):
        """ Constructor """
        self.url = url
        self.logger = logger
        self.cache_dir = cache_dir

    def get_cache_file_path(self):
        """ Returns the cache file path """
        return os.path.join(self.cache_dir, 'devhints_cache.json')

    def clear_cache(self):
        """ Deletes the cache file """
        if os.path.exists(self.get_cache_file_path()):
            os.unlink(self.get_cache_file_path())

    def set_url(self, url):
        """ Sets the DevHints base url """
        self.url = url
        self.clear_cache()

    def filter_results(self, results, query):
        """ Filters a list of results, using the query argument """
        return [x for x in results if query.strip().lower() in x['name'].lower()]

    def get_cheatsheets_list(self, query=None):
        """ Returns a list of available Cheat sheets from DevHints website """

        # Check results from cache
        if os.path.isfile(self.get_cache_file_path()):
            mtime = os.path.getmtime(self.get_cache_file_path())
            now = time.time()
            if now - mtime < CACHE_TTL:
                self.logger.info("Loading from cache")

                # pylint: disable=C0103
                with open(self.get_cache_file_path()) as f:
                    data = json.load(f)

                if query:
                    data = self.filter_results(data, query)

                return data

        self.logger.info("Loading cheat sheets from %s", self.url)

        # pylint: disable=C0103
        r = requests.get('%s/%s' % (self.url, '/data/search-index.json'))
        json_response = r.json()

        result = []
        for item in json_response:
            result.append({
                'name': str(item['title']),
                'category': item['category'],
                'url': '%s%s' % (self.url, item['url'])
            })

        if query:
            result = self.filter_results(result, query)

        result = sorted(result, key=lambda k: k['name'])

        with open(self.get_cache_file_path(), 'w') as cache_file:
            json.dump(result, cache_file)

        return result
