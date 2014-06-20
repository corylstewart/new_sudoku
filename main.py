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


class MainHandler(EH.EnhancedHandler):
    def get(self):
        self.response.write('Hello world!')

class ResumeHandler(EH.EnhancedHandler):
    def get(self):
        self.response.write('Hello world! Again')

PAGE_RE = r'((/(?:[a-zA-Z0-9_-]+/?)*))?'

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/resume', ResumeHandler),
    ('/sudoku', SH.SudokuLevelHandler),
    #('/sudoku' + PAGE_RE, SH.SudokuLevelHandler),
    ('/sudoku/user', SH.SudokuUserGeneratedHandler),
    ('/sudoku/makedb', SH.CreateDB),
    ('/sudoku/get', SH.GetPuzzle),
    ('/sudoku/deletedb', SH.ClearDB)
], debug=True)
