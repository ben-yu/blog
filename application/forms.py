"""
forms.py

Web forms based on Flask-WTForms

See: http://flask.pocoo.org/docs/patterns/wtforms/
     http://wtforms.simplecodes.com/

"""

from flaskext import wtf
from flaskext.wtf import validators
from wtforms.ext.appengine.ndb import model_form

from .models import Post

class ClassicPostForm(wtf.Form):
    post_title = wtf.TextField('Title', validators=[validators.Required()])
    post_slug = wtf.TextField('Slug', validators=[validators.Required()])
    post_body = wtf.TextAreaField('Body', validators=[validators.Required()], id='source')
    post_tags = wtf.TextField('Tags', validators=[validators.Required()])

PostForm = model_form(Post, ClassicPostForm, field_args={
    'post_title': dict(validators=[validators.Required()]),
    'post_slug': dict(validators=[validators.Required()]),
    'post_body': dict(validators=[validators.Required()]),
    'post_tags': dict(validators=[validators.Required()]),
})
