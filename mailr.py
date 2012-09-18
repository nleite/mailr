"""
module that hodls the classes for the manipulation of Mail email messages (emlx files)
"""
import os
from os import path
import email
import base64
import quopri
from optparse import OptionParser
import sys
from bson.errors import InvalidStringData
from bs4 import BeautifulSoup as BS
from HTMLParser import HTMLParseError

CHARSET = 'charset'
CONTENT_TYPE = 'Content-Type'
CONTENT_TRANSFER_ENCODING = 'Content-Transfer-Encoding'

def decode(encode_type, message):
    if encode_type == 'base64':
        return base64.decodestring(message)
    if encode_type == 'quoted-printable':
        return quopri.decodestring(message)
    else:
        return message

def process_charset(part):
    """
    For a given multipart message we try to collect the charset of the payload text
    """
    content_type = part.get(CONTENT_TYPE,'')
    charset = 'utf-8'
    if CHARSET in content_type:
        pos = content_type.index(CHARSET)
        #exclude the initial position of the '"' char
        b = content_type.index('"', pos) + 1
        #get the position of char '"' after begin position
        e = content_type.index('"', b)
        charset = content_type[b:e]
    return charset

def fetch_text(part):
    """
    checks if the current part has text and returns it in the correct format
    """
    text = ''
    if part.get_content_type().startswith('text'):
        payload = part.get_payload()
        if part.has_key(CONTENT_TRANSFER_ENCODING ):
            payload = decode( part[CONTENT_TRANSFER_ENCODING], payload )
        if part.get_content_type() == 'text/html':
            #html text
            try:
                soup = BS(payload, features='html5lib')
                text = soup.get_text()
            except HTMLParseError, e:
                return ''
        if part.get_content_type() == 'text/plain':
            try:
                charset = process_charset(part)
                text = payload.decode(charset)
            except UnicodeError, e:
                #import ipdb;ipdb.set_trace()
                #if it does not coupe with the mail charset lets try latin1
                text = payload.decode('latin1')

    return text


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
        dic = dict(dic.items())
        i=1
        parts = []
        for part in self.content.walk():
            d = dict(part.items())
            text = fetch_text(part)
            if text != '':
                d['text'] = text
            parts.append(d)
        if len(parts) > 0:
            dic['parts'] = parts
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
    #import ipdb;ipdb.set_trace()
    for mail in mailbox.next():
        d = mail.parse()
        try:
            collection.save(d)
        except InvalidStringData:
            import ipdb;ipdb.set_trace()
            dir(d)


def main():

    optparser = OptionParser()
    optparse.add_option('-m', '--host', dest='host', help='database host machine', default='localhost')
    optparse.add_option('-d', '--databasename', dest='databasename', help='database name', default='test')
    optparse.add_option('-c', '--collectionname', dest='collectionname', help='collection name', default='mails')
    optparse.add_option('-f', '--mailfolder', dest='collectionname', help='collection name', default='mails')

    (options, args) = optparse.parse()
    #Initiate mongodb connection
    mongo = Connection(options.host)
    #Load mailbox dir
    mailbox = MailBox(options.dir)

    load_data(mongo, mailbox, options.databasename, options.collectionname)
    print "Documents: %d" % (mongo[options.databasename][options.collectionname].count())

if __name__ == '__main__':
    main()


