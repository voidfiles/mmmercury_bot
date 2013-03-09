import requests
import json


class AdnClient(object):
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, access_token=None):

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.api_anchor = 'https://alpha-api.app.net/stream/0/%s'
        self.client = requests.session()

    def _request(self, url, method='GET', params=None, files=None, api_call=None, headers=None, *args, **kwargs):

        method = method.lower()
        if not method in ('get', 'post', 'delete'):
            return "ERROR: NOT CORRECT METHOD"

        params = params or {}
        headers = headers or {}

        func = getattr(self.client, method)

        headers['Authorization'] = 'Bearer %s' % self.access_token

        if method == 'get' or method == 'delete':
            kwargs['params'] = params
        else:
            kwargs.update({
                'files': files,
                'data': params
            })

        response = func(url, headers=headers, *args, **kwargs)

        content = json.loads(response.content)

        return content

    def api_request(self, url, *args, **kwargs):
        url = self.api_anchor % (url,)
        headers = kwargs.get('headers', {})
        method = kwargs.get('method', 'get')

        # If we are posting we are probably going to be posting JSON
        if method == "POST":
            headers.update({'Content-type': 'application/json'})

        kwargs['headers'] = headers
        return self._request(url, *args, **kwargs)

    def streams(self, *args, **kwargs):
        return self.api_request('/streams', *args, **kwargs)

    def filters(self, *args, **kwargs):
        return self.api_request('/filters', *args, **kwargs)
