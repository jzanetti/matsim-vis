from process.agent import get_agent_movement, get_all_agents, select_agents
from process.facility import get_facility
from process.network import get_accumulated_traffic, get_link_density, get_network
from process.plans import get_plans
from process.utils import get_diags_time_range, setup_logging, str2datetime
from process.vis.link_density import plot_link_density

# export PYTHONPATH=/home/szhang/Github/matsim-vis:$PYTHONPATH
# xml_path = "/home/szhang/Github/matsim-example-project/output/output_events.xml.gz"
plans_path = "data/example1/output_plans.xml.gz"
network_path = "data/example1/output_network.xml.gz"
facility_path = "data/example1/output_facilities.xml.gz"
diags_start_datetime = "07:30:00"
diags_end_datetime = "08:30:00"
output_interval_mins = 2
accum_traffic = False

logger = setup_logging()
output_path = "etc/animation4.gif"

diags_start_datetime = str2datetime(diags_start_datetime)
diags_end_datetime = str2datetime(diags_end_datetime)

agents = select_agents(get_all_agents(plans_path))

logger.info("read all facilities ...")
all_facilities = get_facility(facility_path)

logger.info("read all networks ...")
all_links = get_network(network_path)

logger.info("obtain time range ...")
all_times = get_diags_time_range(diags_start_datetime, diags_end_datetime)

agent_movements = {}
for proc_agent in agents:
    all_tasks = get_plans(plans_path, proc_agent)
    agent_movements[proc_agent] = get_agent_movement(all_tasks, all_links)


link_density = get_link_density(
    diags_start_datetime, 
    diags_end_datetime, 
    output_interval_mins,
    agent_movements,
    list(all_links["links"].keys()))

if accum_traffic:
    link_density = get_accumulated_traffic(link_density)

plot_link_density(link_density, all_links, all_facilities, accum_traffic=accum_traffic, output_path=output_path)
