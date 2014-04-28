# Author: Harm van Tilborg <harm@zeroxcool.net>
# URL: https://github.com/hvt/Sick-Beard/tree/dtt
#
# This file is part of Sick Beard.
#
# Sick Beard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.

import urllib
import sickbeard
import generic

from sickbeard.common import Quality
from sickbeard import logger
from sickbeard import tvcache
from sickbeard.helpers import sanitizeSceneName
from sickbeard import show_name_helpers
from sickbeard.exceptions import ex


class DTTProvider(generic.TorrentProvider):
    def __init__(self):
        generic.TorrentProvider.__init__(self, "DailyTvTorrents")
        self.supportsBacklog = True
        self.cache = DTTCache(self)
        self.url = 'http://www.dailytvtorrents.org/'

    def isEnabled(self):
        return sickbeard.DTT

    def imageName(self):
        return 'dailytvtorrents.gif'

    def getQuality(self, item):
        url = item.enclosures[0].href
        quality = Quality.sceneQuality(url)
        return quality

    def getSearchResults(self, show, season, ep_objs, seasonSearch=False, manualSearch=False):
        return generic.TorrentProvider.getSearchResults(self, show, season, ep_objs, seasonSearch, manualSearch)

    def _dtt_show_id(self, show_name):
        return sanitizeSceneName(show_name).replace('.', '-').lower()

    def _get_season_search_strings(self, show, season, episode):
        search_string = []

        for show_name in set(show_name_helpers.allPossibleShowNames(show)):
            show_string = sanitizeSceneName(show_name).replace('.', '-').lower()
            search_string.append(show_string)

        return search_string

    def _get_episode_search_strings(self, show, season, episode, add_string=''):
        return self._get_season_search_strings(show, season, episode)

    def _doSearch(self, search_params, show=None, age=None):

        #        show_id = self._dtt_show_id(show.name)

        params = {"items": "all"}

        if sickbeard.DTT_NORAR:
            params.update({"norar": "yes"})

        if sickbeard.DTT_SINGLE:
            params.update({"single": "yes"})

        searchURL = self.url + "rss/show/" + search_params + "?" + urllib.urlencode(params)

        logger.log(u"Search string: " + searchURL, logger.DEBUG)

        data = self.getRSSFeed(searchURL)

        if not data:
            return []

        try:
            items = data.entries
        except Exception, e:
            logger.log(u"Error trying to load DTT RSS feed: " + ex(e), logger.ERROR)
            logger.log(u"RSS data: " + data, logger.DEBUG)
            return []

        results = []

        for curItem in items:
            (title, url) = self._get_title_and_url(curItem)
            results.append(curItem)

        return results

    def _get_title_and_url(self, item):
        title = item.title
        url = item.enclosures[0].href

        return (title, url)


class DTTCache(tvcache.TVCache):
    def __init__(self, provider):
        tvcache.TVCache.__init__(self, provider)

        # only poll DTT every 30 minutes max
        self.minTime = 30

    def _getRSSData(self):

        params = {"items": "all"}

        if sickbeard.DTT_NORAR:
            params.update({"norar": "yes"})

        if sickbeard.DTT_SINGLE:
            params.update({"single": "yes"})

        url = self.provider.url + 'rss/allshows?' + urllib.urlencode(params)
        logger.log(u"DTT cache update URL: " + url, logger.DEBUG)
        return self.provider.getRSSFeed(url)

    def _parseItem(self, item):
        title, url = self.provider._get_title_and_url(item)
        logger.log(u"Adding item from RSS to cache: " + title, logger.DEBUG)
        return self._addCacheEntry(title, url)


provider = DTTProvider()