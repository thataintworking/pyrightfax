# Port of the RightFax Java API
# Author: Ron Smith, ThatAintWorking.com
# Date: 12/7/2011

# NOTE: RightFax uses a non-standard base64 encoding scheme so we cannot use the python library base64 functions

from cStringIO import StringIO
from contextlib import closing
import logging
import urllib2
from constants import *
from exceptions import RFEncodingException



RF_BASE64 = (
    'A','B','C','D','E','F','G','H','I','J',
    'K','L','M','N','O','P','Q','R','S','T',
    'U','V','W','X','Y','Z','a','b','c','d',
    'e','f','g','h','i','j','k','l','m','n',
    'o','p','q','r','s','t','u','v','w','x',
    'y','z','0','1','2','3','4','5','6','7',
    '8','9','+','/')


def b64_encode(data):
    if not data: return ''
    with closing(StringIO()) as encout:
        i = len(data)
        j = k = i1 = j1 = 0
        for k1 in range(0, i, 3):
            j = ord(data[k1])
            i1 = 1
            if k1 + 1 >= i: break
            k = ord(data[k1 + 1])
            i1 = 2
            if k1 + 2 >= i: break
            b0 = ord(data[k1 + 2])
            j1 += 4
            encout.write(RF_BASE64[(j & 252) >> 2])
            encout.write(RF_BASE64[(j & 3) << 4 | (k & 240) >> 4])
            encout.write(RF_BASE64[(k & 15) << 2 | (b0 & 192) >> 6])
            encout.write(RF_BASE64[b0 & 63])
            if j1 > 75:
                encout.write('\n')
                j1 = 0
            i1 = 0
            j = 0
            k = 0

        if i1 == 1:
            k = 0
            encout.write(RF_BASE64[(j & 252) >> 2])
            encout.write(RF_BASE64[(j & 3) << 4 | (k & 240) >> 4])
            encout.write('==')
        elif i1 == 2:
            l = 0
            encout.write(RF_BASE64[(j & 252) >> 2])
            encout.write(RF_BASE64[(j & 3) << 4 | (k & 240) >> 4])
            encout.write(RF_BASE64[(k & 15) << 2 | (l & 192) >> 6])
            encout.write('=')
        encout.write('\n')
        return encout.getvalue()


def b64_encode_file(fname):
    with file(fname, 'rb') as fin:
        data = fin.read()
    return b64_encode(data)


def b64_encode_url(url):
    req = urllib2.Request(url=url)
    with closing(urllib2.urlopen(req)) as uin:
        data = uin.read()
    return b64_encode(data)


def mime_encode(xml, attachments):
    with closing(StringIO()) as mime:
        mime.write('This is a multi-part message in MIME format.\r\n')
        mime.write(MIME_BOUNDRY_START)
        mime.write('Content-Type: text/xml; charset=us-ascii\r\n')
        mime.write('Content-Transfer-Encoding: 7bit\r\n')
        mime.write('\r\n')
        mime.write(xml)

        for attachment in attachments:
            if _mime_attachment_is_url(attachment):
                _logger().debug('Attachment (%s) is a URL path.' % attachment)
                encoded = b64_encode_url(attachment)
            else:
                _logger().debug('Attachment (%s) is a file path.' % attachment)
                encoded = b64_encode_file(attachment)
            if not encoded:
                raise RFEncodingException('Encoding failed for attachment (%s).' % attachment)

            file_name = _mime_attachment_file_name(attachment)
            content_type = _mime_attachment_content_type(file_name)

            mime.write(MIME_BOUNDRY_ATTACH)
            mime.write( 'Content-Type: %s; name=%s\r\n' % (content_type, file_name))
            mime.write('Content-Transfer-Encoding: base64\r\n')
            mime.write('\r\n')
            mime.write(encoded)
            mime.write('\r\n')

        mime.write(MIME_BOUNDRY_END)
        return mime.getvalue()


def _mime_attachment_is_url(attachment):
    a = attachment.lower().strip()
    return a.startswith('http') or a.startswith('ftp')


def _mime_attachment_file_name(attachment):
    last_slash = attachment.rfind('\\')
    if last_slash >= 0:
        return attachment[last_slash+1:].strip()
    last_slash = attachment.rfind('/')
    if last_slash >= 0:
        return attachment[last_slash+1:].strip()
    return attachment


def _mime_attachment_content_type(attachment):
    last_dot = attachment.rfind('.')
    if last_dot > 0:
        ext = attachment[last_dot+1:].lower().strip()
        if ext == 'doc' or ext == 'rtf':
            return 'application/msword'
        elif ext == 'xls':
            return 'application/msexcel'
        elif ext == 'ppt':
            return 'application/msppt'
        elif ext == 'ps' or ext == 'eps':
            return 'application/postscript'
    return 'application/octet-stream'

def _logger():
    return logging.getLogger('rightfax.encoders')