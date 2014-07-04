import webapp2
import jinja2
import os
import sys

from users import user_db as UDB

#create the paths for the templates
this_folder = os.path.dirname(__file__)
parent_folder = os.path.dirname(this_folder)
template_dir = os.path.join(parent_folder, 'templates')

jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

#define the template redering
def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)

class EnhancedHandler(webapp2.RedirectHandler):

    def __init__(self, *args, **kwargs):
        webapp2.RequestHandler.initialize(self, *args, **kwargs)
        self.arg_dict = {}
        uid = self.read_secure_cookie('user_id')
        if uid:
            self.user = uid
            self.arg_dict['user'] = self.user 
        else:
            self.user = 'guest'
        


    def write(self, *args, **kwargs):
        '''Shorthand for writing out.
        Use it like self.response.out.write(*args, **kwargs)
        '''
        self.response.out.write(*args, **kwargs)

    def render_str(self, template, **kwargs):
        t = jinja_env.get_template(template)
        return t.render(**kwargs)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))

    def set_secure_cookie(self, name, value):
        cookie_value = UDB.SecureValue().make_secure_value(value)
        self.response.headers.add_header(
                    'Set-Cookie',
                    '%s=%s; Path=/' % (name, cookie_value))

    def read_secure_cookie(self, name):
        cookie_value = self.request.cookies.get(name)
        return cookie_value and UDB.SecureValue().check_secure_value(cookie_value)

    def login(self, user_key):
        self.set_secure_cookie('user_id', str(user_key))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def check_super_user(self):
        if self.user not in ['admin']:
            self.render('sorry.html', **self.arg_dict)
            return False
        return True