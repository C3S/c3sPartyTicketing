# -*- coding: utf-8 -*-
import unittest
from pyramid import testing


class TestGnuPG(unittest.TestCase):
    """
    Test some utility functions used to interact with GnuPG.

    * encrypt some lines
    * encrypt some unicode lines (with umlauts)
    * import key
    """
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_encrypt_with_gnupg_w_umlauts(self):
        """
        test if unicode input is acceptable and digested
        """
        from c3spartyticketing.gnupg_encrypt import encrypt_with_gnupg
        result = encrypt_with_gnupg(u'fuck the umläuts')
        self.assertTrue('-----BEGIN PGP MESSAGE-----' in str(result))
        self.assertTrue('-----END PGP MESSAGE-----' in str(result))

    def test_encrypt_with_gnupg_import_key(self):
        """
        test if encryption produces any result at all
        """
        from c3spartyticketing.gnupg_encrypt import encrypt_with_gnupg
        result = encrypt_with_gnupg('foo')
        self.assertTrue('-----BEGIN PGP MESSAGE-----' in str(result))
        self.assertTrue('-----END PGP MESSAGE-----' in str(result))
