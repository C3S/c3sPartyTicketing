# -*- coding: utf-8 -*-

from c3spartyticketing.models import PartyTicket

import os
import qrcode
import subprocess
import tempfile
import random
import string


def make_random_string():
    """
    used as email confirmation code
    """
    randomstring = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits
        ) for x in range(10))
    # check if confirmation code is already used
    #print(
    #    "checking if ex. conf"
    #    ".code: %s" % PartyTicket.check_for_existing_confirm_code(
    #        randomstring))
    while (PartyTicket.check_for_existing_confirm_code(randomstring)):
            # create a new one, if the new one already exists in the database
            #print("generating new code")
            randomstring = make_random_string()  # pragma: no cover

    return randomstring


def ticket_code_prefix(_ticket):
    '''
    produce a code to be printed on the tickets,
    incorporating the barcamp and assembly attendance options
    and membership type
    '''
    code = u''
    # gv attendance
    if _ticket.ticket_gv_attendance == 1:
        code += 'A'
    elif _ticket.ticket_gv_attendance == 2:
        code += 'R'
    elif _ticket.ticket_gv_attendance == 3:
        code += '0'
    # barcamp attendance
    if _ticket.ticket_bc_attendance:
        code += 'B'
    else:
        code += '0'
    # membership status
    if 'normal' in _ticket.membership_type:
        code += 'N'
    else:
        code += 'I'
    return code


def ticket_code_suffix(_ticket):
    '''
    produce a code to be appended to ticket code
    showing helper, guest, eichhoernchen
    '''
    code = u''
    #if _ticket.guestlist ...  # not implemented yet, see #628
    return code


def get_ticket_code(_ticket):
    code = (
        ticket_code_prefix(_ticket)
        + _ticket.email_confirm_code
        + ticket_code_suffix(_ticket)
    )
    return code


def make_qr_code_pdf(_ticket, _url):
    """
    this function creates a QR-Code PDF for whatever purpose

    append .name to the result to get the filename
    """

    _img = qrcode.make(_url)  # the qr-code image, unsaved
    _ticket_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'pdftk/C3S_Ticket_BCGV.pdf'
    )
    use_pdf = {
        'bcgv': _ticket_path
    }

    _pdf_to_use = use_pdf['bcgv']

    #import os.path
    #print(u'_pdf_to_use %s') % _pdf_to_use
    #print(u'isfile: %s') % os.path.isfile(_pdf_to_use)

    tmp_img = tempfile.NamedTemporaryFile()  # for the qr-code
    tmp_pdf = tempfile.NamedTemporaryFile()  # converted to pdf

    _img.save(tmp_img)  # save the qr-code to tempfile

    #print(u'tmp_img %s') % tmp_img.name
    #print(u'isfile: %s') % os.path.isfile(tmp_img.name)

    tmp_pdf.name = tmp_pdf.name + '.pdf'  # rename so convert knows what to do
    #
    # resize/arrange the code on the page so it aligns nicely
    # when combined with ticket PDF
    #
    _caption_code = str(
        'Caption:' + get_ticket_code(_ticket)
    )
    subprocess.check_call(
        ['convert',
         '-page',
         'A4+340+470',  # A4, push image right (x) and up (y)
         tmp_img.name,
         '-resize', '245x245',
         '-format', 'pdf',
         '-size', '320x50',
         tmp_pdf.name])
    tmp_pdf.seek(0)
    #
    # stamp the qr-code onto the ticket
    #
    tmp_ticket = tempfile.NamedTemporaryFile()
    subprocess.check_call(
        ['pdftk', _pdf_to_use,
         'stamp', tmp_pdf.name,  # use qr-code as stamp
         'output', tmp_ticket.name
         ]
    )
    #
    # make image with alphanum code
    #
    tmp_code = tempfile.NamedTemporaryFile()
    tmp_code.name = tmp_code.name + '.pdf'
    # convert -size 320x50 caption:'ABCDEFGHIJ' CODE.png
    subprocess.check_call(
        ['convert',
         '-size', '220x50',
         '-page',
         'A4+364+440',  # A4, push image right (x) and up (y)
         _caption_code,  # 'caption:ABCDEFGHIJ',
         #'caption:ABCDEFGHIJ',
         tmp_code.name]
    )
    #
    # stamp the alphanum code onto the ticket
    #
    tmp_ticket2 = tempfile.NamedTemporaryFile()
    subprocess.check_call(
        ['pdftk', tmp_ticket.name,  # input
         'stamp', tmp_code.name,  # use code as stamp
         'output', tmp_ticket2.name
         ]
    )
    return tmp_ticket2


def make_qr_code_pdf_mobile(_ticket, _url):
    """
    this function creates a QR-Code PDF for mobile_devices

    append .name to the result to get the filename
    """
    _img = qrcode.make(_url)  # the qr-code image, unsaved

    tmp_img = tempfile.NamedTemporaryFile()  # for the qr-code
    tmp_pdf = tempfile.NamedTemporaryFile()  # converted to pdf

    _img.save(tmp_img)  # save the qr-code to tempfile
    tmp_pdf.name = tmp_pdf.name + '.pdf'  # rename so convert knows what to do

    # resize/arrange the code on the page so it aligns nicely
    # when combined with ticket PDF
    _caption_code = str(
        'caption:' + get_ticket_code(_ticket)
    )
    subprocess.check_call(
        ['convert',
         tmp_img.name,
         '-format', 'pdf',
         '-size', '320x50',
         tmp_pdf.name])
    tmp_pdf.seek(0)
    # make image with alphanum code
    tmp_code = tempfile.NamedTemporaryFile()
    tmp_code.name = tmp_code.name + '.pdf'
    # convert -size 320x50 caption:'ABCDEFGHIJ' CODE.png
    subprocess.check_call(
        ['convert',
         '-size', '500x90',
         '-page',
         'A4+80+0',  # A4, push image right (x) and up (y)
         _caption_code,
         tmp_code.name]
    )
    # stamp the alphanum code onto the ticket
    tmp_ticket2 = tempfile.NamedTemporaryFile()
    subprocess.check_call(
        ['pdftk', tmp_pdf.name,  # input
         'stamp', tmp_code.name,  # use code as stamp
         'output', tmp_ticket2.name
         ]
    )
    return tmp_ticket2
