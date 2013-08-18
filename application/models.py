"""
models.py

App Engine datastore models

"""

import markdown2

from google.appengine.ext import ndb

#-- Blog Post class
class Post(ndb.Model):
    author = ndb.UserProperty()
    post_slug = ndb.StringProperty()
    post_title = ndb.StringProperty(required = True)
    post_tags = ndb.StringProperty(required = True)
    post_body = ndb.TextProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    last_modified = ndb.DateTimeProperty(auto_now = True)

    def render_body(self):
        return markdown2.markdown(self.post_body)
