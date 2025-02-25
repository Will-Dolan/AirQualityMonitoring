from email.message import EmailMessage
import base64, mimetypes

class Email:
	def __init__(self, to_email: str, from_email: str, subject: str) -> None:
		self.message = EmailMessage()
		self.message['To'] = to_email
		self.message['From'] = from_email
		self.message['Subject'] = subject

	def update_attachment(self, attachment_path: str):
		type_subtype, _ = mimetypes.guess_type(attachment_path)
		maintype, subtype = type_subtype.split('/')

		with open(attachment_path, 'rb') as fp:
			attachment_data = fp.read()
		self.message.add_attachment(attachment_data, maintype, subtype)
	
	def update_content(self, content: str):
		self.message.set_content(content)

	
	def send_email(self, service):
		encoded_message = base64.urlsafe_b64encode(self.message.as_bytes()).decode()

		self.create_message = {
			'raw': encoded_message
		}

		sent_message = service.users().messages().send(
			userId="me", 
			body=self.create_message
			).execute()
