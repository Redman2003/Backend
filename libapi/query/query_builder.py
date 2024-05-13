import json
import requests

###
### - only works for GET and POST http methods currently, I think that's all we need to worry about too
### - we aren't posting info to the api anyway
###
class QueryBuilder:
    def __init__(self,url="",params={}, headers={}, data={}):
        if url != "":
            self.url = [url]
        else:
            self.url = []
            
        self.params=params
        self.headers=headers
        self.data=data
        
    def add_params(self, key="", value=""):
        self.params[key] = value
        return self
    
    def remove_params(self, key="", value=""):
        if key in self.params:
            del self.params[key]
        return self
    
    def append_url(self, value=""):
        self.url.append(value)
        return self
    
    def add_header(self, key="", value=""):
        self.headers[key] = value
        return self

    ### use for post requests
    def add_data(self, key="", value=""):
        self.data[key] = value
        return self

    def remove_data(self, key="", value=""):
        if key in self.data:
            del self.data[key]
        return self

    def remove_header(self, key="", value=""):
        if key in self.headers:
            del self.headers[key]
        return self
    
    def clear(self):
        self.url = []
        self.params = {}
        self.headers = {}
        self.data = {}
        return self

    def print_headers(self):
        print(self.headers)
        return self

    def print_data(self):
        print(self.data)
        return self

    def make_get_request(self):
        _url = '/'.join(self.url)
        return requests.get(_url, params=self.params, headers=self.headers)
    
    def make_post_request(self):
        _url = '/'.join(self.url)
        return requests.post(_url, data=self.data, headers=self.headers)
    
    def add_to_url(self, new):
        self.url.append(new)
        return self
    
    def remove_from_url(self):
        self.url.pop(-1)
        return self
