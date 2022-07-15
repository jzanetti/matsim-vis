
from process.agent import get_agent_movement, interp_agent_movement
from process.facility import get_facility
from process.network import get_network
from process.plans import get_plans
from process.utils import get_diags_time_range, setup_logging
from process.vis import plot_agent_movement

# export PYTHONPATH=/home/szhang/Github/matsim-vis:$PYTHONPATH
# xml_path = "/home/szhang/Github/matsim-example-project/output/output_events.xml.gz"
plans_path = "/home/szhang/Github/matsim-example-project/output/output_plans.xml.gz"
network_path = "/home/szhang/Github/matsim-example-project/output/output_network.xml.gz"
facility_path = "/home/szhang/Github/matsim-example-project/output/output_facilities.xml.gz"
diags_start_datetime = "08:00:00"
diags_end_datetime = "08:30:00"
agents = ["p11", "p21", "p22", "p31", "p32", "p33", "p41", "p51", "p52", "p61", "p62"] # "p41", "p52", "p62"]
# agents = ["p51"] # "p41", "p52", "p62"
logger = setup_logging()
output_path = "test.gif"

logger.info("read all facilities ...")
all_facilities = get_facility(facility_path)

logger.info("read all networks ...")
all_links = get_network(network_path)

logger.info("obtain time range ...")
all_times = get_diags_time_range(diags_start_datetime, diags_end_datetime)

agent_movements = {}
for proc_agent in agents:
    all_tasks = get_plans(plans_path, proc_agent)
    agent_movement = get_agent_movement(all_tasks, all_links)
    agent_movements[proc_agent] = interp_agent_movement(agent_movement, all_times)

plot_agent_movement(agent_movements, all_links, all_facilities, output_path=output_path)

logger.info("animation is produced")
