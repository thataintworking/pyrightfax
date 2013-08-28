# Port of the RightFax Java API
# Author: Ron Smith, ThatAintWorking.com
# Date: 12/7/2011

import logging
import urllib2
from urlparse import urljoin
import xml.sax
from contextlib import closing
from constants import *
from exceptions import RFInvalidOpException, RFUnexpectedResponseException, RFNoDataException


class Transporter(object):

    RFISAPIDLL = 'rfwebcon.dll'

    _logger = logging.getLogger('rightfax.Transporter')

    def __init__(self, url, content_type, avt_type):
        self.url = url
        self.content_type = content_type
        self.avt_type = avt_type

    def do_transport(self, data):
#        if self._logger.getEffectiveLevel() == logging.DEBUG:
#            with file('transport.out', 'w') as transout:
#                transout.write(data)
#                transout.flush()

        req = urllib2.Request(url=self._full_url(self.url), data=data, headers=self._make_headers(data))
        with closing(urllib2.urlopen(req)) as url:
            resp = url.read()
            
        Transporter._logger.debug('RETURN XML:\n%s' % resp)
        return resp

    def do_transport_ex(self, data):
        resp = self.do_transport(data)
        if not resp or not resp.startswith('<?xml'):
            raise RFUnexpectedResponseException('Unexpected response from server.')
        handler = _ResponseHandler()
        xml.sax.parseString(resp, handler)
        return handler.status_list

    def _make_headers(self, data):
        headers = dict()

        if self.content_type == CONTENT_MIME:
            headers['Content-type'] = 'multipart/mixed; boundary="MIMEBOUNDRY"'
        else:
            headers['Content-type'] = 'text/xml'

        if self.avt_type == AVT_SUBMIT:
            headers['X-AVT-Method'] = 'submit'
        elif self.avt_type == AVT_QUERY:
            headers['X-AVT-Method'] = 'query'
        elif self.avt_type == AVT_ACTION:
            headers['X-AVT-Method'] = 'action'
        else:
            raise RFInvalidOpException('Invalid AVT Type: %d.' % self.avt_type)

        headers['Content-length'] = str(len(data))
        headers['Connnection'] = 'keep-alive'
        headers['Accept'] = 'text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2'
        
        return headers

    def _full_url(self, url):
        if not url:
            raise RFNoDataException('URL not specified.')
        url = url.lower()
        dllidx = url.find(Transporter.RFISAPIDLL)
        rfxidx = url.find('rfxml')
        if dllidx < 0:
            if rfxidx < 0:
                url = urljoin(url, 'rfxml/')
            url = urljoin(url, Transporter.RFISAPIDLL)
        else:
            if rfxidx < 0:
                url = urljoin(url[0:dllidx], 'rfxml/')
                url = urljoin(url, Transporter.RFISAPIDLL)
        return url


class _ResponseHandler(xml.sax.handler.ContentHandler):
    """SAX handler for parsing status query response"""

    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self.status_list = None
        self.status = None
        self.status_parm = None
        self.status_tag = None

    def startDocument(self):
        self.status_list = list()

    def startElement(self, name, attrs):

        if not self.status and 'unique_id' in attrs.getNames():
            self.status_tag = name
            self.status = { 'fax_id' : attrs.getValue('unique_id') }
        elif self.status and name in ('STATUS_CODE','STATUS_MSG','ERROR_CODE','SEND_TIME','SEND_DATETIME','SEND_CHANNEL'):
            self.status_parm = name.lower()
            self.status[self.status_parm] = ''

    def endElement(self, name):
        if self.status_tag == name:
            self.status_list.append(self.status)
            self.status = None
            self.status_tag = None
        elif self.status_parm == name.lower():
            self.status_parm = None

    def characters(self, content):
        if self.status and self.status_parm:
            self.status[self.status_parm] += content

