import os
import urllib2
from os.path import abspath, basename, dirname, exists, join

RLIS_URL = 'http://library.oregonmetro.gov/rlisdiscovery'
RLIS_TERMS = 'http://rlisdiscovery.oregonmetro.gov/view/terms.htm'
TRIMET_DRIVE = '//gisstore/gis'

STREETS = 'streets'
TRAILS = 'trails'


def define_data_paths(refresh=True, data_path=None):
    if exists(TRIMET_DRIVE):
        trimet_rlis = join(TRIMET_DRIVE, 'Rlis')
        streets = join(trimet_rlis, 'STREETS', '{}.shp'.format(STREETS))
        trails = join(trimet_rlis, 'TRANSIT', '{}.shp'.format(TRAILS))
    else:
        if not data_path:
            data_path = join(dirname(abspath(__name__)), 'data')

        if not exists(data_path):
            os.makedirs(data_path)

        streets = join(data_path, '{}.zip'.format(STREETS))
        trails = join(data_path, '{}.zip'.format(TRAILS))

        if refresh or not exists(streets) or not exists(trails):
            user_accept = raw_input(
                'RLIS data is about to be downloaded in order to use this '
                'data you must comply with their license, see more info here: '
                '"{}", do you wish to proceed? (y/n)\n'.format(RLIS_TERMS))

            if user_accept.lower() not in ('y', 'yes'):
                "you've declined RLIS's terms, program terminating..."
                exit()

            for ds in (STREETS, TRAILS):
                download_with_progress(
                    '{}/{}.zip'.format(RLIS_URL, ds), data_path)

    return streets, trails


def download_with_progress(url, write_dir):
    # adapted from: http://stackoverflow.com/questions/22676

    file_name = basename(url)
    file_path = join(write_dir, file_name)
    content = urllib2.urlopen(url)

    meta = content.info()
    file_size = int(meta.getheaders('Content-Length')[0])
    file_size_dl = 0
    block_sz = 8192

    print '\nDownload Info:'
    print 'file name: {} '.format(file_name)
    print 'target directory: {}'.format(write_dir)
    print 'file size: {:,} bytes'.format(file_size)

    with open(file_path, 'wb') as file_:

        while True:
            buffer_ = content.read(block_sz)
            if not buffer_:
                break

            file_size_dl += len(buffer_)
            file_.write(buffer_)

            status = '{0:12,d}  [{1:3.2f}%]'.format(
                file_size_dl, file_size_dl * 100. / file_size)
            status += chr(8) * (len(status) + 1)
            print status,
        print ''
    return file_path


if __name__ == '__main__':
    define_data_paths()
