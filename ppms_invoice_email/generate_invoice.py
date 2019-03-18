# -*- coding: utf-8 -*-

import os
from jinja2 import Environment, FileSystemLoader

PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False)


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def create_html(
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
    final_charge,
    fee_flag,
    subsidy_flag
):

    context = {
        'invoice_ref': invoice_ref,
        'invoice_date': invoice_date,
        'group': group,
        'autonomous_sessions': autonomous_sessions,
        'training_sessions': training_sessions,
        'autonomous_charge': autonomous_charge,
        'assisted_charge': assisted_charge,
        'training_charge': training_charge,
        'total': final_charge,
        'fee_flag': fee_flag,
        'subsidy_flag': subsidy_flag
    }

    with open(invoice_path, 'w') as f:
        html = render_template('basic_invoice_template.html', context)
        f.write(html)


def main():
    create_html()


if __name__ == "__main__":
    main()
