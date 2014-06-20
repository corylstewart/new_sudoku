import webapp2
import jinja2
import os


#create the paths for the templates
#template_dir = os.path.join(os.path.dirname(__file__), 'templates')
this_folder = os.path.dirname(__file__)
parent_folder = os.path.dirname(this_folder)
template_dir = os.path.join(parent_folder, 'templates')

jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

#define the template redering
def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)

class EnhancedHandler(webapp2.RedirectHandler):

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

    def __init__(self, *args, **kwargs):
        webapp2.RequestHandler.initialize(self, *args, **kwargs)
        self.arg_dict = {}