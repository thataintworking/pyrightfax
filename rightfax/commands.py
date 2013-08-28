# Port of the RightFax Java API
# Author: Ron Smith, ThatAintWorking.com
# Date: 12/7/2011

from contextlib import closing

import logging
from cStringIO import StringIO

from constants import *
from encoders import mime_encode
from transport import Transporter
from exceptions import RFNoDataException
from components import Document

class FaxCommand(object):

    _logger = logging.getLogger('rightfax.FaxCommand')

    def __init__(self, debug=False, target_url=None):
        self.debug = debug
        self.target_url = target_url

    def get_xml(self):
        with closing(StringIO()) as xmlbuf:
            xmlbuf.write('<?xml version="1.0" ?>\r\n')
            self.append_xml(xmlbuf)
            return xmlbuf.getvalue()

    def append_xml(self, xmlbuf):
        pass # subclass should override this method

    def send_data(self, data, content_type, avt_type, target_url=None):
        if not data:
            raise RFNoDataException('No data provided to send.')
        if target_url:
            url = target_url
        else:
            url = self.target_url
        transporter = Transporter(url, content_type, avt_type)
        resp_str = transporter.do_transport(data)
        FaxCommand._logger.info('Message transported to RightFax Server.')
        return resp_str

    def send_data_ex(self, data, content_type, avt_type, target_url=None):
        if not data:
            raise RFNoDataException('No data provided to send.')
        if target_url:
            url = target_url
        else:
            url = self.target_url
        transporter = Transporter(url, content_type, avt_type)
        resp_list = transporter.do_transport_ex(data)
        if resp_list:
            FaxCommand._logger.info('Message successfully transported to RightFax Server.')
        else:
            FaxCommand._logger.warn('Message failed transport to RightFax Server.')
        return resp_list


class FaxAction(FaxCommand):

    def __init__(self, debug=False, target_url=None, actions=None):
        super(self.__class__, self).__init__(debug, target_url)
        if actions:
            self.actions = actions
        else:
            self.actions = []

    def add_action(self, action):
        self.actions.append(action)

    def append_xml(self, xmlbuf):
        if not self.actions:
            raise RFNoDataException('No actions were provided.')
        xmlbuf.write('<XML_FAX_ACTION xmlns="x-schema:../schemas/XML_FAX_ACTION_schema.xml">\r\n')
        for action in self.actions:
            action.append_xml(xmlbuf)
        xmlbuf.write('</XML_FAX_ACTION>\r\n')

    def submit(self, xml=None):
        if xml:
            return self.send_data_ex(xml, CONTENT_TEXT, AVT_ACTION)
        else:
            return self.send_data_ex(self.get_xml(), CONTENT_TEXT, AVT_ACTION)

    def submit_ex(self, xml=None):
        if xml:
            return self.send_data(xml, CONTENT_TEXT, AVT_ACTION)
        else:
            return self.send_data(self.get_xml(), CONTENT_TEXT, AVT_ACTION)


class FaxQuery(FaxCommand):

    def __init__(self, debug=False, target_url=None, queries=None):
        super(FaxQuery, self).__init__(debug, target_url)
        if queries:
            self.queries = queries
        else:
            self.queries = []

    def add_query(self, query):
        self.queries.append(query)

    def append_xml(self, xmlbuf):
        if not self.queries:
            raise RFNoDataException('No queries were provided.')
        xmlbuf.write('<XML_FAX_QUERY xmlns="x-schema:../schemas/XML_FAX_QUERY_schema.xml">\r\n')
        xmlbuf.write('\t<QUERIES>\r\n')
        for query in self.queries:
            query.append_xml(xmlbuf)
        xmlbuf.write('\t</QUERIES>\r\n')
        xmlbuf.write('</XML_FAX_QUERY>\r\n')

    def submit(self, xml=None):
        if xml:
            return self.send_data_ex(xml, CONTENT_TEXT, AVT_QUERY)
        else:
            return self.send_data_ex(self.get_xml(), CONTENT_TEXT, AVT_QUERY)

    def submit_ex(self, xml=None):
        if xml:
            return self.send_data(xml, CONTENT_TEXT, AVT_QUERY)
        else:
            return self.send_data(self.get_xml(), CONTENT_TEXT, AVT_QUERY)


class FaxSubmit(FaxCommand):

    _logger = logging.getLogger('rightfax.FaxSubmit')

    def __init__(self, debug=False, target_url=None, document=None, attachments=None):
        super(FaxSubmit, self).__init__(debug, target_url)
        if document:
            self.document = document
        else:
            self.document = Document()
        if attachments:
            self.attachments = attachments
        else:
            self.attachments = []

    def add_attachment(self, attachment):
        self.attachments.append(attachment)

    def append_xml(self, xmlbuf):
        if not self.document:
            raise RFNoDataException('No document given.')
        xmlbuf.write('<XML_FAX_SUBMIT stylesheet="XML_FAX_SUBMIT.xslt" xmlns="x-schema:XML_FAX_SUBMIT.xdr">\r\n')
        self.document.append_xml(xmlbuf)
        xmlbuf.write('</XML_FAX_SUBMIT>\r\n')

    def submit(self, xml=None, attachments=None):
        if not xml:
            xml = self.get_xml()
        if xml:
            FaxSubmit._logger.debug('XML (attachments not added yet):\n%s' % xml)
        else:
            raise RFNoDataException('No XML data given.')

        if not attachments:
            attachments = self.attachments
        if not attachments:
            FaxSubmit._logger.debug('No attachments so submitting as text')
            resp_list = self.send_data_ex(xml, CONTENT_TEXT, AVT_SUBMIT)
        else:
            FaxSubmit._logger.debug('There are attachments so MIME encode the whole thing')
            resp_list = self.send_data_ex(mime_encode(xml, attachments), CONTENT_MIME, AVT_SUBMIT)
        return resp_list

    def submit_ex(self, xml=None, attachments=None):
        if not xml:
            xml = self.get_xml()
        if xml:
            FaxSubmit._logger.debug('XML (attachments not added yet):\n%s' % xml)
        else:
            raise RFNoDataException('No XML data given.')

        if not attachments:
            attachments = self.attachments
        if not attachments:
            FaxSubmit._logger.debug('No attachments so submitting as text')
            resp_str = self.send_data(xml, CONTENT_TEXT, AVT_SUBMIT)
        else:
            FaxSubmit._logger.debug('There are attachments so MIME encode the whole thing')
            resp_str = self.send_data(mime_encode(xml, attachments), CONTENT_MIME, AVT_SUBMIT)
        return resp_str
