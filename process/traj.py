from datetime import datetime, timedelta
from math import sqrt

from process import TRAVEL_TRAJ_INTERVAL_MINS


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
        route_start_time (datetime): route start time in datetime, e.g., 
            datetime.datetime(1900, 1, 1, 8, 15)
        route_end_time (datetime): route end time in datetime, e.g.,
            datetime.datetime(1900, 1, 1, 8, 20)
        link_output_input (dict): link output information, e.g.,
        {
            'link8-9': {'start': {'x': 500.0, 'y': 2000.0}, 'end': {'x': 1500.0, 'y': 2000.0}, 'dis': 1000.0}
            'link9-10': {'start': {'x': 1500.0, 'y': 2000.0}, 'end': {'x': 2250.0, 'y': 2000.0}, 'dis': 750.0}
            'link10-9': {'start': {'x': 2250.0, 'y': 2000.0}, 'end': {'x': 2000.0, 'y': 2000.0}, 'dis': 250.0}
        }
        link_names_input (list): link names, e.g., 
            ['link8-9', 'link9-10', 'link10-9']
        ave_spd (float): agent moving speed, e.g., 400.0

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
