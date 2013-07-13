import os
import re
import random
import hashlib
import hmac
import logging
import json
import functools
import webapp2
import jinja2
import markdown2
import email

from string import letters
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

secret = 'beyu'

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

#-- Admin wrapper to make restrict access
def administrator(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        user = users.get_current_user()
        if not user:
            if self.request.method == "GET":
                self.redirect(users.create_login_url(self.request.uri))
                return
            raise web.HTTPError(403)
        elif not users.is_current_user_admin():
            raise web.HTTPError(403)
        else:
            return method(self, *args, **kwargs)
    return wrapper

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)


#-- Generic Handler for Blog

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_json(self, d):
        json_txt = json.dumps(d)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(json_txt)

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'

class LoginHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>)" %
                        (user.nickname(), users.create_logout_url("/")))
        else:
            greeting = ("<a href=\"%s\">Sign in or register</a>." %
                        users.create_login_url("/"))

        self.response.out.write("<html><body>%s</body></html>" % greeting)

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

#-- Blog Post class
class Post(db.Model):
    author = db.UserProperty()
    slug = db.StringProperty()
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        #self._render_text = self.content.replace('\n', '<br>')
        self._render_text = self.content
        return render_str("post.html", p = self)

    def render_condensed(self):
        #self._render_text = self.content.replace('\n', '<br>')
        self._render_text = self.content
        return render_str("post.html", p = self)

    def as_dict(self):
        time_fmt = '%c'
        d = {'subject': self.subject,
             'content': self.content,
             'created': self.created.strftime(time_fmt),
             'last_modified': self.last_modified.strftime(time_fmt)}
        return d

class GenericHandler(BlogHandler):
    def get(self):
        self.render("about.html", users = users)

class AboutHandler(BlogHandler):
    def get(self):
        self.render("about.html", target = "about", users = users)

class GameHandler(BlogHandler):
    def get(self):
        self.render("game.html", target = "game", users = users)

class ContactHandler(BlogHandler):
    def get(self):
        self.render("contact.html", target = "contact", users = users)

#-- Blog front page handler
class BlogFront(BlogHandler):
	def get(self):
		key = 'top'
		posts = memcache.get(key)
		if posts is None:
			logging.error("DB QUERY")
			posts = Post.all().order('-created').fetch(limit=10)
			memcache.set(key, posts)
		if self.format == 'html':
			self.render('front.html', posts = posts, target = "main", users = users)
		else:
			return self.render_json([p.as_dict() for p in posts])

#--Permalink post page Handler
class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return
        if self.format == 'html':
            self.render("permalink.html", post = post)
        else:
            self.render_json(post.as_dict())

class NewPost(BlogHandler):
    @administrator
    def get(self):
        self.render("newpost.html")

    @administrator
    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent = blog_key(), subject = subject, content = markdown2.markdown(content.decode()))
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)

class FeedHandler(BlogHandler):
    def get(self):
        posts = db.Query(Post).order('-created').fetch(limit=10)
        self.response.headers['Content-Type'] = 'application/atom+xml'
        self.render("atom.xml", posts=posts)


class EmailHandler(InboundMailHandler):
    def receive(self, mail_message):
        post = Post()
        post.title = mail_message.subject
        for content_type, body in mail_message.bodies():
            post.body = markdown2.markdown(body.decode())
        post.author = 'Benjamin Yu'
        post.put()

app = webapp2.WSGIApplication([('/', AboutHandler),
                               ('/blog/([0-9]+)(?:.json)?', PostPage),
                               ('/blog', BlogFront),
                               ('/game', GameHandler),
                               ('/about', ContactHandler),
                               ('/newpost', NewPost),
                               ('/login', LoginHandler),
                               ('/feed', FeedHandler),
                               EmailHandler.mapping(),
                               ],
                              debug=True)
