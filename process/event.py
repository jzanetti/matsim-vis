from datetime import datetime, timedelta
from xml.etree.ElementTree import iterparse

from numpy import NaN
from xopen import xopen

from process import EMISSION_TYPES


def interp_emission(all_events: dict, all_times: list, max_allowed_min_diff: int = 5) -> dict:
    """Assign the agent movement to the requirement dataframe

    Args:
        agent_movement (dict): agent movement from get_agent_movement
        all_times (list): the list contains the time steps

    Returns:
        dict: the dict contains data for all time steps
    """
    output = {}

    all_event_times = list(all_events.keys())
    used_nearest_event_time = []
    for i, proc_time in enumerate(all_times):

        output[proc_time] = {}
        if len(all_event_times) == 0:
            for proc_emission_type in EMISSION_TYPES:
                output[proc_time][proc_emission_type] = NaN
            continue

        nearest_event_time = min(all_event_times, key=lambda d: abs(d - proc_time))

        if (((nearest_event_time - proc_time).total_seconds() / 60.0) > max_allowed_min_diff) or (
            nearest_event_time in used_nearest_event_time):
            for proc_emission_type in EMISSION_TYPES:
                output[proc_time][proc_emission_type] = NaN
        else:
            used_nearest_event_time.append(nearest_event_time)
            for proc_emission_type in EMISSION_TYPES:
                output[proc_time][proc_emission_type] = all_events[nearest_event_time][proc_emission_type]
    
    return output



def get_emission(xml_path: str, person_id: str, all_times: list) -> tuple:
    """Get event information

    Args:
        xml_path (str): _description_
        person_id (str): _description_

    Returns:
        tuple: _description_
    """
    all_emission = {"warmEmissionEvent": {}, "coldEmissionEvent": {}}

    tree = iterparse(xopen(xml_path, "r"), events=['start', 'end'])

    ref_time = datetime(all_times[0].year, all_times[0].month, all_times[0].day, 0, 0, 0)
    for xml_event, elem in tree:

        if xml_event == "start" and elem.tag == "event":
            elem_attrib = elem.attrib
            if elem_attrib["type"] not in ["warmEmissionEvent", "coldEmissionEvent"]:
                continue

            if elem_attrib["vehicleId"] == person_id:
                event_time = ref_time + timedelta(seconds=float(elem_attrib["time"]))
                
                if event_time not in all_emission[elem_attrib["type"]]:
                    all_emission[elem_attrib["type"]][event_time] = {}

                for proc_emission_type in EMISSION_TYPES:
                    try:
                        emission_total = float(elem_attrib[proc_emission_type])
                    except KeyError:
                        emission_total = NaN
                    all_emission[elem_attrib["type"]][event_time][proc_emission_type] = emission_total
    
    all_emission_interp = {}
    for emission_event_name in ["coldEmissionEvent", "warmEmissionEvent"]:
        all_emission_interp[emission_event_name] = interp_emission(
            all_emission[emission_event_name], all_times)

    return all_emission_interp
