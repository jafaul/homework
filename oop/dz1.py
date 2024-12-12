import copy
from typing import Optional


class Url:
    def __init__(
            self,
            scheme: str,
            authority: str,
            path: Optional[list] = None,
            query: Optional[dict] = None,
            fragment: str = ""
    ):
        """
               :param scheme: required (e.g. http, https)
               :param authority: domain or authority part (e.g. www.example.com / localhost:80)
               :param path: optional, by default '' (e.g.if "/3456/my-document", path = [3456, my-document])
               :param query: optional, by default '' (e.g. if key1=value1&key2=value2, query = {'key1': 'value1, ...})
               :param fragment: optional, by default '' (e.g. bar from http://www.example.org/foo.html#bar)
        """

        self.scheme = scheme
        self.authority = authority
        self.path = path if path is not None else []
        self.query = query if query is not None else {}
        self.fragment = fragment

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __str__(self):
        url = f"{self.scheme}://{self.authority}"
        if self.path:
            url += f"/{'/'.join(self.path)}"
        if self.query:
            query = '&'.join(f"{key}={value}" for key, value in self.query.items())
            url += f"?{query}"
        if self.fragment:
            url += f"#{self.fragment}"
        return url


class HttpsUrl(Url):
    def __init__(
            self,
            authority: str,
            path: Optional[list] = None,
            query: Optional[dict] = None,
            fragment: str = ""
    ):
        super().__init__('https', authority, path, query, fragment)


class HttpUrl(Url):
    def __init__(
            self,
            authority: str,
            path: Optional[list] = None,
            query: Optional[dict] = None,
            fragment: str = ""
    ):
        super().__init__('http', authority, path, query, fragment)


class GoogleUrl(HttpsUrl):
    def __init__(
            self,
            path: Optional[list] = None,
            query: Optional[dict] = None,
            fragment: str = ""
    ):
        super().__init__("google.com", path, query, fragment)


class WikiUrl(HttpsUrl):
    def __init__(
            self,
            path: Optional[list] = None,
            query: Optional[dict] = None,
            fragment: str = ""
    ):
        super().__init__("wikipedia.org", path, query, fragment)


# task 5
class UrlCreator:
    def __init__(self, scheme: str, authority: str):
        self.scheme = scheme
        self.authority = authority
        self.path = []
        self.query = {}
        self.fragment = ""

    def _create(self) -> Url:
        return Url(
            scheme=self.scheme, authority=self.authority, path=self.path, query=self.query, fragment=self.fragment
        )

    # why does not it work correctly and
    # return https://docs.python.org/shape/shape/__len__/shape/shape/__len__/docs/v1/api/list/shape/shape/__len__?
    # it is not present if __getattr__ method is commented.
    # self.path = ['shape', 'shape', '__len__'] implicitly right after creation an obj
    # def __getattr__(self, item: str):
    #     self.path.append(item)
    #     return self

    def __getattr__(self, item: str):
        new_creator = UrlCreator(self.scheme, self.authority)
        new_creator.path = copy.copy(self.path)
        new_creator.path.append(item)

        new_creator.query = copy.copy(self.query)
        new_creator.fragment = copy.copy(self.fragment)
        return new_creator

    def __call__(self, *path, **query):
        # here path = () and query = {}
        new_creator = UrlCreator(self.scheme, self.authority)
        new_creator.path = copy.copy(self.path)
        new_creator.query = copy.copy(self.query)
        new_creator.fragment = copy.copy(self.fragment)

        new_creator.path.extend(path)
        new_creator.query.update(query)
        return new_creator

    def __str__(self):
        return str(self._create())

    def __eq__(self, other) -> bool:
        return str(self) == str(other)


assert GoogleUrl() == HttpsUrl(authority='google.com')
assert GoogleUrl() == Url(scheme='https', authority='google.com')
assert GoogleUrl() == 'https://google.com'
assert WikiUrl() == str(Url(scheme='https', authority='wikipedia.org'))
assert WikiUrl(path=['wiki', 'python']) == 'https://wikipedia.org/wiki/python'
assert GoogleUrl(query={'q': 'python', 'result': 'json'}) == 'https://google.com?q=python&result=json'

# UrlCreator check
url_creator=UrlCreator(scheme='https', authority='docs.python.org')
assert url_creator.docs.v1.api.list == 'https://docs.python.org/docs/v1/api/list'
assert url_creator("api", "v1","list") == 'https://docs.python.org/api/v1/list'
assert url_creator("api", "v1","list", q='my_list') == 'https://docs.python.org/api/v1/list?q=my_list'
assert url_creator('3').search(q='getattr', check_keywords='yes', area='default')._create()  == \
       'https://docs.python.org/3/search?q=getattr&check_keywords=yes&area=default'
