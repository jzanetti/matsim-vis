
from collections.abc import Iterable
from datetime import datetime, timedelta
from pathlib import Path
from xml.etree.ElementTree import iterparse

from xopen import xopen


def get_plans(xml_path: str, person_id: str):

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
                if elem.attrib["selected"] == "yes":
                    task_id = 0
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
                return all_tasks

    raise Exception("not able to finish the plan ...")
    
