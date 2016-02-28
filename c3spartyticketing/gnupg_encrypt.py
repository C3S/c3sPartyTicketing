#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module holds GnuPG functionality for c3sPartyTicketing.

GnuPG is used:

* to encrypt email to staff when new tickets are booked
* for data export (e.g. CSV)
"""
#
# you need python-gnupg, so
# bin/pip install python-gnupg

import gnupg
import tempfile
import shutil

DEBUG = False
# DEBUG = True


def encrypt_with_gnupg(data):
    """
    This function encrypts "data" with gnupg.

    Returns:
        multiline strings containing GnuPG messages
    """
    # we use a temporary folder to store stuff
    keyfolder = tempfile.mkdtemp()
    if DEBUG:  # pragma: no cover
        print(keyfolder)

    gpg = gnupg.GPG(gnupghome=keyfolder)
    gpg.encoding = 'utf-8'

    # check if we have the membership key
    list_of_keys = gpg.list_keys()
    if DEBUG:  # pragma: no cover
        print("=== the list of keys: " + repr(list_of_keys))

    if 'C3S-Yes!' not in str(list_of_keys):
        # open and read key file
        # reading public key
        pubkey_content = """
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v2.0.22 (GNU/Linux)

mQENBFBIqlMBCADR7hxvDnwJkLgXU3Xol71eRkdNCAdIDnXQq/+Bmn5rxcJcXzNK
DyibSGbVVpwMMOIiVuKxM66QdlvBm+2/QUdD/kdcMTwRBFqP40N9T+vaIVDpit4r
6ZH1w8QD6EJTL0wbtmIkdAYMhYd0k4wDJ+xOcfx/VINiwhS5/DT38jimqmkaOEzs
DqzbBBogdZ+Tw+leC+D9JkSzGRjwO+UzUxjw4kdib9KbSppTbjv7HdL+Pn1y0ACd
2ELZjTumqQzQi19WFENNhMaRHlUU5iGp9sLbKUN0GtgxGYIs85QNXH/5/0Qr2ZjH
2/yZCyyWzZR0efut6WthcxFNb4OMDs056v5LABEBAAG0KUMzUyBZZXMhIChodHRw
Oi8vd3d3LmMzcy5jYykgPHllc0BjM3MuY2M+iQE+BBMBAgAoAhsDBgsJCAcDAgYV
CAIJCgsEFgIDAQIeAQIXgAUCVfFpxQUJB4SXzQAKCRBx9rqRzdKBEGp6B/9jblJX
+Kn4z6H8f85DlUT+cXqzi+rwI553726fWln7RnpgSLzcHKNsEAPO8lFs4MfvNMG9
KlCgWQ0mB2lZgJ17P3aidJ1qgv4fBc3DhlDVGcmbXfY2ifVa0DIziFoLQLpXelil
wM5eU3m34e9SfN+BmTFIQ+tQP3fl8/FKWkHcMxaPRPwmpXKhp9NvhYx00RDT3uJH
P4yoLVk3gVNVfLV35/H48CvdXE7bQDVRZxFLEMvKHOLOnxhR6dg1WscOxcGzjTxC
+ergK2LOGf8YYT3MU3eDFEqrKhkJHsuMRqwr+aH4i3JCCpMOwsSLPzRy9YG8SjTD
bbxbf2k+cRyUyN2VuQENBFBIqlMBCACoys54nxs3nrRcUkwFG0lp3L8N0udCzckI
iVgU/1SdgbfAD9rnRdKv4UE/uvn7MkfyO8V2V2OZANu8ZL+dtjmi6DWS2iTEXOl6
Mn6j0FyvZNDe6scvahPDjWYnrjOwrNy6FC5Y4eAyHTprABioZgfwNkonK5Oh0pXL
Rkr5z00lHjnkxYwyoFoMa3T7j7sxS0t3bkYZxETMCd+5YqDyt7fPEZ2sPugi1oqV
U/ytADNgEpjkzUhl4iWYYkk8RlQ8MFWVWEJd34HO6iOT+Pz6A9anuRbEqYCWYlHx
M3wBc2Klv/heN0yz5ldZVx1ug0/eLwexNecJOTpy2eQYjVLP/BwTABEBAAGJASUE
GAECAA8CGwwFAlXxad0FCQeEl80ACgkQcfa6kc3SgRDLxwf5AZ20HfLw3zryIh0j
E5/GuYw18z396sY7+MmBaYSklazvu4aIPXZhLRMWjrRf7BuqmJgpxt+C9FDhH/41
hKoJW4FVu/qLqrEdgrOsPrujf2dNa2SqfVUhJyMOAWifjlm7669ItlMEO5nBXgHD
w11FO4vFhEnYtyANABFIOkmHQyf7Z7VfSjZfrcpnY4TXHmibn7uOY/ZcaaVtXsuv
VlO6byBzfMYAHo6Zlpo1gNCaiEXzDg2ouarvAGo/ngMJBSLhm3a1KrgiYKJ54yFz
/uAvSZ0NtUWOhIlghX5/AKq6GMIOJWtRVazVr1aZAHL+CzUwTqHtGvJ2JkaRH0Gm
kViZMg==
=+viX
-----END PGP PUBLIC KEY BLOCK-----
"""

        # import public key
        gpg.import_keys(pubkey_content)
    else:
        if DEBUG:  # pragma: no cover
            print("=== not imported: key already known")
        pass

    if DEBUG:  # pragma: no cover
        print("===============================================")
        print("list_keys(): {}".format(gpg.list_keys()))
        print("===============================================")

    # prepare
    to_encode = data

    # if DEBUG:  # pragma: no cover
    #    print("encrypt_with_gnupg: data: %s") % data
    #    print("encrypt_with_gnupg: type(data): %s") % type(data)
    #    print("type of to_encode: %s") % type(to_encode)

    if isinstance(to_encode, unicode):
        # print("type is unicode")
        to_encrypt = to_encode.encode(gpg.encoding)
    else:
        to_encrypt = to_encode
    # elif isinstance(to_encode, str):
    #    print("type was string")
    #    to_encrypt = to_encode.encode(gpg.encoding)
    #    print("type is now %s") % type(to_encrypt)
    # else:
    #    print("type is neither str nor unicode: %s") % type(to_encode)

    if DEBUG:  # pragma: no cover
        print "len(to_encrypt): " + str(len(str(to_encrypt)))
        # print("encrypt_with_gnupg: to_encrypt: %s") % to_encrypt
        print("encrypt_with_gnupg: type(to_encrypt): %s") % type(to_encrypt)

    # encrypt
    encrypted = gpg.encrypt(
        to_encrypt,
        '89FC70ECCAD4487972D8924D71F6BA91CDD28110',  # key fingerprint
        always_trust=True)

    if DEBUG:  # pragma: no cover
        # print("encrypt_with_gnupg: encrypted: %s") % encrypted
        print("encrypt_with_gnupg: type(encrypted): %s") % type(encrypted)
        print(
            "encrypt_with_gnupg: type(encrypted.data): %s"
        ) % type(
            encrypted.data)
        # print "encrypted: " + str(encrypted)
        # print "len(encrypted): " + str(len(str(encrypted)))
        print ("========================================== GNUPG END")
    shutil.rmtree(keyfolder)

    return encrypted.data


if __name__ == '__main__':  # pragma: no coverage

    my_unicode_text = u"""
    --                                      --
    --  So here is some sample text.        --
    --  With umlauts: öäß        --
    --  I want this to be encrypted.        --
    --  And then maybe send it via email    --
    --                                      --
    """
    result = encrypt_with_gnupg(my_unicode_text)
    print result

    my_string = """
    --                                      --
    --  So here is some sample text.        --
    --  With out umlauts.                   --
    --  I want this to be encrypted.        --
    --  And then maybe send it via email    --
    --                                      --
    """
    result = encrypt_with_gnupg(my_string)
    print result
