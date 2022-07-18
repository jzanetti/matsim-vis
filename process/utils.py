from datetime import datetime, timedelta
from logging import INFO, Formatter, StreamHandler, getLogger

from process import DEFAULT_DATETIME_FMT, TRAVEL_TRAJ_INTERVAL_MINS


def str2datetime(datetime_str: str, str_fmt: str = DEFAULT_DATETIME_FMT) -> datetime:
    """convert string to datetime

    Args:
        datetime_str (str): datetime in string
        str_fmt (str, optional): string format. Defaults to DEFAULT_DATETIME_FMT.

    Returns:
        datetime: time in datetime
    """
    return datetime.strptime(datetime_str, str_fmt)


def get_diags_time_range(
    diags_start_datetime: datetime,
    diags_end_datetime: datetime, 
    time_interval_min: int = TRAVEL_TRAJ_INTERVAL_MINS) -> list:
    """Get matsim diags time range

    Args:
        diags_start_datetime (str): diags start time
        diags_end_datetime (str): diags end time

    Returns:
        list: the list contains all the diags time
    """
    proc_datetime = diags_start_datetime

    diags_time_range = []
    while proc_datetime <= diags_end_datetime:
        proc_datetime += timedelta(minutes=time_interval_min)
        diags_time_range.append(proc_datetime)
    
    return diags_time_range


def setup_logging():
    """set up logging system for tasks

    Returns:
        object: a logging object
    """
    formatter = Formatter("%(asctime)s - %(name)s.%(lineno)d - %(levelname)s - %(message)s")
    ch = StreamHandler()
    ch.setLevel(INFO)
    ch.setFormatter(formatter)
    logger = getLogger()
    logger.setLevel(INFO)
    logger.addHandler(ch)

    return logger


def get_xy_range(all_links: dict, buffer: float = 200) -> dict:
    """get xy range from nodes

    Args:
        all_links (dict): all links information

    Returns:
        dict: the xy range
    """

    max_x = 0
    max_y = 0
    min_x = 99999999999.0
    min_y = 99999999999.0
    for proc_node in all_links["nodes"]:

        proc_x = all_links["nodes"][proc_node]["x"]
        proc_y = all_links["nodes"][proc_node]["y"]

        if proc_x > max_x:
            max_x = proc_x
        
        if proc_x < min_x:
            min_x = proc_x

        if proc_y > max_y:
            max_y = proc_y
        
        if proc_y < min_y:
            min_y = proc_y
    
    return {
        "x": {"min": min_x - buffer, "max": max_x + buffer},
        "y": {"min": min_y - buffer, "max": max_y + buffer}
    }
