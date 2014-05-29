#!/usr/bin/env python
# coding: UTF-8


#DONE add parsed waypoints
#DONE add exeptions
#TODO? maybe add parsed myltitracks

from lxml import etree


def get_etree_obj(filepath):
    """
    return etree object parsed from file
    """
    return etree.parse(filepath)


def get_root_xmlns(etree_obj):
    """
    return main file namespace(xmlns)
    """
    return etree_obj.getroot().nsmap[None]


def get_xmlns(etree_obj, xpath, namespace):
    """
    return additional namespace from file. Needed if we want parse something like <gpxx:DisplayColor>DarkMagenta</gpxx:DisplayColor>
    """
    node = etree_obj.xpath(xpath, namespaces=namespace)[0].getchildren()[0]
    return node.nsmap[node.prefix]


def parse_gpx(etree_obj, namespace):
    """
    parse gpx file and return all gpx data(except trkpt) in dictionary
    """


    def get_gpx_tag(etree_obj):
        """
        return tag <gpx>
        """
        gpx_string = etree.tostring(etree_obj.getroot())
        return gpx_string[:gpx_string.find(">")+1]


    def get_wpts(etree_obj, namespace):
        """
        return all wpt tags if they present in the file
        """
        wpts = etree_obj.xpath('/r:gpx//r:wpt', namespaces=namespace)
        return "\n".join([etree.tostring(wpt, encoding='UTF-8') for wpt in wpts])


    gpx_data = {"xml_tag": '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n'}
    gpx_data["gpx_tag"] = get_gpx_tag(etree_obj) + "\n"
    try:
        gpx_data["metadata_tag"] = etree.tostring(etree_obj.xpath('/r:gpx//r:metadata', namespaces=namespace)[0])
    except IndexError:
        gpx_data["metadata_tag"] = ""
    gpx_data["trk_tag"] = "<trk><name>{0}</name>\n".format((etree_obj.xpath('/r:gpx//r:trk//r:name', namespaces=namespace)[0].text).encode("UTF-8"))
    try:
        gpx_data["extensions_tag"] = etree.tostring(etree_obj.xpath('/r:gpx//r:trk//r:extensions', namespaces=namespace)[0])
    except:
        gpx_data["extensions_tag"] = ""
    gpx_data["trkseg_open_tag"] = "<trkseg>\n"
    gpx_data["wpts"] = get_wpts(etree_obj, namespace)
    gpx_data["gpx_end"] = "</trkseg>\n</trk>\n</gpx>"


    return gpx_data



def parse_track_points(etree_obj, namespace, namespace_set):
    """
        parse coordinates, elevation and time from GPX file and return
        list like [{"lat":245324, "lon":243255, "ele":234232, "time":23:324:324Z}, {{"lat":245324, "lon":243255, "ele":234232, "time":23:324:324Z}}]
    """
    trkpts = etree_obj.xpath('/r:gpx//r:trk//r:trkseg//r:trkpt', namespaces=namespace)

    points = []
    for trkpt in trkpts:
        trkpt_lat = trkpt.get("lat")
        trkpt_lon = trkpt.get("lon")
        try:
            trkpt_ele = trkpt.find(namespace_set + "ele").text
        except AttributeError:
            trkpt_ele = ""
        try:
            trkpt_time = trkpt.find(namespace_set + "time").text
        except AttributeError:
            trkpt_time = ""

        points.append({"lat":float(trkpt_lat), "lon":float(trkpt_lon), "ele":float(trkpt_ele), "time":trkpt_time})

    return points


def get_data(filepath):
    """
    return parsed GPX and points
    """

    tree = get_etree_obj(filepath)
    root_xmlns = get_root_xmlns(tree)
    root_xmlns_set = "{" + root_xmlns + "}"
    root_xmlns_dct = { "r": root_xmlns}

    return parse_gpx(tree, root_namespace_dct), parse_track_points(tree, root_xmlns_dct, root_xmlns_set)


def generate_gpx(gpx_data, points):
    """
    generated xml for GPX file and return it like a string
    """
    trkpt_tag = ''
    for point in points:
        trkpt_tag += '<trkpt lat="{0}" lon="{1}">\n\t<ele>{2}</ele>\n\t<time>{3}</time>\n</trkpt>\n'.format(point["lat"], point["lon"], point["ele"], point["time"])

    return gpx_data["xml_tag"] + gpx_data["gpx_tag"] + gpx_data["metadata_tag"] + gpx_data["trk_tag"] + gpx_data["extensions_tag"] + gpx_data["trkseg_open_tag"] + trkpt_tag + gpx_data["wpts"] + gpx_data["gpx_end"]

