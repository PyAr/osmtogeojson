"""
Usage:
    osmtogeojson.py [options] [<osm_file>]
    osmtogeojson.py -h | --help

Options:
  -h --help                             Show this screen
  -v --verbose                          Show debugging information
"""
import json
import logging

import geojson
from docopt import docopt

logger = logging.getLogger(__name__)


def make_polygons(ways):
    """Return a list of polygons.

    Each polygon it's a dict with role and lines keys.
    Role can be outer or inner.
    Lines it's a sorted list of the points needed to form the polygon.
    """
    polygons = []
    current_polygon_role = ways[0]['role']
    current_polygon_points = ways[0]['points']
    ways = ways[1:]

    while ways:
        target_point = current_polygon_points[-1]
        i = 0
        while i < len(ways):
            line = ways[i]['points']
            if line[0] == target_point:
                current_polygon_points.extend(line)
                del ways[i]
                break
            if line[-1] == target_point:
                current_polygon_points.extend(line[::-1])
                del ways[i]
                break
            i += 1
        else:
            logger.debug("First point: %s. Last point: %s", current_polygon_points[0],
                         current_polygon_points[-1])
            logger.debug("No of remaining ways: %s", len(ways))
            assert current_polygon_points[0] == current_polygon_points[-1]
            polygons.append({'role': current_polygon_role, 'points': current_polygon_points})
            if ways:
                current_polygon_role = ways[0]['role']
                current_polygon_points = ways[0]['points']
                ways = ways[1:]

    return polygons


def convert_to_geojson(ways):
    """Convert a list of ways to GeoJson objects.

    One "way" is a dict containing role and lines. Role can be outer or inner.
    """
    polygons = make_polygons(ways)
    outer_polygons = [x for x in polygons if x['role'] == 'outer']
    inner_polygons = [x for x in polygons if x['role'] == 'inner']

    no_outer = len(outer_polygons)
    no_inner = len(inner_polygons)
    logger.debug("Number of outer polygons: %s", no_outer)
    logger.debug("Number of inner polygons: %s", no_inner)

    if no_outer > 1 and no_inner > 0:
        raise ValueError('Unexpected combination between number of outer and inner polygons.'
                         'No. outer: {}. No. inner: {}'.format(no_outer, no_inner))

    if no_outer > 1:  # needs to create a multipolygon
        polygon_list = [x['points'] for x in outer_polygons]
        res = geojson.MultiPolygon(polygon_list)
    else:
        polygon_list = [outer_polygons[0]['points']]
        polygon_list.extend([x['points'] for x in inner_polygons])
        res = geojson.Polygon(polygon_list)

    return res


def read_json(osm_file):
    ways = []
    with open(osm_file, 'rt') as fd:
        data = json.load(fd)

    for member in data['elements'][0]['members']:
        if member['type'] == 'way':
            ways.append({
                'role': member['role'],
                'points': [(x['lon'], x['lat']) for x in member['geometry']]
            })
    return ways


READERS = {
    'json': read_json
}


def convert_file(osm_file, format='json'):
    """Convert the file in parameter to geojson."""
    if format not in READERS:
        raise ValueError('Unexpected format file: "{}".'
                         'Current valid formats: {}'.format(format, str(list(READERS.keys()))))
    ways = READERS[format](osm_file)
    if len(ways) == 0:
        return

    print(convert_to_geojson(ways))


if __name__ == '__main__':
    opts = docopt(__doc__)

    osm_file = opts['<osm_file>']
    verbose = opts['--verbose']

    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    convert_file(osm_file)
