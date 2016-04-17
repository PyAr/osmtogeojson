import json
import sys

import geojson

filepath = 'examples/argentina-realtion-286393.json'
with open(filepath) as fd:
    data = json.load(fd)

element = data['elements'][0]  # raro

outer_lines = []
inner_lines = []

for member in element['members']:
    if member["type"] == "way":
        if member['role'] == 'outer':
            outer_lines.append([(x['lon'], x['lat']) for x in member['geometry']])
        elif member['role'] == 'inner':
            inner_lines.append([(x['lon'], x['lat']) for x in member['geometry']])

if not outer_lines:
    sys.exit(1)


def make_polygons(lines):
    polygons = []
    current_polygon = [lines[0]]
    lines = lines[1:]
    while lines:
        target_point = current_polygon[-1][-1]
        i = 0
        while i < len(lines):
            line = lines[i]
            if line[0] == target_point:
                current_polygon.append(line)
                del lines[i]
                break
            if line[-1] == target_point:
                current_polygon.append(line[::-1])
                del lines[i]
                break
            i += 1
    if i == len(lines):
        assert current_polygon[0][0] == current_polygon[-1][-1]
        polygons.append([point for _line in current_polygon for point in _line])
        if lines:
            current_polygon = [lines[0]]
            lines = lines[1:]
    return polygons


p_outer = make_polygons(outer_lines)
p_inner = make_polygons(inner_lines)

print geojson.MultiPolygon([p_outer, p_inner])
