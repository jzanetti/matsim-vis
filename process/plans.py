from xml.etree.ElementTree import iterparse

from xopen import xopen


def get_unselected_and_selected_plans(
    xml_path: str, 
    person_id: str, 
    how_many_plans_to_check: int = 5) -> dict:
    """Get all plans, including the unselected plans

    Args:
        xml_path (str): the output_events.xml path
        person_id (str): person name, e.g., p11
        how_many_plans_to_check (int, optional): total number of plans to be checked. Defaults to 5.

    Returns:
        dict: the dict contains all the plans
    """
    blacklist_id = []
    all_plans = {}
    for i in range(how_many_plans_to_check):
        all_plans[i], blacklist_id = get_plans(
            xml_path, 
            person_id, 
            apply_selected=False, 
            blacklist_id = blacklist_id)
    return all_plans


def get_plans(xml_path: str, person_id: str, apply_selected: bool = True, blacklist_id: list = []) -> tuple:
    """Get plans information

    Args:
        xml_path (str): _description_
        person_id (str): _description_
        apply_selected (bool, optional): if only get the plan which is selected. Defaults to True.
        blacklist_id (list, optional): when apply_selected=False, we return a list 
            contains the plan being processed. Defaults to [].

    Raises:
        Exception: _description_

    Returns:
        tuple: _description_
    """
    all_tasks = {}

    tree = iterparse(xopen(xml_path, "r"), events=['start', 'end'])

    start_person = False
    start_plan = False
    for xml_event, elem in tree:

        if xml_event == "start" and elem.tag == "person":
            if elem.attrib["id"] == person_id:
                start_person = True
        
        if start_person and (not start_plan):
            if xml_event == "start" and elem.tag == "plan":
                if apply_selected:
                    if elem.attrib["selected"] == "yes":
                        task_id = 0
                        start_plan = True
                else:
                    if elem.attrib["score"] not in blacklist_id:
                        task_id = 0
                        blacklist_id.append(elem.attrib["score"])
                        start_plan = True          

        if start_plan:
            if xml_event == "start" and elem.tag == "activity":
                all_tasks[task_id] = {"elem": elem, "type": "activity"}
                task_id += 1
            elif xml_event == "start" and elem.tag == "leg":
                all_tasks[task_id] = {"elem": elem, "type": "leg"}
                task_id += 1
            elif xml_event == "start" and elem.tag == "route":
                all_tasks[task_id] = {"elem": elem, "type": "route"}
                task_id += 1
    
            if xml_event == "end" and elem.tag == "plan":
                return all_tasks, blacklist_id

    raise Exception("not able to finish the plan ...")
