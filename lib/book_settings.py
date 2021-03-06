# book_settings.py

import os
import re
from urllib import urlencode
from urllib2 import urlparse

from calibre_plugins.xray_creator.lib.goodreads_parser import GoodreadsParser

from calibre.utils.config import JSONConfig
from calibre.library import current_library_path
from calibre.ebooks.BeautifulSoup import BeautifulSoup

class BookSettings(object):
    GOODREADS_URL_PAT = re.compile(r'href="(/book/show/.+?)"')
    BOOK_ID_PAT = re.compile(r'\/show\/([\d]+)')
    AMAZON_ASIN_PAT = re.compile(r'data\-asin=\"([a-zA-z0-9]+)\"')
    GOODREADS_ASIN_PAT = re.compile(r'"asin":"(.+?)"')

    HEADERS = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/html", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0"}
    LIBRARY = current_library_path()
    HONORIFICS = 'mr mrs ms esq prof dr fr rev pr atty adv hon pres gov sen ofc pvt cpl sgt maj capt cmdr lt col gen'
    HONORIFICS = HONORIFICS.split()
    HONORIFICS.extend([x + '.' for x in HONORIFICS])
    HONORIFICS += 'miss master sir madam lord dame lady esquire professor doctor father mother brother sister reverend pastor elder rabbi sheikh'.split()
    HONORIFICS += 'attorney advocate honorable president governor senator officer private corporal sargent major captain commander lieutenant colonel general'.split()
    RELIGIOUS_HONORIFICS = 'fr br sr rev pr'
    RELIGIOUS_HONORIFICS = RELIGIOUS_HONORIFICS.split()
    RELIGIOUS_HONORIFICS.extend([x + '.' for x in RELIGIOUS_HONORIFICS])
    RELIGIOUS_HONORIFICS += 'father mother brother sister reverend pastor elder rabbi sheikh'.split()
    DOUBLE_HONORIFICS = 'lord'
    # We want all the honorifics to be in the general honorifics list so when we're checking if a word is an honorifics, we only need to search in one list
    HONORIFICS += RELIGIOUS_HONORIFICS
    HONORIFICS += DOUBLE_HONORIFICS

    COMMON_WORDS = 'the of de'.split()

    def __init__(self, db, book_id, goodreads_conn, amazon_conn, expand_aliases):
        self._db = db
        self._book_id = book_id
        self._goodreads_conn = goodreads_conn
        self._amazon_conn = amazon_conn
        self._expand_aliases = expand_aliases

        book_path = self._db.field_for('path', book_id).replace('/', os.sep)

        self._prefs = JSONConfig(os.path.join(book_path, 'book_settings'), base_path=self.LIBRARY)
        self.prefs.setdefault('asin', '')
        self.prefs.setdefault('goodreads_url', '')
        self.prefs.setdefault('aliases', {})
        self.prefs.commit()

        self._title = self._db.field_for('title', book_id)
        self._author = ' & '.join(self._db.field_for('authors', self._book_id))

        self.asin = self.prefs['asin'] if self.prefs['asin'] != '' else None
        if not self.asin:
            identifiers = self._db.field_for('identifiers', self._book_id)
            self.asin = self._db.field_for('identifiers', self._book_id)['mobi-asin'].decode('ascii') if 'mobi-asin' in identifiers.keys() else None
            if self.asin:
                self.prefs['asin'] = self.asin
            else:
                self.asin = self.search_for_asin(self.title_and_author)
                if self.asin:
                    mi = self._db.get_metadata(self._book_id)
                    identifiers = mi.get_identifiers()
                    identifiers['mobi-asin'] = self.asin
                    mi.set_identifiers(identifiers)
                    self._db.set_metadata(self._book_id, mi)
                    self.prefs['asin'] = self.asin

        self.goodreads_url = self.prefs['goodreads_url']
        if self.goodreads_url == '':
            url = None
            if self.asin:
                url = self.search_for_goodreads(self.asin)
            if not url and self.title != 'Unknown' and self.author != 'Unknown':
                url = self.search_for_goodreads(self.title_and_author)

            if url:
                self.goodreads_url = url
                self.prefs['goodreads_url'] = self.goodreads_url
                if not self.asin:
                    self.asin = self.search_for_asin_on_goodreads(self.goodreads_url)
                    if self.asin:
                        mi = self._db.get_metadata(self._book_id)
                        identifiers = mi.get_identifiers()
                        identifiers['mobi-asin'] = self.asin
                        mi.set_identifiers(identifiers)
                        self._db.set_metadata(self._book_id, mi)
                        self.prefs['asin'] = self.asin

        self._aliases = self.prefs['aliases']

        self.save()

    @property
    def prefs(self):
        return self._prefs

    @property
    def asin(self):
        return self._asin

    @asin.setter
    def asin(self, val):
        self._asin = val

    @property
    def title(self):
        return self._title

    @property
    def author(self):
        return self._author

    @property
    def title_and_author(self):
        return '%s - %s' % (self.title, self.author)

    @property
    def goodreads_url(self):
        return self._goodreads_url

    @goodreads_url.setter
    def goodreads_url(self, val):
        self._goodreads_url = val

    @property
    def aliases(self):
        return self._aliases

    @aliases.setter
    def aliases(self, val):
        # 'aliases' is a string containing a comma separated list of aliases.
        #
        # Split it, remove whitespace from each element, drop empty strings (strangely, split only does this if you don't specify a separator)
        #
        # so "" -> []  "foo,bar" and " foo   , bar " -> ["foo", "bar"]
        label, aliases = val
        aliases = [x.strip() for x in aliases.split(",") if x.strip()]
        self._aliases[label] =  aliases

    def save(self):
        self.prefs['asin'] = self.asin
        self.prefs['goodreads_url'] = self.goodreads_url
        self.prefs['aliases'] = self.aliases

    def search_for_asin(self, query):
        query = urlencode({'keywords': query})
        try:
            self._amazon_conn.request('GET', '/s/ref=sr_qz_back?sf=qz&rh=i%3Adigital-text%2Cn%3A154606011%2Ck%3A' + query[9:] + '&' + query, headers=self.HEADERS)
            response = self._amazon_conn.getresponse().read()
        except Exception as e:
            try:
                self._amazon_conn.close()
                self._amazon_conn.connect()
                self._amazon_conn.request('GET', '/s/ref=sr_qz_back?sf=qz&rh=i%3Adigital-text%2Cn%3A154606011%2Ck%3A' + query[9:] + '&' + query, headers=self.HEADERS)
                response = self._amazon_conn.getresponse().read()
            except:
                return None

        # check to make sure there are results
        if 'did not match any products' in response and not 'Did you mean:' in response and not 'so we searched in All Departments' in response:
            return None

        soup = BeautifulSoup(response)
        results = soup.findAll('div', {'id': 'resultsCol'})

        if not results or len(results) == 0:
            return None

        for r in results:
            if 'Buy now with 1-Click' in str(r):
                asinSearch = self.AMAZON_ASIN_PAT.search(str(r))
                if asinSearch:
                    return asinSearch.group(1)

        return None

    def search_for_goodreads(self, keywords):
        query = urlencode({'q': keywords})
        try:
            self._goodreads_conn.request('GET', '/search?' + query)
            response = self._goodreads_conn.getresponse().read()
        except:
            try:
                self._goodreads_conn.close()
                self._goodreads_conn.connect()
                self._goodreads_conn.request('GET', '/search?' + query)
                response = self._goodreads_conn.getresponse().read()
            except:
                return None

        # check to make sure there are results
        if 'No results' in response:
            return None

        urlsearch = self.GOODREADS_URL_PAT.search(response)
        if not urlsearch:
            return None

        # return the full URL with the query parameters removed
        url = 'https://www.goodreads.com' + urlsearch.group(1)
        return urlparse.urlparse(url)._replace(query=None).geturl()

    def search_for_asin_on_goodreads(self, url):
        book_id_search = self.BOOK_ID_PAT.search(url)
        if book_id_search:
            return None

        book_id = book_id_search.group(1)

        try:
            self._goodreads_conn.request('GET', '/buttons/glide/' + book_id)
            response = self._goodreads_conn.getresponse().read()
        except:
            try:
                self._goodreads_conn.close()
                self._goodreads_conn.connect()
                self._goodreads_conn.request('GET', '/buttons/glide/' + book_id)
                response = self._goodreads_conn.getresponse().read()
            except:
                return None

        book_asin_search = self.GOODREADS_ASIN_PAT.search(response)
        if not book_asin_search:
            return None

        return book_asin_search.group(1)

    def update_aliases(self, url, raise_error_on_page_not_found=False):
        try:
            goodreads_parser = GoodreadsParser(url, self._goodreads_conn, self._asin, create_xray=True, raise_error_on_page_not_found=raise_error_on_page_not_found)
            goodreads_parser.get_characters()
            goodreads_parser.get_settings()
            goodreads_chars = goodreads_parser.characters
        except:
            return

        self._aliases = {}
        characters = []
        alias_lookup = {}
        for char, char_data in goodreads_chars.items():
            characters.append(char_data['label'])
            alias_lookup[char_data['label']] = char_data['label']

            if char_data['label'] not in self.aliases.keys():
                self.aliases = (char_data['label'], ','.join(goodreads_chars[char]['aliases']))

            if not self._expand_aliases:
                continue

            for alias in char_data['aliases']:
                characters.append(alias)
                alias_lookup[alias] = char_data['label']

        aliases = self.auto_expand_aliases(characters)
        for alias, fullname in aliases.items():
            self.aliases = (alias_lookup[fullname], alias + ',' + ','.join(self.aliases[alias_lookup[fullname]]))

        for setting, setting_data in goodreads_parser.settings.items():
            self.aliases = (setting_data['label'], '')

    def auto_expand_aliases(self, characters):
        actual_aliases = {}
        duplicates = [x.lower() for x in characters]
        for fullname in characters:
            aliases = self.fullname_to_possible_aliases(fullname.lower())
            for alias in aliases:
                # if this alias has already been flagged as a duplicate or is a common word, skip it
                if alias in duplicates or alias in self.COMMON_WORDS:
                    continue
                # check if this alias is a duplicate but isn't in the duplicates list
                if actual_aliases.has_key(alias):
                    duplicates.append(alias)
                    actual_aliases.pop(alias)
                    continue

                # at this point, the alias is new -- add it to the dict with the alias as the key and fullname as the value
                actual_aliases[alias] = fullname

        return actual_aliases

    def fullname_to_possible_aliases(self, fullname):
        """
        Given a full name ("{Title} ChristianName {Middle Names} {Surname}"), return a list of possible aliases

        ie. Title Surname, ChristianName Surname, Title ChristianName, {the full name}

        The returned aliases are in the order they should match
        """
        aliases = []
        parts = fullname.split()

        if parts[0].lower() in self.HONORIFICS:
            title = []
            while len(parts) > 0 and parts[0].lower() in self.HONORIFICS:
                title.append(parts.pop(0))
            title = ' '.join(title)
        else:
            title = None

        if len(parts) >= 2:
            # Assume: {Title} Firstname {Middlenames} Lastname
            # Already added the full form, also add Title Lastname, and for some Title Firstname
            surname = parts.pop() # This will cover double barrel surnames, we split on whitespace only
            christian_name = parts.pop(0)
            middlenames = parts
            if title:
                # Religious Honorifics usually only use {Title} {ChristianName}
                # ie. John Doe could be Father John but usually not Father Doe
                if title in self.RELIGIOUS_HONORIFICS:
                    aliases.append("%s %s" % (title, christian_name))
                # Some titles work as both {Title} {ChristianName} and {Title} {Lastname}
                # ie. John Doe could be Lord John or Lord Doe
                elif title in self.DOUBLE_HONORIFICS:
                    aliases.append("%s %s" % (title, christian_name))
                    aliases.append("%s %s" % (title, surname))
                # Everything else usually goes {Title} {Lastname}
                # ie. John Doe could be Captain Doe but usually not Captain John
                else:
                    aliases.append("%s %s" % (title, surname))
            aliases.append(christian_name)
            aliases.append(surname)
            aliases.append("%s %s" % (christian_name, surname))

        elif title:
            # Odd, but got Title Name (eg. Lord Buttsworth), so see if we can alias
            if len(parts) > 0:
                aliases.append(parts[0])
        else:
            # We've got no title, so just a single word name.  No alias needed
            pass
        return aliases