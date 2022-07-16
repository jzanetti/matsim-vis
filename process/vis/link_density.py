import matplotlib.patheffects as pe
from matplotlib import cm, colors
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.pyplot import close, colorbar, plot, subplots
from process.network import get_link_coords, get_the_max_traffic_from_link
from process.utils import get_xy_range


def plot_link_density(link_density: dict, all_links: dict, all_facilities: dict, accum_traffic: bool = False, output_path: str = "test.gif", fps: int = 10):
    """Plot agent movement and save it in a mp4 format

    Args:
        agent_movement (dict): the dict contains the agents movements
        all_links (dict): all links information
        all_facilities (dict): facilities to be shown

    Returns:
        _type_: _description_
    """
    fig, ax = subplots()
    title = ax.text(0.5, 1.02, "", # bbox={'facecolor':'w', 'alpha':0.5, 'pad':5},
                    transform=ax.transAxes, ha="center")
    ln, = plot([], [], 'ro')

    title_prefix = "Traffic load"
    if accum_traffic:
        title_prefix = "Accumulated traffic load"

    my_cmap = cm.Blues
    my_norm = colors.Normalize(vmin=0.0, vmax=get_the_max_traffic_from_link(link_density) * 0.3)
    colorbar(cm.ScalarMappable(norm=my_norm, cmap=my_cmap), fraction=0.02, orientation="vertical", label="Traffic load")

    link_density = postproc_link_density(link_density, all_links)
    xy_range = get_xy_range(all_links)
    
    def init():
        ax.set_xlim(xy_range["x"]["min"], xy_range["x"]["max"])
        ax.set_ylim(xy_range["y"]["min"], xy_range["y"]["max"])
        ax.invert_yaxis()
        for proc_facility_name in all_facilities:
            proc_facility = all_facilities[proc_facility_name]
            ax.text(proc_facility["x"], proc_facility["y"], proc_facility_name, zorder=30)

        ax.set_xlabel("x")
        ax.set_ylabel("y")

        return ln,

    def update(i):

        frame = link_density[i]
        ref_link = list(frame.keys())[0]
        title.set_text("{title_prefix} at {t}".format(
            title_prefix=title_prefix,
            t = frame[ref_link]["time"].strftime("%H:%M")))
        for link_name in frame:
            xdata = [frame[link_name]["coords"]["x"]["start"], frame[link_name]["coords"]["x"]["end"]]
            ydata = [frame[link_name]["coords"]["y"]["start"], frame[link_name]["coords"]["y"]["end"]]
            ax.plot(
                xdata, 
                ydata,
                linewidth=7.5,
                color=my_cmap(my_norm(frame[link_name]["num"])),
                path_effects=[pe.Stroke(linewidth=10.0, foreground="g"), pe.Normal()])
        return ln,

    ani = FuncAnimation(fig, update, frames=len(link_density),
                        init_func=init, blit=True)

    writervideo = FFMpegWriter(fps=fps)

    ani.save(output_path, writer=writervideo)
    close()


def postproc_link_density(link_density: dict, all_links: dict) -> list:
    """Link density postprocessing

    Args:
        link_density (dict): link density in a dict
        all_links (dict): all links information in a dict

    Returns:
        list: the postprocessed links
    """
    all_link_densities = []

    for proc_link_time in link_density:
        out = {}
        for proc_link_name in link_density[proc_link_time]:
            proc_link_coords = get_link_coords(all_links, proc_link_name)
            out[proc_link_name] = {
                "time": proc_link_time,
                "num": link_density[proc_link_time][proc_link_name],
                "coords": proc_link_coords
                }

        all_link_densities.append(out)

    return all_link_densities
