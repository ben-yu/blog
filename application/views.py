"""
views.py

URL route handlers

"""
from google.appengine.api import users
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import request, render_template, flash, url_for, redirect

from flask_cache import Cache

from application import app
from decorators import login_required, admin_required
from forms import ClassicPostForm
from models import Post


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


def home():
    return render_template('about.html', target='about')

def about():
    return render_template('contact.html', target='contact')

def game():
    return render_template('game.html')

@cache.cached(timeout=60)
def list_posts():
    """List all posts"""
    posts = Post.query()
    return render_template('list_posts.html', posts=posts, target='main')


def show_post(post_slug):
    """List a single post"""
    post = Post.query(Post.post_slug == post_slug)
    return render_template('permalink.html', post=post)

@admin_required
def new_post():
    form = ClassicPostForm(request.form)
    if request.method == "POST" and form.validate():
        post = Post()
        post.post_title = form.data.get('post_title')
        post.post_slug = form.data.get('post_slug')
        post.post_body = form.data.get('post_body')
        post.post_tags = form.data.get('post_tags')
        post.put()
        flash(u'Post successfully saved.', 'success')
        return redirect(url_for('list_posts'))
    return render_template('newpost.html', form=form)

@admin_required
def edit_post(post_id):
    post = Post.get_by_id(post_id)
    form = ClassicPostForm(obj=post)
    if request.method == "POST" and form.validate():
        post = Post()
        post.post_title = form.data.get('post_title')
        post.post_slug = form.data.get('post_slug')
        post.post_body = form.data.get('post_body')
        post.post_tags = form.data.get('post_tags')
        post.put()
        flash(u'Post successfully saved.', 'success')
        return redirect(url_for('list_posts'))
    return render_template('newpost.html', post=post, form=form)

@admin_required
def delete_post(post_id):
    """Delete an example object"""
    post = Post.get_by_id(post_id)
    try:
        post.key.delete()
        flash(u'Example %s successfully deleted.' % post_id, 'success')
        return redirect(url_for('list_posts'))
    except CapabilityDisabledError:
        flash(u'App Engine Datastore is currently in read-only mode.', 'info')
        return redirect(url_for('list_posts'))

def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''

