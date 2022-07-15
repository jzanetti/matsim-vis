from xml.etree.ElementTree import iterparse

from xopen import xopen


def get_leg_info(all_tasks: dict, task_id: int, max_goback_id: int = 6):
    for id_diff in range(max_goback_id):
        proc_id = task_id - id_diff

        if all_tasks[proc_id]["type"] == "leg":
            return all_tasks[proc_id]


def get_network(network_filepath: str) -> dict:
    """Decode network.xml file

    Args:
        network_filepath (str): the path for the network.xml file

    Returns:
        dict: decoded network file
    """
    tree = iterparse(xopen(network_filepath, 'r'), events=['start', 'end'])

    nodes = {}
    links = {}

    for xml_event, elem in tree:
        if elem.tag == "node" and xml_event == 'start':
            atts = elem.attrib
            nodes[atts['id']] = {"x": float(atts['x']), "y": float(atts['y'])}

        elif elem.tag == 'link' and xml_event == 'start':
            atts = elem.attrib

            links[atts['id']] = {
                "from_node": atts['from'],
                "to_node": atts['to'],
                "length": float(atts['length']),
                "freespeed": float(atts['freespeed']),
                "capacity": float(atts['capacity']),
                "permlanes": float(atts['permlanes'])
            }

    return {"nodes": nodes, "links": links}
