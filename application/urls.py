"""
urls.py

URL dispatch route mappings and error handlers

"""
from flask import render_template

from application import app
from application import views


## URL dispatch rules
# App Engine warm up handler
# See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
app.add_url_rule('/_ah/warmup', 'warmup', view_func=views.warmup)

# Home page
app.add_url_rule('/', 'home', view_func=views.home)

# Home page
app.add_url_rule('/about', 'about', view_func=views.about)

app.add_url_rule('/game', 'game', view_func=views.game)

# Blog
app.add_url_rule('/blog', 'list_posts', view_func=views.list_posts, methods=['GET'])

# Single post
app.add_url_rule('/blog/<post_slug>', 'show_post', view_func=views.show_post, methods=['GET'])

# Edit a post
app.add_url_rule('/blog/new', 'new_post', view_func=views.new_post, methods=['GET', 'POST'])

# Edit a post
app.add_url_rule('/blog/<int:post_id>/edit', 'edit_post', view_func=views.edit_post, methods=['GET', 'POST'])

# Delete a post
app.add_url_rule('/blog/<int:post_id>/delete', view_func=views.delete_post, methods=['POST'])


## Error handlers
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

