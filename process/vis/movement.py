import matplotlib.patheffects as pe
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.pyplot import close, plot, subplots
from process.network import get_link_coords
from process.utils import get_xy_range


def get_postp_movements_times(agent_movements: dict, pt_movements: dict) -> list:

    if len(agent_movements) > 0:
        ref_agent = list(agent_movements.keys())[0]
        all_agent_times = sorted(list(agent_movements[ref_agent].keys()))

    if len(pt_movements) > 0:
        ref_pt_id = list(pt_movements.keys())[0]
        all_pt_times = sorted(list(pt_movements[ref_pt_id].keys()))

    if len(agent_movements) > 0 and len(pt_movements) > 0:
        if set(all_agent_times) == set(all_pt_times):
            return all_agent_times
    else:
        if len(agent_movements) > 0:
            return all_agent_times
        if len(pt_movements) > 0:
            return all_pt_times
    
    raise Exception("seems the input times for movements are not identical ...")


def postproc_agent_movements(agent_movements: dict, pt_movements: dict) -> dict:
    """Postprocess agent_movements data and write it 
    to a format that can be easily processed by FuncAnimation

    Args:
        agent_movements (dict): the original agent movements data
        pt_movements (dict): the original pt movements data

    Returns:
        dict: the dict contains the processed data
    """

    all_agent_times = get_postp_movements_times(agent_movements, pt_movements)

    output = []

    for proc_time in all_agent_times:
        proc_data = {}
        for proc_agent in agent_movements:
            proc_data[proc_agent] = {
                "id": proc_agent,
                "time": proc_time,
                "mode": "car",
                "x": agent_movements[proc_agent][proc_time]["x"],
                "y": agent_movements[proc_agent][proc_time]["y"],
            }
        
        for proc_pt in pt_movements:
            proc_data[proc_pt] = {
                "id": proc_pt,
                "time": proc_time,
                "mode": "pt",
                "x": pt_movements[proc_pt][proc_time]["x"],
                "y": pt_movements[proc_pt][proc_time]["y"],
            }
        output.append(proc_data)
    
    return output


def plot_movement(
    agent_movements: dict, 
    pt_movements: dict, 
    all_links: dict, 
    all_facilities: dict, 
    output_path: str = "test.mp4"):
    """Plot agent movement and save it in a mp4 format

    Args:
        agent_movement (dict): the dict contains the agents movements
        all_links (dict): all links information
        all_facilities (dict): facilities to be shown

    Returns:
        _type_: _description_
    """
    all_movements = postproc_agent_movements(agent_movements, pt_movements)

    fig, ax = subplots()
    title = ax.text(0.5, 1.02, "", # bbox={'facecolor':'w', 'alpha':0.5, 'pad':5},
                    transform=ax.transAxes, ha="center")

    ln_car, = plot([], [], 'bo')
    ln_pt, = plot([], [], 'ro')

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
        ln_pt.set_label("pt")
        ln_car.set_label("car")
        ax.legend()

        return ln_car, ln_pt

    def update(frame):
        ref_agent = list(frame.keys())[0]
        title.set_text("car/pt movement at {t}".format(t = frame[ref_agent]["time"].strftime("%H:%M")))

        xdata1 = []
        ydata1 = []
        for id in frame:
            if frame[id]["mode"] == "car":
                xdata1.append(frame[id]["x"])
                ydata1.append(frame[id]["y"])

        ln_car.set_data(xdata1, ydata1)
        ln_car.set_color("b")
        ln_car.set_marker("o")
        ln_car.set_markeredgecolor("k")
        ln_car.set_markersize(15)
        ln_car.set_zorder(10)

        xdata2 = []
        ydata2 = []
        for id in frame:
            if frame[id]["mode"] == "pt":
                xdata2.append(frame[id]["x"])
                ydata2.append(frame[id]["y"])

        ln_pt.set_data(xdata2, ydata2)
        ln_pt.set_color("r")
        ln_pt.set_marker("o")
        ln_pt.set_markeredgecolor("k")
        ln_pt.set_markersize(15)
        ln_pt.set_zorder(10)

        return ln_car, ln_pt

    ani = FuncAnimation(fig, update, frames=all_movements,
                        init_func=init, blit=True)

    writervideo = FFMpegWriter(fps=15)

    ani.save(output_path, writer=writervideo)
    close()
