from datetime import timedelta
from math import sqrt
from xml.etree.ElementTree import iterparse

from xopen import xopen

from process import PT_SECTIONS_TO_BE_READ
from process.traj import get_travel_traj
from process.utils import str2datetime


def update_section_flag(xml_flag: dict, xml_event: str, elem) -> dict:
    """If we are getting into the transitStops section

    Args:
        xml_event (str): xml_event, e.g., start/end

    Returns:
        dict: get xml flag, e.g., if we are reading certain section
    """

    if xml_event == "start":
        xml_flag[elem.tag]["start"] = True
    elif xml_event == "end":
        xml_flag[elem.tag]["start"] = False
    
    if "id" in elem.attrib:
        xml_flag[elem.tag]["id"] = elem.attrib["id"]
    
    return xml_flag
    
def get_stop_info(elem_attrib) -> dict:
    
    return {
        "x": elem_attrib["x"],
        "y": elem_attrib["y"],
        "link": elem_attrib["linkRefId"]
    }


def check_condition_to_run(xml_section_flag: dict, conditions: list, xml_event: None or str = None) -> bool:

    # we hope all the items in conditions to be true
    for proc_cond in conditions:
        if not xml_section_flag[proc_cond]["start"]:
            return False
    
    # we hope all the items not in conditions to be false
    for proc_cond in list(set(list(xml_section_flag.keys())) - set(conditions)):
        if xml_section_flag[proc_cond]["start"]:
            return False

    if xml_event != "start":
        return False

    return True


def get_pt(xml_path: str, all_links: dict) -> dict:
    """

    Args:
        xml_path (str): transitSchedule.xml from matsim

    Returns:
        dict: the dict contains the public transportation trajectory

    Returns:

    """
    tree = iterparse(xopen(xml_path, "r"), events=['start', 'end'])

    xml_section_flag = {}
    for section_titles in PT_SECTIONS_TO_BE_READ:
        xml_section_flag[section_titles] = {
            "start": False,
            "id": None
        }

    all_routes = {}
    for xml_event, elem in tree:

        # ----------------------------
        # step 1: check which section we are currently at in xml
        # ----------------------------
        if elem.tag in PT_SECTIONS_TO_BE_READ:
            xml_section_flag = update_section_flag(xml_section_flag, xml_event, elem)

        # ----------------------------
        # step 2: read section information if needed
        # ----------------------------
        # 2.1 get stop information (e.g., stopFacility) within transitStops
        if check_condition_to_run(xml_section_flag, ["transitStops"], xml_event=xml_event):
            if elem.tag != "stopFacility":
                stops = {}
            else:
                stops[elem.attrib["id"]] = get_stop_info(elem.attrib)

        # 2.2 get route profile information (e.g., stop) within transitStops
        if check_condition_to_run(xml_section_flag, ["transitLine", "transitRoute", "routeProfile"], xml_event=xml_event):
            if elem.tag != "stop":
                output_routeprofile = {}
            else:
                output_routeprofile[elem.attrib["refId"]] = {
                    "arrivalOffset": elem.attrib["arrivalOffset"],
                    "departureOffset": elem.attrib["departureOffset"]
                }

        # 2.3 get route information (e.g., link) within transitStops
        if check_condition_to_run(xml_section_flag, ["transitLine", "transitRoute", "route"], xml_event=xml_event):
            if elem.tag != "link":
                output_route = []
            else:
                output_route.append(elem.attrib["refId"])

        # 2.4 get departures information (e.g., departure) within transitStops
        if check_condition_to_run(xml_section_flag, ["transitLine", "transitRoute", "departures"], xml_event=xml_event):
            if elem.tag != "departure":
                output_departures = {}
            else:
                output_departures[elem.attrib["id"]] = {
                    "departureTime": elem.attrib["departureTime"],
                    "vehicleRefId": elem.attrib["vehicleRefId"]
                }

        # ----------------------------
        # step 3: final process
        # ----------------------------
        if xml_event == "end" and elem.tag == "departures":
            route_id = "{trasitline_id}_{trasitroute_id}".format(
                trasitline_id=xml_section_flag["transitLine"]["id"],
                trasitroute_id=xml_section_flag["transitRoute"]["id"]
            )
            all_routes[route_id] = get_pt_traj(
                output_departures, output_route, output_routeprofile, stops, all_links)
    
    return all_routes


def get_pt_traj(
    output_departures: dict, 
    output_route: dict, 
    output_routeprofile: dict, 
    stops: dict, 
    all_links: dict) -> dict:
    """Get public transportation trajectory

    Args:
        output_departures (dict): departures information from the xml, e.g.,
            {
                'depart_1': {'departureTime': '07:00:00', 'vehicleRefId': 'bus_no1'}
                'depart_2': {'departureTime': '07:15:00', 'vehicleRefId': 'bus_no2'}
                'depart_3': {'departureTime': '07:30:00', 'vehicleRefId': 'bus_no3'}
            }
        output_route (dict): route information from the xml, e.g.,
            ['link5-4', 'link4-3', 'link3-7', 'link7-8', 'link8-9', 'link9-10']
        output_routeprofile(dict): route profile from the xml file, e.g.,
            {
                'stop2r': {'arrivalOffset': '00:00:00', 'departureOffset': '00:05:00'}
                'stop1r': {'arrivalOffset': '00:00:00', 'departureOffset': '00:10:00'}
                'stop3': {'arrivalOffset': '00:00:00', 'departureOffset': '00:15:00'}
                'stop4': {'arrivalOffset': '00:00:00', 'departureOffset': '00:20:00'}
                'stop5': {'arrivalOffset': '00:00:00', 'departureOffset': '00:25:00'}
            }
        stops (dict): stops information from the xml, e.g., 
            {
                'stop1': {'x': '600.0', 'y': '1000.0', 'link': 'link3-4'}
                'stop1r': {'x': '600.0', 'y': '1000.0', 'link': 'link4-3'}
                  ......
                'stop2r': {'x': '1100.0', 'y': '1000.0', 'link': 'link5-4'}
            }
        all_links (dict): link information from the network.xml

    Returns:
        dict: the dict contains all the movements for all pt, e.g.,
            {
                depature1: {
                    datetime.datetime(19... 1, 17, 0): {'link': 'link5r', 'x': 1000.0, 'y': 2000.0}, 
                    datetime.datetime(19... 17, 0, 6): {'link': 'link5r', 'x': 960.0, 'y': 2000.0}, 
                    ...
                    datetime.datetime(19... 1, 18, 0): {'link': 'link7r', 'x': 500.0, 'y': 2500.0}, 
                    datetime.datetime(19... 18, 0, 6):  ...
                }
                ...
            }
    """
    output = {}
    for departure_id in output_departures:

        proc_departure = output_departures[departure_id]

        proc_departure_start_time = proc_departure["departureTime"]

        all_stops = list(output_routeprofile.keys())

        output[departure_id] = {}
    
        for i in range(len(all_stops)):
            if i >= len(all_stops) - 1:
                break

            start_stop = all_stops[i]
            end_stop = all_stops[i + 1]

            links_in_between = get_links_in_between(
                stops[start_stop], stops[end_stop], output_route)
            
            # ------------------------------------------
            # start_stop (x,y) --> start_link (to_node) -<links between>- end_link(from_node) --> end_stop(x, y)
            # ------------------------------------------
            # 1. start_stop (x,y) --> start_link (to_node)
            start_link_name = stops[start_stop]["link"]
            start_link_info = all_links["links"][start_link_name]
            proc_node_info = all_links["nodes"][start_link_info["to_node"]]
            first_leg = {
                "link_name": start_link_name,
                "start": {"x": float(stops[start_stop]["x"]), "y": float(stops[start_stop]["y"])},
                "end": {"x": float(proc_node_info["x"]), "y": float(proc_node_info["y"])},
            }
            # 2. end_link(from_node) --> end_stop(x, y)
            end_link_name = stops[end_stop]["link"]
            end_link_info = all_links["links"][end_link_name]
            proc_node_info = all_links["nodes"][end_link_info["from_node"]]
            last_leg = {
                "link_name": end_link_name,
                "start": {"x": float(proc_node_info["x"]), "y": float(proc_node_info["y"])},
                "end": {"x": float(stops[end_stop]["x"]), "y": float(stops[end_stop]["y"])}
            }
            # 3. <links between>
            inbetween_legs = []
            for proc_link_name in links_in_between:
                start_node = all_links["links"][proc_link_name]["from_node"]
                end_node = all_links["links"][proc_link_name]["to_node"]
                inbetween_legs.append(
                    {
                        "link_name": proc_link_name,
                        "start": {
                            "x": float(all_links["nodes"][start_node]["x"]), 
                            "y": float(all_links["nodes"][start_node]["y"])
                        },
                        "end": {
                            "x": float(all_links["nodes"][end_node]["x"]), 
                            "y": float(all_links["nodes"][end_node]["y"])
                        }
                    }
                )
            
            all_legs = [first_leg] + inbetween_legs + [last_leg]

            travelled_distance = 0
            for proc_leg in all_legs:
                travelled_distance += sqrt(
                    (proc_leg["end"]["x"] - proc_leg["start"]["x"]) ** 2 + 
                    (proc_leg["end"]["y"] - proc_leg["start"]["y"]) ** 2
                )

            travelled_time_start = str2datetime(proc_departure["departureTime"]) + \
                timedelta(minutes=str2datetime(output_routeprofile[start_stop]["departureOffset"]).minute)
            travelled_end_start = str2datetime(proc_departure["departureTime"]) + \
                timedelta(minutes=str2datetime(output_routeprofile[end_stop]["departureOffset"]).minute)
            travelled_spd = travelled_distance / ((travelled_end_start - travelled_time_start).total_seconds() / 60.0)

            link_output_input = {}
            link_names_input = []
            for proc_leg in all_legs:
                link_output_input[proc_leg["link_name"]] = {
                    "start": proc_leg["start"],
                    "end": proc_leg["end"],
                    "dis": sqrt(
                        (proc_leg["end"]["x"] - proc_leg["start"]["x"]) ** 2 + 
                        (proc_leg["end"]["y"] - proc_leg["start"]["y"]) ** 2
                    )
                }
                link_names_input.append(proc_leg["link_name"])

            output[departure_id].update(get_travel_traj(
                travelled_time_start, 
                travelled_end_start, 
                link_output_input, 
                link_names_input, 
                travelled_spd))

    return output


    """
            {
            'link8-9': {'start': {'x': 500.0, 'y': 2000.0}, 'end': {'x': 1500.0, 'y': 2000.0}, 'dis': 1000.0}
            'link9-10': {'start': {'x': 1500.0, 'y': 2000.0}, 'end': {'x': 2250.0, 'y': 2000.0}, 'dis': 750.0}
            'link10-9': {'start': {'x': 2250.0, 'y': 2000.0}, 'end': {'x': 2000.0, 'y': 2000.0}, 'dis': 250.0}
        }
    """
            


def get_links_in_between(start_link: str, end_link: str, output_route: list) -> list:
    """Get all links between start_link and end_link

    Args:
        start_link (str): start_link name, e.g., "link4-3"
        end_link (str): end link name, e.g., "link8-9"
        output_route (list): route information, e.g.,
            ['link5-4', 'link4-3', 'link3-7', 'link7-8', 'link8-9', 'link9-10']

    Returns:
        list: [link3-7, link7-8]
    """
    return output_route[
        output_route.index(start_link["link"])+1:output_route.index(end_link["link"])]
