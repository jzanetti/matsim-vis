from xml.etree.ElementTree import iterparse

from xopen import xopen


def get_facility(facility_filepath: str) -> dict:
    """Read facilities information

    Args:
        facility_filepath (str): facility path to be decoded

    Returns:
        dict: the dict contains the facilities
    """
    tree = iterparse(xopen(facility_filepath, 'r'), events=['start', 'end'])

    facilities = {}

    for xml_event, elem in tree:

        if xml_event == "start" and elem.tag == "facility":
            elem_attrib = elem.attrib
            facilities[elem_attrib["id"]] = {"x": float(elem_attrib["x"]), "y": float(elem_attrib["y"])}
    
    print(facilities)
    return facilities
