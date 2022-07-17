from process.agent import get_agent_travel_time, get_all_agents, select_agents
from process.plans import get_unselected_and_selected_plans

plans_path = "data/example2/output_plans.xml.gz"
network_path = "data/example2/output_network.xml.gz"
facility_path = "data/example2/output_facilities.xml.gz"
diags_start_datetime = "07:30:00"
diags_end_datetime = "08:30:00"

# export PYTHONPATH=/home/szhang/Github/matsim-vis:$PYTHONPATH
agents = select_agents(get_all_agents(plans_path))

all_tasks = {}
agent_travel_time = {}
for person_id in agents:
    all_tasks[person_id] = get_unselected_and_selected_plans(plans_path, person_id)
    agent_travel_time[person_id] = {}
    for task_id in all_tasks[person_id]:
        agent_travel_time[person_id][task_id] = get_agent_travel_time(all_tasks[person_id][task_id])

x = 3
