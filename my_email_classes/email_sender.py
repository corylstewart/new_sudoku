from google.appengine.api import mail

class SendEmail:
    def __init__(self, recipient_name, recipient_email, subject, body,
                sender_name = 'Cory Stewart', 
                sender_email = 'corylstewart@gmail.com',
                attachments=None):
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.recipient_name = recipient_name
        self.recipient_email = recipient_email
        self.subject = subject
        self.body = body
                		
        self.make_addresses()
        if attachments:
            pass
        #self.attachment = attachment

    def make_addresses(self):
        self.sender = self.sender_name + ' <' + self.sender_email + '>'
        self.recipient = self.recipient_name + ' <' + self.recipient_email + '>'

    def send_email(self):
        mail.send_mail(sender = self.sender,
					        to = self.recipient,
					        subject = self.subject,
					        body = self.body)

    def construct_attachments(self):
        self.attachments = []
        for attachment in attachments:
            self.attachments.append(mail.Attachment(attachment[0], attachment[1]))


class AdminAlertEmail:
	def __init__(self):
		self.recipient_name = 'Cory Stewart'
		self.recipient_email = 'corylstewart@gmail.com'
		self.subject = 'There has been activity on Demo Page'
		
	def send_new_user_email(self):
		self.body = 'You have a new user'
		self.send_email()
		
	def send_new_picure_upload(self):
		self.body = 'A new picture has been uploaded'
		self.send_email()
		
	def send_new_option_position(self):
		self.body = 'A new option position has been created'
		self.send_email()
		
		
	def send_email(self):
		email = SendEmail(self.recipient_name,
								self.recipient_email,
								self.subject,
								self.body)
		email.send_email()