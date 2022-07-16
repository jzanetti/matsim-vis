from statistics import mean

from matplotlib.pyplot import close, plot, savefig, title, xlabel, ylabel


def postproc_travel_time(agent_travel_time: dict) -> list:
    """Convert travel time from dict to list

    Args:
        agent_travel_time (dict): agent travel time in a dict

    Returns:
        list: list contains travel time
    """
    travel_time = []
    for agent in agent_travel_time:
        travel_time.append(agent_travel_time[agent])
    
    return travel_time


def plot_travel_time(agent_travel_time: dict, output_path: str = "test.png"):
    """Plot travel time

    Args:
        agent_travel_time (dict): _description_
    """
    travel_time = postproc_travel_time(agent_travel_time)
    plot(travel_time, "b")
    mean_travel_time = mean(travel_time)
    plot([0, len(travel_time)], [mean_travel_time, mean_travel_time], "r--")
    xlabel("agent")
    ylabel("travel time (minutes)")
    title("Travel time for agents")
    savefig(output_path, bbox_inches="tight")
    close()


