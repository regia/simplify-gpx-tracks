#!/usr/bin/env python
# coding: UTF-8

#TODO check if simplified file already exists


import os
import sys
import traceback
from lib import gpx, simplify


def simplify_track(filepath, filename, simplify_dir):
    """
    parse GPX file, simplifying track and create new GPX file with simplified track
    """
    full_filename = os.path.join(filepath, filename)
    print "{0}:".format(filename)
    parsed_gpx, points = gpx.get_data(full_filename)
    print "\tPoints before simplifying: {0}".format(len(points))
    simplified_points = simplify.simplify(points, 0.0001, True)
    print "\tPoints after simplifying: {0}\n".format(len(simplified_points))

    with open(os.path.join(simplify_dir, filename), 'w') as f:
        f.write(gpx.generate_gpx(parsed_gpx, simplified_points))
        f.flush()


def start():
    """
    Main function
    """
    if len(sys.argv) < 2:
        sys.exit("Script usage: {0} d:\\tracks".format(os.path.basename(sys.argv[0])))
    else:
        tracks_dir = sys.argv[1]

    save_dir = os.path.join(tracks_dir, "simplified_tracks")

    try:
        filenames = os.listdir(tracks_dir)
    except OSError:
        sys.exit("You've entered wrong/bad path")

    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    for filename in filenames:
        if os.path.isfile(os.path.join(tracks_dir, filename)) and os.path.splitext(filename)[1].lower() == ".gpx":
            try:
                simplify_track(tracks_dir, filename, save_dir)
            except Exception, msg:
                print "Exeption: {0}".format(msg)
                print traceback.format_exc()




if __name__ == "__main__":
    start()
