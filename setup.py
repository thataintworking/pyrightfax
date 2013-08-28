# Port of the RightFax Java API
# Author: Ron Smith, ThatAintWorking.com
# Date: 12/7/2011

from distutils.core import setup

setup(
    name = 'pyrightfax',
    version = '1.1',
    packages = ['rightfax'],
    zip_safe = True,

    # metadata for upload to PyPI
    author = 'Ron Smith',
    author_email = 'ron.smith@thataintworking.com',
    description = 'This is a port of the RightFax Java API for Python.\nIt allows you to programatically interact with a RightFAX server to send faxes and query their status.',
    url = 'http://www.thataintworking.com/pyrightfax/',
    download_url = 'http://www.thataintworking.com/pyrightfax/pyrightfax-1.1.zip',
)