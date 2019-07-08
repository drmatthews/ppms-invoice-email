# -*- coding: utf-8 -*-

import os
from exchangelib import (
    DELEGATE, Account, Credentials,
    Configuration, Message, HTMLBody,
    Mailbox
)

USERNAME = os.environ['KCL_USERNAME']
PASSWORD = os.environ['KCL_PASSWORD']

credentials = Credentials(username=USERNAME, password=PASSWORD)

config = Configuration(server='outlook.office365.com', credentials=credentials)
account = Account(primary_smtp_address='nic@kcl.ac.uk', config=config,
                  autodiscover=False, access_type=DELEGATE)


def send(recipients, invoice_ref):
    """Construct email from Recipient object and send.

    Args:
        recipients (list): A list of recipient objects
        invoice_ref (str): Identifier of the invoice
            being emailed
    """

    for recipient in recipients:

        address = recipient.heademail
        cc_address = recipient.admemail

        if recipient.send_only_admin:
            address = recipient.admemail
            cc_address = ""
    
        print("address: {}".format(address))
        print("cc_address: {}".format(cc_address))
        try:
            m = Message(
                account=account,
                folder=account.sent,
                subject=(
                    'NIC@KCL: Invoice {0}'
                    .format(invoice_ref)
                ),
                to_recipients=[Mailbox(email_address=address)]
            )
            if cc_address:
                m.cc_recipients = [
                    Mailbox(email_address=cc_address),
                ]

            f = open(recipient.invoice, "r").read()
            m.body = HTMLBody(f)
            m.send_and_save()
        except:
            print('could not send email about {}'.format(invoice_ref))
            pass