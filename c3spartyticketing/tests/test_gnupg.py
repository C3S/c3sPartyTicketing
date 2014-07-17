# -*- coding: utf-8 -*-
import os
import unittest
#import shutil
from pyramid import testing

from c3spartyticketing.models import DBSession
from c3spartyticketing.scripts import initializedb


class TestGnuPG(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        #import pdb; pdb.set_trace()
        #os.remove('c3spartyticketing.db')
        #DBSession.remove()
        #self.session = _initTestingDB()
        #initializedb.main()

    def tearDown(self):
        DBSession.remove()
        #shutil.rm('c3spartyticketing.db')
        testing.tearDown()

    def test_encrypt_with_gnupg_w_umlauts(self):
        """
        test if unicode input is acceptable and digested
        """
        from c3spartyticketing.gnupg_encrypt import encrypt_with_gnupg
        result = encrypt_with_gnupg(u'fuck the umläuts')
        #print ("the result: " + str(result))
        self.assertTrue('-----BEGIN PGP MESSAGE-----' in str(result))
        self.assertTrue('-----END PGP MESSAGE-----' in str(result))

    def test_encrypt_with_gnupg_import_key(self):
        """
        test if encryption produces any result at all
        """
        from c3spartyticketing.gnupg_encrypt import encrypt_with_gnupg
        result = encrypt_with_gnupg('foo')
        #print ("the result: " + str(result))
        self.assertTrue('-----BEGIN PGP MESSAGE-----' in str(result))
        self.assertTrue('-----END PGP MESSAGE-----' in str(result))
