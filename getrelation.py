import json
import sys

import overpass  # fades

# EXAMPLE:
# fades -p python2 getrelation.py 4422604 | less
# fades -p python2 getrelation.py 286393 > examples/argentina-relation-286393.json

OVERPASS_API_QUERY = '''
relation({osm_id})
'''

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('You need to pass the OSM relation id')
        print('Example:')
        print('python2 getrelation.py 4422604')
        sys.exit(1)

    osm_id = sys.argv[1]
    query = OVERPASS_API_QUERY.format(osm_id=osm_id)

    api = overpass.API()
    response = api.Get(query, responseformat='json', verbosity='body geom')
    print(json.dumps(response, indent=4))
