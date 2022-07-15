
from datetime import datetime, timedelta
from logging import getLogger
from math import sqrt
from random import sample
from xml.etree.ElementTree import iterparse

from numpy import NaN
from xopen import xopen

from process import TRAVEL_TRAJ_INTERVAL_MINS
from process.activity import get_activity_info
from process.network import get_leg_info
from process.utils import str2datetime

logger = getLogger()


def select_agents(all_agents: list, ratio: float = 1.0) -> list:
    """Select a ratio of agents

    Args:
        all_agents (list): the list contains all the agents 
        ratio (float, optional): the ratio of agents to be selected. Defaults to 1.0.

    Returns:
        list: selected agents
    """
    num_agents = int(ratio * len(all_agents))
    return sample(all_agents, num_agents)




def get_all_agents(plans_path: str) -> list:
    """Get all the agents from plans

    Args:
        plans_path (str): output plans

    Returns:
        list: all the agents in the file
    """
    all_agents = []

    tree = iterparse(xopen(plans_path, "r"), events=['start', 'end'])

    for xml_event, elem in tree:

        if xml_event == "start" and elem.tag == "person":
            if elem.attrib["id"] not in all_agents:
                all_agents.append(elem.attrib["id"])
    
    return all_agents


def interp_agent_movement(agent_movement: dict, all_times: list) -> dict:
    """Assign the agent movement to the requirement dataframe

    Args:
        agent_movement (dict): agent movement from get_agent_movement
        all_times (list): the list contains the time steps

    Returns:
        dict: the dict contains data for all time steps
    """
    output = {}

    all_agent_times = list(agent_movement.keys())
    total_timesteps = 0
    for i, proc_time in enumerate(all_times):

        nearest_agent_time = min(all_agent_times, key=lambda d: abs(d - proc_time))

        if ((nearest_agent_time - proc_time).total_seconds() / 60.0) > TRAVEL_TRAJ_INTERVAL_MINS * 2:
            if i == 0:
                output[proc_time] = {"x": NaN, "y": NaN}
            else:
                output[proc_time] = output[all_times[i-1]] # if we don't have travel during a period, we take the last travelled position 
        else:
            output[proc_time] = {
                    "x": agent_movement[nearest_agent_time]["x"],
                    "y": agent_movement[nearest_agent_time]["y"]
                }
            total_timesteps += 1
    
    # logger.info(f"obtain a total of {total_timesteps} timesteps")
    
    return output


def get_agent_movement(all_tasks: dict, all_links: dict) -> dict:
    """Get the agent movement from a single plan

    Args:
        all_tasks (dict): all tasks in a dict, e.g., every activities + routes (including legs) in xml, e.g.,
            {
                ...
                {'elem': <Element 'leg' at 0x...ae108f6f0>, 'type': 'leg'}
                {'elem': <Element 'route' at ...ae108f5b0>, 'type': 'route'}
                {'elem': <Element 'activity' ...ae108f420>, 'type': 'activity'}
                ...
                {'elem': <Element 'leg' at 0x...ae108f4c0>, 'type': 'leg'}
            }
        all_links (dict): the dict contains all the links information, e.g.,
        {
            'nodes': {
                'node_1': {'x': 400.0, 'y': 500.0}, 
                'node_2': {'x': 600.0, 'y': 500.0}, 
                ...},
            'links': {
                'link1': {'from_node': 'node_1', 'to_node': 'node_2', ...}
                ...}
        }

    Returns:
        dict: the dict contains all the movements for a plan, e.g.,
            {

                datetime.datetime(19... 1, 17, 0): {'link': 'link5r', 'x': 1000.0, 'y': 2000.0}, 
                datetime.datetime(19... 17, 0, 6): {'link': 'link5r', 'x': 960.0, 'y': 2000.0}, 
                ...
                datetime.datetime(19... 1, 18, 0): {'link': 'link7r', 'x': 500.0, 'y': 2500.0}, 
                datetime.datetime(19... 18, 0, 6):  ...
                ...
            }
    """
    output = {}
    for task_id in range(len(all_tasks)):

        proc_task = all_tasks[task_id]

        if proc_task["type"] != "route":
            continue

        # -------------------------
        # get acitivities:
        # -------------------------
        previous_activity = get_activity_info(all_tasks, task_id, forward_mode=False)
        next_activity = get_activity_info(all_tasks, task_id, forward_mode=True)

        # -------------------------
        # get route info
        # -------------------------
        leg_info = get_leg_info(all_tasks, task_id)
        route_mode = leg_info["elem"].attrib["mode"]
        route_start_time = str2datetime(leg_info["elem"].attrib["dep_time"])
        route_travel_time = str2datetime(leg_info["elem"].attrib["trav_time"]).minute
        if route_travel_time == 0:
            continue
        route_end_time = str2datetime(leg_info["elem"].attrib["dep_time"]) + timedelta(
            minutes=route_travel_time)

        # -------------------------
        # get links info
        # -------------------------
        link_names = proc_task["elem"].text.split(" ")
        link_output = {}
        for i, proc_link in enumerate(link_names):
            
            if i == 0: # skip the first link (since it is usually the link where the activity locates)
                continue

            link_output[proc_link] = get_proc_link_info(
                i, 
                link_names,
                all_links["nodes"],
                all_links["links"][proc_link],
                previous_activity,
                next_activity)

        total_dis = get_route_total_distance(link_output)
        total_mins = get_route_time_range(route_start_time, route_end_time)
        ave_spd = get_spd(total_mins, total_dis)

        output.update(get_travel_traj(route_start_time, route_end_time, link_output, link_names[1:], ave_spd))

    return output


def get_travel_unit(proc_link: dict) -> dict:
    """Get travel unit

    Args:
        proc_link (dict): link information

    Returns:
        dict: travel unit
    """
    travel_unit = {}

    for index in ["x", "y"]:
        if proc_link["end"][index] > proc_link["start"][index]:
            travel_unit[index] = 1.0
        elif proc_link["end"][index] < proc_link["start"][index]:
            travel_unit[index] = -1.0
        else:
            travel_unit[index] = 0.0
    return travel_unit


def get_proc_link_info(
        link_index: int, 
        link_names: list,
        node_info: dict,
        link_info: dict,
        previous_activity: dict,
        next_activity: dict) -> dict:
    """Get the current link information, including the
        start and end location and the total distance

    Args:
        link_index (int): _description_
        link_names (list): _description_
        node_info (dict): _description_
        link_info (dict): _description_
        previous_activity (dict): _description_
        next_activity (dict): _description_

    Returns:
        dict: _description_
    """
    if link_index == 1:
        proc_link_info = {
            "start": {"x": float(previous_activity["elem"].attrib["x"]), "y": float(previous_activity["elem"].attrib["y"])},
            "end": {
                "x": float(node_info[link_info["to_node"]]["x"]),
                "y": float(node_info[link_info["to_node"]]["y"]),
            }}
    elif link_index == len(link_names) - 1:
        proc_link_info = {
            "start": {
                "x": float(node_info[link_info["from_node"]]["x"]),
                "y": float(node_info[link_info["from_node"]]["y"]),
            },
            "end": {"x": float(next_activity["elem"].attrib["x"]), "y": float(next_activity["elem"].attrib["y"])}
        }
    else:
        proc_link_info = {
            "start": {
                "x": float(node_info[link_info["from_node"]]["x"]),
                "y": float(node_info[link_info["from_node"]]["y"]),
            },
            "end": {
                "x": float(node_info[link_info["to_node"]]["x"]),
                "y": float(node_info[link_info["to_node"]]["y"]),
            }
        } 
    proc_link_info["dis"] = sqrt(
        (proc_link_info["end"]["x"] - proc_link_info["start"]["x"]) ** 2 +
        (proc_link_info["end"]["y"] - proc_link_info["start"]["y"]) ** 2)
    
    return proc_link_info


def get_travel_traj(
    route_start_time: datetime, 
    route_end_time: datetime, 
    link_output_input: dict, 
    link_names_input: list, 
    ave_spd: float) -> dict:
    """Get travel trajector for a leg, e.g., the output would be something like
        {
            datetime.datetime(1900, 1, 1, 7, 5): {'link': 'link4', 'x': 400.0, 'y': 1586.6666666666665}
            ...
            datetime.datetime(1900, 1, 1, 7, 5, 18): {'link': 'link4', 'x': 400.0, 'y': 1660.0}
        }

    Args:
        route_start_time (datetime): _description_
        route_end_time (datetime): _description_
        link_output_input (dict): _description_
        link_names_input (list): _description_
        ave_spd (float): _description_

    Returns:
        dict: the dict contains the single leg timestap location
    """
    proc_time = route_start_time
    link_start_time = route_start_time
    link_index = 0

    travel_traj = {}
    while proc_time <= route_end_time:

        if link_index >= len(link_names_input):
            break

        proc_link_name = link_names_input[link_index]
        proc_link = link_output_input[proc_link_name]

        proc_unit = get_travel_unit(proc_link)

        travelled_x = proc_link["start"]["x"] + ave_spd * proc_unit["x"] * (
            (proc_time - link_start_time).total_seconds() / 60.0
        )
        travelled_y = proc_link["start"]["y"] + ave_spd * proc_unit["y"] * (
            (proc_time - link_start_time).total_seconds() / 60.0
        )

        travelled_dis = sqrt(
            (travelled_x - proc_link["start"]["x"]) ** 2 + 
            (travelled_y - proc_link["start"]["y"]) ** 2
        )

        travel_traj[proc_time] = {"link": proc_link_name, "x": travelled_x, "y": travelled_y}

        if travelled_dis >= proc_link["dis"]:
            link_index += 1
            link_start_time = proc_time
        else:
            proc_time += timedelta(minutes=TRAVEL_TRAJ_INTERVAL_MINS)
    
    return travel_traj


def get_spd(total_mins: float, total_dis: float) -> float:
    """Get the average vehicle speed for a route

    Args:
        total_mins (float): the minutes spent on the route
        total_dis (float): the total distance for a route (with multiple links)

    Returns:
        float: the average speed
    """
    return float(total_dis) / (total_mins)


def get_route_time_range(route_start_time: datetime, route_end_time: datetime) -> float:
    """Get the period to be spent on a route

    Args:
        route_start_time (datetime): route start time
        route_end_time (datetime): route end time

    Returns:
        float: the time range for a route
    """
    return (route_end_time - route_start_time).total_seconds() / 60.0


def get_route_total_distance(link_output_to_use: dict) -> float:
    """Get total distance for a route

    Args:
        link_output_to_use (dict): the dict contains all the links in a route

    Returns:
        float: the total distance
    """
    total_distance = 0
    for link_name in link_output_to_use:
        total_distance += link_output_to_use[link_name]["dis"]

    return total_distance



