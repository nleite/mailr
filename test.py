from pymongo import Connection
from mailr import MailBox, load_data, process_charset, CHARSET, CONTENT_TYPE, decode, main
from mockito import *
import base64
import sys

class TestMailr(object):

    def setUp(self):
        self.mongo = Connection('localhost')
        self.databasename = 'test'
        self.collectioname = 'mails_test'
        self.mail_dir = 'test_data'
        self.part = mock()


    def tearDown(self):
        self.mongo.drop_database(self.databasename)

    def test_load_data(self):

        mailbox = MailBox(self.mail_dir)

        load_data(self.mongo, mailbox, self.databasename, self.collectioname)


    def test_process_charset(self):
        expected = 'utf-8'
        when(self.part).get(CONTENT_TYPE, '').thenReturn('text/plain; charset="utf-8"')
        actual = process_charset(self.part)
        assert expected == actual

    def test_process_charset_ascii(self):
        expected = 'ascii'
        when(self.part).get(CONTENT_TYPE, '').thenReturn('text/plain; charset="ascii"')
        actual = process_charset(self.part)
        assert expected == actual


    def test_process_text(self):
        data = 'my simple milde text'



    def test_decode(self):
        encode_type = 'base64'
        expected = 'this message should not be read by humans'
        message = base64.encodestring(expected)

        actual = decode(encode_type, message)
        assert expected == actual


    def test_main(self):
        sys.argv.append( ['-f', '/var/tmp/', '-d','bitiching', '-c', 'junk'])
        main()
