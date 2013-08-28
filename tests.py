# Author: rksmith
# Created: 12/9/11
# Copyright (c)2011 Pegasus Logistics Group, All Rights Reserved

import logging, unittest, time

TEST_FAX_URL = 'http://c4dprdrfax002/'
#TEST_FAX_URL = 'http://localhost:8888/'
TEST_FAX_USERID = 'SVC_RIGHTFAX'

TEST_FAX_NBR = '4696710325'
#TEST_FAX_NBR = '4696710345'

TEST_FAX_DOC = 'samples/Airbill.html'
TEST_FAX_COVER = 'samples/AirbillCoverSheet.html'

LOG_LEVEL = logging.INFO

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
logger = logging.getLogger('rightfax')
logger.setLevel(LOG_LEVEL)
logger.addHandler(handler)

import rightfax

class RightFaxTester(unittest.TestCase):

    def setUp(self):
        t = time.time()
        self.faxid = 'PT' + ('0000000000' + str(int(t)))[-10:] + str(int((t - int(t)) * 1000))

    def tearDown(self):
        pass

    def test_submit_query(self):
        fax = rightfax.FaxSubmit(target_url=TEST_FAX_URL)
        fax.document.sender.name = 'Pegasus'
        fax.document.sender.company = 'Pegasus'
        fax.document.sender.rf_user = TEST_FAX_USERID
        fax.document.add_destination(rightfax.FaxDestination(
            id = self.faxid,
            fax_num=TEST_FAX_NBR,
            name='Fred Flintstone',
            notify_name='DBNotify',
            notify_suc_tmplt='DBNotify.inc',
            notify_err_tmplt='DBNotify.inc'
        ))
        fax.add_attachment(TEST_FAX_COVER)
        fax.add_attachment(TEST_FAX_DOC)
        resp = fax.submit()
        if resp:
            print 'Response from submit:'
            for status in resp:
                print status

        done = False
        while not done:
            time.sleep(10)

            query = rightfax.FaxQuery(target_url=TEST_FAX_URL)
            query.add_query(rightfax.Query(
                id = self.faxid,
                rf_user=TEST_FAX_USERID
            ))
            resp = query.submit()
            if resp:
                print 'Response from query:'
                for status in resp:
                    print status
                    if status['status_code'] == '6':
                        print 'Fax sent successfully'
                        done = True
                    elif status['status_code'] == '9' or status['error_code'] != '0':
                        print 'Failed to send fax'
                        done = True

                
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(RightFaxTester)
    unittest.TextTestRunner(verbosity=2).run(suite)