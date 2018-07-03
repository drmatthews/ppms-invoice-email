# -*- coding: utf-8 -*-

from datetime import datetime


class Recipient:
    """Abstraction of a group in PPMS. Attributes mirror the return value
    of the `getgroup` action of the PUMAPI.

    Attributes:
        unitlogin (str): Unique ID of the group in PPMS
        unitname (str): Group name in PPMS
        headname (str): Name of the group head in PPMS
        heademail (str): Email address of the group head in PPMS
        unitbcode (str): Default account code (grant code) of the
            group in PPMS - note that this could be an empty string
        department (str): The department the group belongs to
        institution (str): The institution the group belongs to
        address (str): The postal address of the group
        affiliation (str): Any affiliation
        ext (bool): Is the group `external` to KCL
        active (bool): Is the group active
        admname (str): Name of a group admin
        admemail (str): Email address of the group admin
        creationdate (str): Date of creation of the group -
            note that this could be empty if auto-generated by Stratocore

        bcode (str): The grant code being charged on this invoice
        invoice (str): Path the html file containing the summary of charges
            - this html is created by `generate_invoice --> create_html`
        cc_admin (bool): If there is a group admin they get cc'd in the email
            containing the summary
        send_only_admin (bool): If a group head chooses not to recieve the
            invoice summary, it will only get sent to the group admin
    """
    def __init__(self, group_details):

        for key in group_details:
            setattr(self, key, group_details[key])

        self.address = self.address.replace('|', ', ')
        if self.ext == 'false':
            self.ext = False
        if self.ext == 'true':
            self.ext = True
        if self.active == 'false':
            self.active = False
        if self.active == 'true':
            self.active = True
        if self.creationdate:
            self.creationdate = datetime.strptime(
                self.creationdate, "%Y/%m/%d"
            )
        self._bcode = None
        self._invoice = None
        self._cc_admin = False
        self._send_only_admin = False

    @property
    def bcode(self):
        return self._bcode

    @bcode.setter
    def bcode(self, value):
        self._bcode = value

    @property
    def invoice(self):
        return self._invoice

    @invoice.setter
    def invoice(self, value):
        self._invoice = value

    @property
    def send_only_admin(self):
        return self._send_only_admin

    @send_only_admin.setter
    def send_only_admin(self, value):
        self._send_only_admin = value

    def __repr__(self):
        """"""
        return "<Recipient: {0}>".format(self.heademail)


def recipient_from_group(group_text):
    """Create a recipient object from a `group` returned as
    text from the PUMAPI call.recipient

    Returns: Recipient object
    """
    keys = [word for word in group_text.splitlines()[0].split(',')]
    values = [
        word.replace('"', '') for word in group_text.splitlines()[1].split(',')
    ]

    group = {}
    for k, v in zip(keys, values):
        # print("key: {0}, value: {1}".format(k, v))
        group[k] = v
    return Recipient(group)
