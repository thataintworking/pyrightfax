# Port of the RightFax Java API
# Author: Ron Smith, ThatAintWorking.com
# Date: 12/7/2011

from xml.sax.saxutils import escape
from exceptions import RFNoFaxNumberException, RFNoDestinationException

class Destination(object):
    """Base class for destination types"""

    def __init__(self, id=None, name=None, company=None, phone=None, inc=None, def_inc=None, cover=None):
        if self.__class__ is Destination:
            raise NotImplementedError('This method must be called by a subclass')
        self.id = id
        self.name = name
        self.company = company
        self.phone = phone
        self.inc = inc
        self.def_inc = def_inc
        self.cover = cover

    def append_xml(self, xmlbuf):
        if self.__class__ is Destination:
            raise NotImplementedError('This method must be called by a subclass')
        if self.inc:
            xmlbuf.write('\t\t\t<INCLUDE_INC>%s</INCLUDE_INC>\r\n' % self.inc)
        if self.name:
            xmlbuf.write('\t\t\t<TO_NAME>%s</TO_NAME>\r\n' % escape(self.name))
        if self.company:
            xmlbuf.write('\t\t\t<TO_COMPANY>%s</TO_COMPANY>\r\n' % escape(self.company))
        if self.phone:
            xmlbuf.write('\t\t\t<TO_CONTACTNUM>%s</TO_CONTACTNUM>\r\n' % escape(self.phone))
        if self.cover:
            xmlbuf.write('\t\t\t<COVERSHEET>%s</COVERSHEET>\r\n' % escape(self.cover))
        if self.def_inc:
            xmlbuf.write('\t\t\t<INCLUDE_DEF>%s</INCLUDE_DEF>\r\n' % self.def_inc)


class FaxDestination(Destination):

    def __init__(self, id=None, name=None, company=None, phone=None, inc=None, def_inc=None, cover=None, fax_num=None,
                 alt_fax=None, notify_name=None, notify_suc_tmplt=None, notify_err_tmplt=None):
        Destination.__init__(self, id, name, company, phone, inc, def_inc, cover)
        self.fax_num = fax_num
        self.alt_fax = alt_fax
        self.notify_name = notify_name
        self.notify_suc_tmplt = notify_suc_tmplt
        self.notify_err_tmplt = notify_err_tmplt

    def append_xml(self, xmlbuf):
        if not self.fax_num:
            raise RFNoFaxNumberException('No fax number given for this destination.')

        if self.id:
            xmlbuf.write('\t\t<FAX unique_id="%s">\r\n' % self.id)
        else:
            xmlbuf.write('\t\t<FAX>\r\n')

        xmlbuf.write('\t\t\t<TO_FAXNUM>%s</TO_FAXNUM>\r\n' % escape(self.fax_num))

        if self.alt_fax:
            xmlbuf.write('\t\t\t<ALT_FAX_NUM>%s</ALT_FAX_NUM>\r\n' %escape( self.alt_fax))

        super(FaxDestination, self).append_xml(xmlbuf)

        if self.notify_suc_tmplt and self.notify_err_tmplt:
            if self.notify_name:
                xmlbuf.write('\t\t\t<NOTIFY_HOST SuccessTemplate="%s" FailureTemplate="%s" Name="%s"/>\r\n' % (self.notify_suc_tmplt, self.notify_err_tmplt, self.notify_name))
            else:
                xmlbuf.write('\t\t\t<NOTIFY_HOST SuccessTemplate="%s" FailureTemplate="%s"/>\r\n' % (self.notify_suc_tmplt, self.notify_err_tmplt))

        xmlbuf.write('\t\t</FAX>\r\n')

class EmailDestination(Destination):

    def __init__(self, id=None, name=None, company=None, phone=None, inc=None, def_inc=None, cover=None, email_to=None,
                 email_cc=None, email_subj=None, notify_name=None, notify_suc_tmplt=None, notify_err_tmplt=None):
        Destination.__init__(self, id, name, company, phone, inc, def_inc, cover)
        self.email_to = email_to
        self.email_cc = email_cc
        self.email_subj = email_subj
        self.notify_name = notify_name
        self.notify_suc_tmplt = notify_suc_tmplt
        self.notify_err_tmplt = notify_err_tmplt

    def append_xml(self, xmlbuf):
        if not self.email_to:
            raise RFNoDestinationException('No email address given for this destination.')

        if self.id:
            xmlbuf.write('\t\t<EMAIL unique_id="%s">\r\n' % self.id)
        else:
            xmlbuf.write('\t\t<EMAIL>\r\n')

        if self.email_to:
            xmlbuf.write('\t\t\t<TO_EMAIL>%s</TO_EMAIL>\r\n' % escape(self.email_to))
        if self.email_cc:
            xmlbuf.write('\t\t\t<CC_EMAIL>%s</CC_EMAIL>\r\n' % escape(self.email_cc))
        if self.email_subj:
            xmlbuf.write('\t\t\t<SUBJECT>%s</SUBJECT>\r\n' % escape(self.email_subj))

        super(EmailDestination, self).append_xml(xmlbuf)
        
        if self.notify_suc_tmplt and self.notify_err_tmplt:
            if self.notify_name:
                xmlbuf.write('\t\t\t<NOTIFY_HOST SuccessTemplate="%s" FailureTemplate="%s" Name="%s"/>\r\n' % (self.notify_suc_tmplt, self.notify_err_tmplt, escape(self.notify_name)))
            else:
                xmlbuf.write('\t\t\t<NOTIFY_HOST SuccessTemplate="%s" FailureTemplate="%s"/>\r\n' % (self.notify_suc_tmplt, self.notify_err_tmplt))

        xmlbuf.write('\t\t</EMAIL>\r\n')

class PrintDestination(Destination):
    
    def __init__(self, id=None, name=None, company=None, phone=None, inc=None, def_inc=None, cover=None,
                 printer_name=None, copies=0):
        Destination.__init__(self, id, name, company, phone, inc, def_inc, cover)
        self.printer_name = printer_name
        self.copies = copies

    def append_xml(self, xmlbuf):
        if not self.printer_name:
            raise RFNoDestinationException('No printer name given for this destination.')

        if self.id:
            xmlbuf.write('\t\t<PRINT unique_id="%s">\r\n' % self.id)
        else:
            xmlbuf.write('\t\t<PRINT>\r\n')
        if self.printer_name:
            xmlbuf.write('\t\t\t<PRINTER_NAME>%s</PRINTER_NAME>\r\n' % escape(self.printer_name))
        if self.copies > 1:
            xmlbuf.write('\t\t\t<COPIES>%d</COPIES>\r\n' % self.copies)

        super(PrintDestination, self).append_xml(xmlbuf)

        xmlbuf.write('\t\t</PRINT>\r\n')
        
