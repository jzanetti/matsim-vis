

import matplotlib.patheffects as pe
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.pyplot import close, plot, subplots
from process.network import get_link_coords
from process.utils import get_xy_range


def postproc_agent_movements(agent_movements: dict) -> dict:
    """Postprocess agent_movements data and write it 
    to a format that can be easily processed by FuncAnimation

    Args:
        agent_movements (dict): the original agent movements data

    Returns:
        dict: the dict contains the processed data
    """

    ref_agent = list(agent_movements.keys())[0]
    all_agent_times = sorted(list(agent_movements[ref_agent].keys()))

    output = []


    for proc_time in all_agent_times:
        proc_data = {}
        for proc_agent in agent_movements:
            proc_data[proc_agent] = {
                "agent": proc_agent,
                "time": proc_time,
                "x": agent_movements[proc_agent][proc_time]["x"],
                "y": agent_movements[proc_agent][proc_time]["y"],
            }
        
        output.append(proc_data)
    
    return output


def plot_agent_movement(agent_movements: dict, all_links: dict, all_facilities: dict, output_path: str = "test.mp4"):
    """Plot agent movement and save it in a mp4 format

    Args:
        agent_movement (dict): the dict contains the agents movements
        all_links (dict): all links information
        all_facilities (dict): facilities to be shown

    Returns:
        _type_: _description_
    """
    agent_movements = postproc_agent_movements(agent_movements)

    fig, ax = subplots()
    title = ax.text(0.5, 1.02, "", # bbox={'facecolor':'w', 'alpha':0.5, 'pad':5},
                    transform=ax.transAxes, ha="center")
    ln, = plot([], [], 'ro')

    xy_range = get_xy_range(all_links)

    def init():
        ax.set_xlim(xy_range["x"]["min"], xy_range["x"]["max"])
        ax.set_ylim(xy_range["y"]["min"], xy_range["y"]["max"])
        ax.invert_yaxis()
        for proc_link_name in all_links["links"]:

            proc_link_coords = get_link_coords(all_links, proc_link_name)
            ax.plot(
                [proc_link_coords["x"]["start"], proc_link_coords["x"]["end"]],
                [proc_link_coords["y"]["start"], proc_link_coords["y"]["end"]],
                linewidth=7.5,
                zorder=0,
                path_effects=[pe.Stroke(linewidth=10.0, foreground="g"), pe.Normal()]
            )

        for proc_facility_name in all_facilities:
            proc_facility = all_facilities[proc_facility_name]
            ax.text(proc_facility["x"], proc_facility["y"], proc_facility_name, zorder=30)

        ax.set_xlabel("x")
        ax.set_ylabel("y")

        return ln,

    def update(frame):
        ref_agent = list(frame.keys())[0]
        title.set_text("agenet movement at {t}".format(t = frame[ref_agent]["time"].strftime("%H:%M")))

        xdata = []
        ydata = []
        for agent in frame:
            xdata.append(frame[agent]["x"])
            ydata.append(frame[agent]["y"])

        ln.set_data(xdata, ydata)
        ln.set_color("b")
        ln.set_marker("o")
        ln.set_markeredgecolor("k")
        ln.set_markersize(15)
        ln.set_zorder(10)
        return ln,

    ani = FuncAnimation(fig, update, frames=agent_movements,
                        init_func=init, blit=True)

    writervideo = FFMpegWriter(fps=15)

    ani.save(output_path, writer=writervideo)
    close()
