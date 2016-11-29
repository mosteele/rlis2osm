import os
from collections import defaultdict
from os.path import basename, dirname, join, splitext
from zipfile import ZipFile

from shapely.geometry import LineString


def zip_path(path, **kwargs):
    """fiona has the ability open zipped shapefiles, this method
    handles both zipped and unzipped
    """

    vfs = None
    if path.endswith('.zip'):
        vfs = 'zip://{}'.format(path)
        path = '/{}'.format(basename(path).replace('.zip', '.shp'))
    else:
        path = path

    return dict(path=path, vfs=vfs, **kwargs)


def zip_shapefile(shp_path, zip_name=None, delete_src=False):
    # parts via https://en.wikipedia.org/wiki/Shapefile
    part_exts = ('ain', 'aih', 'atx', 'cpg', 'dbf', 'fbn', 'fbx', 'ixs',
                 'mxs', 'prj', 'qix', 'sbn', 'sbx', 'shp', 'shp.xml', 'shx')

    shp_dir = dirname(shp_path)
    shp_name = splitext(basename(shp_path))[0]
    if not shp_path.endswith('.shp'):
        raise ValueError(
            'the file {} is not a shapefile, provide a file '
            'that has the extension ".shp"'.format(shp_path))

    # if the user doesn't supply a name for the output use the name of
    # the shapefile
    if not zip_name:
        zip_name = shp_name

    zip_shp_path = join(shp_dir, '{}.zip'.format(zip_name))
    with ZipFile(zip_shp_path, 'w') as zip_shp:
        for file_name in os.listdir(shp_dir):
            if file_name.startswith(shp_name) \
                    and file_name.endswith(part_exts):
                file_path = join(shp_dir, file_name)
                zip_shp.write(file_path, file_name)

                if delete_src:
                    os.remove(file_path)

    return zip_shp_path


def extract_linear_rings(geom):
    try:
        coords = geom.coords
    except NotImplementedError:
        from shapely.geometry import mapping
        for part in geom:
            print mapping(part)
        exit()

    coord_pos = defaultdict(list)
    for i, coord in enumerate(geom.coords):
        coord_pos[coord].append(i)

    # start with first and last coordinate indexes in set
    split_pts = set([0, len(coords) - 1])
    for indexes in coord_pos.itervalues():
        if len(indexes) < 2:
            continue

        split_pts |= set(indexes)

    split_pts = sorted(split_pts)
    split_pairs = zip(split_pts[:-1], split_pts[1:])
    segments = [LineString(coords[i:j+1]) for i, j in split_pairs]
    return segments
