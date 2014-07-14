from users import user_db as UDB
from EnhancedHandler import EnhancedHandler as EH
from my_email_classes import email_sender as EMS

class SignUpHandler(EH.EnhancedHandler):
    def get(self):
        self.render('signup-form.html')

    def post(self):
        self.have_error = False
        self.user_name = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        self.arg_dict['username'] = self.user_name
        self.arg_dict['email'] = self.email

        check_user = UDB.ValidInputs()
        if not check_user.valid_user_name(self.user_name):
            self.arg_dict['error_username'] = "That's not a valid username"
            self.have_error = True

        if not check_user.valid_password(self.password):
            self.arg_dict['error_password'] = "That wasn't a valid password."
            self.have_error = True
        elif self.password != self.verify:
            self.arg_dict['error_verify'] = "Your passwords didn't match."
            self.have_error = True

        if not check_user.valid_email(self.email):
            self.arg_dict['error_email'] = "That's not a valid email."
            self.have_error = True

        if self.have_error:
            self.render('signup-form.html', **self.arg_dict)
        else:
            if UDB.User().by_name(self.user_name):
                msg = 'That user already exists.'
                self.render('signup-form.html', error_username = msg)
            else:
                self.pw_hash = UDB.SecureValue().make_pw_hash(self.user_name, self.password)
                UDB.User().register(self.user_name, self.pw_hash, self.email)
                self.login(self.user_name)
                EMS.AdminAlertEmail().send_new_user_email()   #####this is the new line to send an email 7/9/2014
                self.redirect('/')
                


class LoginHandler(EH.EnhancedHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        self.user_name = self.request.get('username')
        self.password = self.request.get('password')
        
         #check to see if the users name is in the database
        user = UDB.User().by_name(self.user_name)

        if not user:               
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)
            return

        #if user is in the database check to see if the passsword matchs
        secure = UDB.SecureValue().check_valid_pw(self.user_name, self.password, user.pw_hash)
        if not secure:
            msg = 'Password and login do not match'
            self.render('login-form.html', error = msg)
        else:
            self.login(user.user_name)
            self.redirect('/')

class LogoutHandler(EH.EnhancedHandler):
    def get(self):
        self.logout()
        self.redirect('/')