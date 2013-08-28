# Port of the RightFax Java API
# Author: Ron Smith, ThatAintWorking.com
# Date: 12/7/2011

from xml.sax.saxutils import escape
from exceptions import RFNoIDException

class Action(object):
    """Base class for Action types"""

    def __init__(self, id=None):
        if self.__class__ is Action:
            raise NotImplementedError('This method must be called by a subclass')
        self.id = id

    def append_xml(self, xmlbuf):
        if not self.id:
            raise RFNoIDException('No ID given to act upon.')

        xmlbuf.write('\t<FAX unique_id="%s">\r\n' % self.id)
        self.append_action_xml(xmlbuf)
        xmlbuf.write('\t</FAX>\r\n')

    def append_action_xml(self, xmlbuf):
        raise NotImplementedError('This method must be implemented by a subclass')


class ForwardAction(Action):
    def __init__(self, id=None, fax_num=None, name=None, company=None, alt_fax=None, phone=None, coversheet=None):
        Action.__init__(self, id)
        self.fax_num = fax_num
        self.name = name
        self.company = company
        self.alt_fax = alt_fax
        self.phone = phone
        self.coversheet = coversheet

    def append_action_xml(self, xmlbuf):
        xmlbuf.write('\t\t<FORWARD>\r\n')
        xmlbuf.write('\t\t\t<FAX_RECIPIENT>\r\n')
        if self.name:
            xmlbuf.write('\t\t\t\t<TO_NAME>%s</TO_NAME>\r\n' % escape(self.name))
        if self.company:
            xmlbuf.write('\t\t\t\t<TO_COMPANY>%s</TO_COMPANY>\r\n' % escape(self.company))
        if self.alt_fax:
            xmlbuf.write('\t\t\t\t<ALT_FAX_NUM>%s</ALT_FAX_NUM>\r\n' % escape(self.alt_fax))
        if self.phone:
            xmlbuf.write('\t\t\t\t<TO_CONTACTNUM>%s</TO_CONTACTNUM>\r\n' % escape(self.phone))
        if self.coversheet:
            xmlbuf.write('\t\t\t\t<COVERSHEET>%s</COVERSHEET>\r\n' % escape(self.coversheet))
        if self.fax_num:
            xmlbuf.write('\t\t\t\t<TO_FAXNUM>%s</TO_FAXNUM>\r\n' % escape(self.fax_num))
        xmlbuf.write('\t\t\t</FAX_RECIPIENT>\r\n')
        xmlbuf.write('\t\t</FORWARD>\r\n')


class DeleteAction(Action):

    def __init__(self, id=None):
        Action.__init__(self, id)

    def append_xml(self, xmlbuf):
        xmlbuf.write('\t\t<DELETE/>\r\n')


class CreateLibDocAction(Action):
    
    def __init__(self, id=None, lib_doc_id=None, lib_doc_desc=None):
        Action.__init__(self, id)
        self.lib_doc_id = lib_doc_id
        self.lib_doc_desc = lib_doc_desc

    def append_xml(self, xmlbuf):
        xmlbuf.write('\t\t<CREATE_LIB_DOC>\r\n')
        xmlbuf.write('\t\t\t<ID>%s</ID\r\n' % self.lib_doc_id)
        xmlbuf.write('\t\t\t<DESCRIPTION>%s</DESCRIPTION>\r\n' % escape(self.lib_doc_desc))
        xmlbuf.write('\t\t</CREATE_LIB_DOC>\r\n')


