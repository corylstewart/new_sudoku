#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import sys
import jinja2
import re

from EnhancedHandler import EnhancedHandler as EH
from sudoku import sudoku_handler as SH
from users import user_handler as UH
from options import option_handler as OH
from options import option_memcache as OM


class MainHandler(EH.EnhancedHandler):
    def get(self):
        self.render('welcome.html', **self.arg_dict)

class ResumeHandler(EH.EnhancedHandler):
    def get(self):
        self.render('resume.html',  **self.arg_dict)

class Play(EH.EnhancedHandler):
    def get(self):
        optionable = OM.OptionsMemcache().get_optionable_list()
        self.write(optionable)
        self.write('done')

class StockHandler(EH.EnhancedHandler):
    def get(self):
        self.write('<script src="//www.gmodules.com/ig/ifr?url=http://hosting.gmodules.com/ig/gadgets/file/102972771291788536078/google-finance-yahoo-stock-ticker.xml&amp;synd=open&amp;w=320&amp;h=200&amp;title=&amp;border=%23ffffff%7C3px%2C1px+solid+%23999999&amp;output=js"></script>')

PAGE_RE = r'((/(?:[a-zA-Z0-9_-]+/?)*))?'

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/resume', ResumeHandler),
    ('/sudoku', SH.SudokuLevelHandler),
    ('/sudoku/makedb', SH.CreateDB),
    ('/sudoku/get', SH.GetPuzzle),
    ('/sudoku/deletedb', SH.ClearDB),
    ('/stock', StockHandler),
    ('/signup', UH.SignUpHandler),
    ('/login', UH.LoginHandler),
    ('/logout', UH.LogoutHandler),
    ('/optionposition', OH.OptionPageHandler),
    ('/play', Play)
], debug=True)
