from datetime import datetime, timedelta
from xml.etree.ElementTree import iterparse

from xopen import xopen


def get_link_density(
        diags_start_datetime: datetime, 
        diags_end_datetime: datetime, 
        output_interval_mins: int,
        agent_movements: dict,
        all_link_names: list) -> dict:
    """Get link usage density

    Args:
        agent_movements (dict): agent movemet in a dict, e.g.,
            {
                time1: {link: ..., x: ..., y: ...},
                ...
            }

    Returns:
        dict: the dict contains the number of movement against time
    """

    def _init_link_density(all_link_names: list) -> dict:
        """_summary_

        Args:
            all_link_names (list): _description_
        """
        proc_link_density = {}
        for link_name in all_link_names:
            proc_link_density[link_name] = 0.0
        
        return proc_link_density

    proc_time = diags_start_datetime

    link_density = {}

    while proc_time <= diags_end_datetime - timedelta(minutes=output_interval_mins):

        if proc_time not in link_density:
            link_density[proc_time] = _init_link_density(all_link_names)

        for agent in agent_movements:
            for agent_time in agent_movements[agent]:
                if agent_time >= proc_time and agent_time < proc_time + timedelta(minutes=output_interval_mins):
                    proc_link = agent_movements[agent][agent_time]["link"]
                    link_density[proc_time][proc_link] += 1
        
        proc_time += timedelta(minutes=output_interval_mins)
    
    return link_density




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


def get_link_coords(all_links: dict, link_name_to_use: str) -> dict:
    """Get link coordinates

    Args:
        all_links (dict): _description_
        link_name_to_use (str): _description_

    Returns:
        dict: _description_
    """
    proc_link = all_links["links"][link_name_to_use]

    return {
        "x": {
                "start": all_links["nodes"][proc_link["from_node"]]["x"], 
                "end": all_links["nodes"][proc_link["to_node"]]["x"]
            },
        "y": {
                "start": all_links["nodes"][proc_link["from_node"]]["y"], 
                "end": all_links["nodes"][proc_link["to_node"]]["y"]
            },
    }
