"""
module that hodls the classes for the manipulation of Mail email messages (emlx files)
"""
import os
from os import path
import email
import base64
from optparse import OptionParser
import sys

def decode(encode_type, message):
    if encode_type == 'base64':
        return base64.decodestring(message)
    else:
        return message

class Mail(object):
    """
    Holds the reference for an email file and parses the content into mongo document
    """

    def __init__(self, filepath):
        """
        Holds the opened file reference for read
        """
        self.path = filepath


    def parse(self):
        """
        Parses the email file into a dictornary
        """
        dic = {}
        fh = open(self.path, 'r')
        nbytes = int(fh.readline().strip())
        self.content = email.message_from_string(fh.read( nbytes))

        for part in self.content.walk():
            dic = dict(dic.items() + part.items())
            payload = ''
            if part.get_content_type() == 'text/plain':
                payload = part.get_payload()
                if part.has_key( 'Content-Transfer-Encoding' ):
                    payload = decode( part['Content-Transfer-Encoding'], payload )
                dic['text_plain'] = payload
        return dic

    def get_content(self):
        return self.content


class MailBox(object):
    """
    Email files class holder
    """

    def __init__(self, mailboxfilepath):
        """
        Initialized with a path of the email files
        """
        self.path = mailboxfilepath

    def next(self):
        """
        Generator that provides the next email listed on the mail box
        """
        files = []
        for (d, ds, fls) in os.walk(self.path):
            for x in fls:
                if x.endswith('emlx'):
                    yield Mail( path.join( d, x) )



def load_data( mongo, mailbox, databasename='test', collectionname='mails'):
    collection = mongo[databasename][collectionname]
    import ipdb;ipdb.set_trace()
    for mail in mailbox.next():
        d = mail.parse()
        collection.save(d)

def main():

    optparser = OptionParser()
    optparse.add_option('-m', '--host', dest='host', help='database host machine', default='localhost')
    optparse.add_option('-d', '--databasename', dest='databasename', help='database name', default='test')
    optparse.add_option('-c', '--collectionname', dest='collectionname', help='collection name', defautl='mails')
    optparse.add_option('-f', '--mailfolder', dest='collectionname', help='collection name', defautl='mails')

    (options, args) = optparse.parse()
    #Initiate mongodb connection
    mongo = Connection(options.host)
    #Load mailbox dir
    mailbox = MailBox(options.dir)

    load_data(mongo, mailbox, options.databasename, options.collectionname)
    print "Documents: %d" % (mongo[options.databasename][options.collectionname].count())

if __name__ == '__main__':
    main()


