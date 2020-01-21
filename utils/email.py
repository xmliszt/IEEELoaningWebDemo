import smtplib, ssl
from utils.log_manager import log_manager

logger = log_manager("email_sender")

port = 587  # For SSL
password = "mygod2968816"

#
sender_email = "sutdieeeweb@gmail.com"

# Create a secure SSL context
context = ssl.create_default_context()


def send_email(message, receiver):
    '''

    :param message:
    :param receiver:
    :return:
    '''
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.ehlo()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver, message)
            server.close()
    except Exception as e:
        logger.error("Failed to send email! "+str(e))
        print("Failed to send email!")
        return -1
