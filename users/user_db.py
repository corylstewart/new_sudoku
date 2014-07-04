import re
import random
import hashlib
import hmac
from string import letters
import secret

from google.appengine.ext import ndb

class User(ndb.Model):
    user_name = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add = True)

    def by_id(self, user_id):
        return User.get_by_id(user_id)

    def by_name(self, name):
        user = User.query(User.user_name == name)
        if user.count() > 0:
            for u in user:
                return u
        else:
            return False

    def register(self, name, pw_hash, email = None):
        user = User(user_name = name,
                    pw_hash = pw_hash,
                    email = email)
        user_key = user.put()
        return user_key

    def user_exists(self, name):
        user = self.by_name(name)
        if user:
            return True
        else:
            return False


class SecureValue:

    def __init__(self):
        self.secret = secret.secret

    def make_secure_value(self, value):
        return '%s|%s' % (value, hmac.new(self.secret,value).hexdigest())

    def check_secure_value(self, secure_value):
        value = secure_value.split('|')[0]
        if secure_value == self.make_secure_value(value):
            return value

    def make_salt(self, length=5):
        return ''.join(random.choice(letters) for x in range(length))

    def make_pw_hash(self, name, pw, salt=None):
        if not salt:
            salt = self.make_salt()
        pw_hash = hashlib.sha256(name+pw+salt).hexdigest()
        return '%s|%s' % (salt, pw_hash)

    def check_valid_pw(self, name, password, pw_hash):
        salt = pw_hash.split('|')[0]
        return pw_hash == self.make_pw_hash(name, password, salt)


class ValidInputs:

    def valid_user_name(self, user_name):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        return user_name and USER_RE.match(user_name)

    def valid_password(self, password):
        PASS_RE = re.compile(r"^.{3,20}$")
        return password and PASS_RE.match(password)
 
    def valid_email(self, email):
        EMAIL_RE  = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
        return not email or EMAIL_RE.match(email)