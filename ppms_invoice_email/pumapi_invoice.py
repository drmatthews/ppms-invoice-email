# -*- coding: utf-8 -*-

import requests
import os
import pandas as pd
from datetime import datetime

from recipient import recipient_from_group
from session import (
    sessions_from_invoice,
    filter_by_session_type,
    total_charge,
    check_for_adjustments
)
import generate_invoice
import send_email

import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

PPMS_PUMAPI_KEY = os.environ['PPMS_PUMAPI_KEY']
PPMS_URL = 'https://ppms.eu/kcl/pumapi/'


def PPMS_call(payload):
    """Does the actual PUMAPI call"""
    try:
        r = requests.post(PPMS_URL, data=payload)
        if r.status_code == 200:
            return r.text
        else:
            raise ValueError("Response not received from PPMS")
    except: # noqa
        print("PPMS API request could not be completed")


def get_invoice(invoice_ref):
    """Set up a PUMAPI call with the action `getinvoice`"""
    invoice = {
        'action': 'getinvoice',
        'invoiceid': invoice_ref,
        'apikey': PPMS_PUMAPI_KEY,
    }

    i = PPMS_call(invoice)
    return (
        pd.read_csv(
            StringIO(i),
            sep=",",
            names=["bcode", "total"]
        )
    )


def get_invoice_details(bcode, invoice_ref):
    """Set up a PUMAPI call with the action `getinvoicedetails`"""
    invoice_details = {
        'action': 'getinvoicedetails',
        'invoiceid': invoice_ref,
        'bcode': bcode,
        'apikey': PPMS_PUMAPI_KEY,
    }
    return PPMS_call(invoice_details)


def get_group(group_ref):
    """Set up a PUMAPI call with the action `getgroup`

    Args:
        group_ref (str): The grant code as a reference to the group in PPMS

    Returns:
        A Recipient object
    """
    group = {
        'action': 'getgroup',
        'unitlogin': group_ref,
        'apikey': PPMS_PUMAPI_KEY,
    }
    g = PPMS_call(group)
    return recipient_from_group(g)


def make_invoices(invoice_ref, split_codes, include, exclude, only_admin):
    """Use the PUMAPI to create an html invoice

    Args:
        invoice_ref (str): Identifier for the PPMS invoice
        split_codes (str): The long code for an charges that are split
            over two grant codes
        include (list of str): A list of email addresses so send summaries to
        exclude (list of str): A list of email addresses to exclude from
            sending
        only_admin (list of str): A list of PPMS unitname of groups where only
            an admin is to be sent the summary

    Return:
        A list of Recipient objects
    """

    # api call to get the invoice - returns list of grant codes and charge
    invoice_date = (
        datetime.strptime(invoice_ref[17:25], "%Y%m%d").strftime("%d/%m/%Y")
    )
    invoice_list = get_invoice(invoice_ref)
    recipients = []
    for index, row in invoice_list.iterrows():
        bcode = row['bcode']
        for code in split_codes:
            if bcode in code:
                bcode = code
        details = get_invoice_details(bcode, invoice_ref)

        # check for training sessions in the invoice text
        # if there are training sessions store that text
        # as a new variable
        invoice_text = details.split("\n", 3)[3]
        if "Autonomous" in details and "Training" in details:
            a = invoice_text[0:invoice_text.find("Training")]
            t = invoice_text[invoice_text.find("Training"):]
            a_df = pd.read_csv(StringIO(a), sep=",")
            t_df = pd.read_csv(StringIO(t), sep=",", header=1)
            invoice = [a_df, t_df]
        else:
            invoice = [pd.read_csv(StringIO(invoice_text), sep=",")]

        sessions = sessions_from_invoice(invoice)

        autonomous_sessions = filter_by_session_type(sessions, "autonomous")
        assisted_sessions = filter_by_session_type(sessions, "assisted")
        training_sessions = filter_by_session_type(sessions, "training")

        autonomous_charge = total_charge(autonomous_sessions)
        assisted_charge = total_charge(assisted_sessions)
        training_charge = total_charge(training_sessions)

        (fee_flag, subsidy_flag) = check_for_adjustments(autonomous_sessions)

        group = get_group(invoice[0]['Group'].values[0])
        group.bcode = bcode
        print("grant code: {}".format(bcode))
        print("autonomous_charge: {}".format(autonomous_charge))
        print("assisted_charge: {}".format(assisted_charge))
        print("training_charge: {}".format(training_charge))
        print("")

        invoice_path = "invoice_{0}-{1}.html".format(invoice_ref, group.bcode)
        group.invoice = invoice_path
        #   generate an html summary
        generate_invoice.create_html(
            invoice_path,
            invoice_ref,
            invoice_date,
            group,
            autonomous_sessions,
            assisted_sessions,
            training_sessions,
            autonomous_charge,
            assisted_charge,
            training_charge,
            fee_flag,
            subsidy_flag
        )
        if group.unitlogin in only_admin:
            group.send_only_admin = True

        if include:
            if group.heademail in include:
                recipients.append(group)
        elif exclude:
            if group.heademail not in exclude:
                recipients.append(group)
        else:
            recipients.append(group)
    return recipients


def main(invoice_ref, split_codes, include, exclude, only_admin):
    if include and exclude:
        raise ValueError("Use include or exclude not both together")
    recipients = make_invoices(
        invoice_ref,
        split_codes,
        include,
        exclude,
        only_admin
    )
    if recipients:
        send_email.send(recipients, invoice_ref)


if __name__ == '__main__':
    include = ['paula.booth@kcl.ac.uk']
    exclude = []
    only_admin = ['paula.booth']
    main(
        'PPMS2-NICatKings-20180601-DRAFT',
        ["SPLIT|50|MGSRACR|50|MGS1000"],
        include,
        exclude,
        only_admin
    )
