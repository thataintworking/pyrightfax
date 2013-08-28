# Port of the RightFax Java API
# Author: Ron Smith, ThatAintWorking.com
# Date: 12/7/2011

import logging
from xml.sax.saxutils import escape
from exceptions import RFNoDataException, RFNoDestinationException
from constants import ENCODING_NONE, ENCODING_BASE64
from rightfax import RFEmptyQueryException
from rightfax.timeutils import format_datetime_utc

class Sender(object):

    def __init__(self, name=None, emp_id=None, company=None, department=None, phone=None, email=None, bill_info1=None, bill_info2=None, reply_url=None, rf_user=None):
        self.name = name
        self.emp_id = emp_id
        self.company = company
        self.department = department
        self.phone = phone
        self.email = email
        self.bill_info1 = bill_info1
        self.bill_info2 = bill_info2
        self.reply_url = reply_url
        self.rf_user = rf_user

    def append_xml(self, xmlbuf):
        xmlbuf.write('\t<SENDER>\r\n')
        if self.name:
            xmlbuf.write('\t\t<FROM_NAME>%s</FROM_NAME>\r\n' % escape(self.name))
        if self.emp_id:
            xmlbuf.write('\t\t<EMP_ID>%s</EMP_ID>\r\n' % self.emp_id)
        if self.company:
            xmlbuf.write('\t\t<FROM_COMPANY>%s</FROM_COMPANY>\r\n' % escape(self.company))
        if self.department:
            xmlbuf.write('\t\t<FROM_DEPARTMENT>%s</FROM_DEPARTMENT>\r\n' % escape(self.department))
        if self.phone:
            xmlbuf.write('\t\t<FROM_PHONE>%s</FROM_PHONE>\r\n' % escape(self.phone))
        if self.email:
            xmlbuf.write('\t\t<RETURN_EMAIL>%s</RETURN_EMAIL>\r\n' % escape(self.email))
        if self.bill_info1:
            xmlbuf.write('\t\t<BILLINFO1>%s</BILLINFO1>\r\n' % escape(self.bill_info1))
        if self.bill_info2:
            xmlbuf.write('\t\t<BILLINFO2>%s</BILLINFO2>\r\n' % escape(self.bill_info2))
        if self.reply_url:
            xmlbuf.write('\t\t<REPLY_TO>%s</REPLY_TO>\r\n' % escape(self.reply_url))
        if self.rf_user:
            xmlbuf.write('\t\t<RF_USER>%s</RF_USER>\r\n' % self.rf_user)
        else:
            xmlbuf.write('\t\t<RF_USER>DEFAULT</RF_USER\r\n')
        xmlbuf.write('\t</SENDER>\r\n')
        

class Body(object):

    _logger = logging.getLogger('rightfax.Body')

    def __init__(self, body_data=None, body_type=None, ftm=-1.0, flm=-1.0, fbm=-1.0, font=None, font_size=-1, leading=-1, pitch=-1, encoding=ENCODING_NONE):
        self.body_data = body_data
        self.body_type = body_type
        self.ftm = ftm
        self.flm = flm
        self.fbm = fbm
        self.font = font
        self.font_size = font_size
        self.leading = leading
        self.pitch = pitch
        self.encoding = encoding

    def append_xml(self, xmlbuf):
        if not self.body_data:
            Body._logger.warn('Body contains no data.')
            return
        xmlbuf.write('\t<BODY')
        if self.body_type:
            xmlbuf.write(' type="%s"' % self.body_type)
        if self.encoding == ENCODING_BASE64:
            xmlbuf.write(' encoding="BASE64"')
        if self.ftm >= 0.0:
            xmlbuf.write(' tm="%f"' % self.ftm)
        if self.flm >= 0.0:
            xmlbuf.write(' lm="%f"' % self.flm)
        if self.fbm >= 0.0:
            xmlbuf.write(' bm="%f"' % self.fbm)
        if self.font:
            xmlbuf.write(' font_name="%s"' % self.font)
            if self.font_size >= 0:
                xmlbuf.write(' font_size="%d"' % self.font_size)
            if self.leading >= 0:
                xmlbuf.write(' font_leading="%d"' % self.leading)
            if self.pitch >= 0:
                xmlbuf.write(' font_pitch="%d"' % self.pitch)
        xmlbuf.write('>\r\n')
        xmlbuf.write(self.body_data)
        xmlbuf.write('\t</BODY>\r\n')

    def has_data(self):
        return not (not self.body_data)


class Document(object):

    def __init__(self, send_datetime=None, beg_inc='xml.beg', end_inc='xml.end', form_name=None, form_x=0.0, form_y=0.0,
                 lib_doc_id=None, cover_text=None, cover_ext='TXT', cover_enc=ENCODING_NONE, sender=None,
                 destinations=None, body=None):
        self.send_datatime = send_datetime
        self.beg_inc = beg_inc
        self.end_inc = end_inc
        self.form_name = form_name
        self.form_x = form_x
        self.form_y = form_y
        self.lib_doc_id = lib_doc_id
        self.cover_text = cover_text
        self.cover_ext = cover_ext
        self.cover_enc = cover_enc
        if sender:
            self.sender = sender
        else:
            self.sender = Sender()
        if destinations:
            self.destinations = destinations
        else:
            self.destinations = []
        if body:
            self.body = body
        else:
            self.body = Body()

    def add_destination(self, destination):
        self.destinations.append(destination)

    def append_xml(self, xmlbuf):
        if not self.sender:
            raise RFNoDataException('No sender data given.')
        if not self.destinations:
            raise RFNoDestinationException('No destination(s) given.')

        if self.send_datatime:
            xmlbuf.write('\t<SEND_DATE_TIME>%s</SEND_DATE_TIME>\r\n' % format_datetime_utc(self.send_datatime))
        if self.beg_inc:
            xmlbuf.write('\t<INCLUDE_BEG>%s</INCLUDE_BEG>\r\n' % self.beg_inc)
        self.sender.append_xml(xmlbuf)
        xmlbuf.write('\t<DESTINATIONS>\r\n')
        for dest in self.destinations:
            dest.append_xml(xmlbuf)
        xmlbuf.write('\t</DESTINATIONS>\r\n')
        if self.form_name:
            xmlbuf.write('\t<FORM xcoord="%f" ycoord="%f">%s</FORM>\r\n' % (self.form_x, self.form_y, self.form_name))
        if self.cover_text:
            if self.cover_ext:
                cover_type = ' type="%s"' % self.cover_ext
            else:
                cover_type = ''
            if self.cover_enc == ENCODING_BASE64:
                encoding = ' encoding="BASE64"'
            else:
                encoding = ''
            xmlbuf.write('\t<COVER_TEXT%s%s>%s</COVER_TEXT>\r\n' % (cover_type, encoding, escape(self.cover_text)))
        if self.body and self.body.has_data():
            self.body.append_xml(xmlbuf)
        if self.lib_doc_id:
            xmlbuf.write('\t<ADD_LIBDOC>%s</ADD_LIBDOC>\r\n' % self.lib_doc_id)
        if self.end_inc:
            xmlbuf.write('\t<INCLUDE_END>%s</INCLUDE_END>\r\n' % self.end_inc)


class Query(object):

    def __init__(self, id=None, fax_num=None, rf_user=None, status=None, datetime_range=None):
        self.id = id
        self.fax_num = fax_num
        self.rf_user = rf_user
        self.status = status
        self.datetime_range = datetime_range

    def append_xml(self, xmlbuf):
        if not (self.id or self.fax_num or self.rf_user or self.status or self.datetime_range):
            raise RFEmptyQueryException('No data given with which to perform a query.')
        
        xmlbuf.write('\t\t<QUERY>\r\n')
        if self.id:
            xmlbuf.write('\t\t\t<UNIQUE_ID>%s</UNIQUE_ID>\r\n' % self.id)
        if self.datetime_range:
            xmlbuf.write('\t\t\t<DATE_RANGE start="%s" end="%s"/>\r\n' % tuple([format_datetime_utc(dt) for dt in self.datetime_range]))
        if self.fax_num:
            xmlbuf.write('\t\t\t<TO_FAXNUM>%s</TO_FAXNUM>\r\n' % self.fax_num)
        if self.rf_user:
            xmlbuf.write('\t\t\t<RF_USER>%s</RF_USER>\r\n' % self.rf_user)
        if self.status:
            xmlbuf.write('\t\t\t<STATUS>%s</STATUS>\r\n' % escape(self.status))
        xmlbuf.write('\t\t</QUERY>\r\n')
