# -*- coding: utf-8 -*-


class BaseSession:
    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def round_final_amount(self):
        return (
            "{0:.2f}".format(
                int((self.final_amount * 100) + 0.5) / float(100)
            )
        )


class TrainingSession(BaseSession):
    """Class which encapsulates training sessions"""
    def __init__(self, duration, **kwargs):
        self.duration = duration
        super().__init__(**kwargs)


class Session(BaseSession):
    """Class which encapsulates both autonomous and assisted sessions."""

    def __init__(self, booked_time, used_time, notes, fee, subsidy, **kwargs):
        self.booked_time = booked_time
        self.used_time = used_time
        self.notes = notes
        self.fee = fee
        self.subsidy = subsidy
        if not isinstance(notes, str):
            self.notes = ""
        # if "cancelled too late" in self.notes:
        #     self.notes = ""
        super().__init__(**kwargs)
        self.initial_amount = self.final_amount - self.fee + self.subsidy


def sessions_from_invoice(invoice_list):
    sessions = []
    for invoice in invoice_list:
        for index, row in invoice.iterrows():
            kwargs = {
                'session_type': row['Session Type'],
                'session_ref': row['Reference'],
                'user': row['User'],
                'system_type': row['System Type'],
                'system': row['System'],
                'date': row['Date'],
                'start_time': row['Start time'],
                'final_amount': row['Final Amount']
            }

            if (
                ("autonomous" in row['Session Type']) or
                ("assisted" in row['Session Type'])
            ):
                sessions.append(
                    Session(
                        row['Duration (booked)'],
                        row['Duration (used)'],
                        row['Notes'],
                        row['Fee'],
                        row['Subsidy'],
                        **kwargs
                    )
                )
            elif "training" in row['Session Type']:
                sessions.append(
                    TrainingSession(
                        row['Duration'],
                        **kwargs
                    )
                )
    return sessions


def filter_by_session_type(sessions, session_type):
    filtered = []
    for session in sessions:
        if session_type in session.session_type:
            filtered.append(session)
    return filtered


def total_charge(sessions):
    total = 0.0
    for session in sessions:
        total += session.final_amount
    total = int((total * 100) + 0.5) / float(100)
    return "{0:.2f}".format(total)


def final_total(autonomous, assisted, training):
    total = 0.0
    for auto in autonomous:
        total += auto.final_amount

    for assit in assisted:
        total += assit.final_amount

    for train in training:
        total += train.final_amount

    total = int((total * 100) + 0.5) / float(100)
    return "{0:.2f}".format(total)


def check_for_adjustments(sessions):
    fee_flag = False
    subsidy_flag = False
    for session in sessions:
        if session.fee > 0.0:
            fee_flag = True
        if session.subsidy > 0.0:
            subsidy_flag = True
    return (fee_flag, subsidy_flag)

