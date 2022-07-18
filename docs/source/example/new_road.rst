How about a new road
=====

In this example we want to build a road connecting the node 6 and 10, and we would like to
simulate how the traffic flow would change with this road

The new road to be built is shown below:

.. image:: matsim_village2.PNG
   :width: 600px
   :height: 640px
   :scale: 100 %
   :alt: alternate text
   :align: center

The accumulated traffic loads differences are shown below:

.. image:: with_new_roads.gif
   :width: 330px
   :height: 300px
   :scale: 100 %
   :alt: alternate text
   :align: left
.. image:: without_new_roads.gif
   :width: 330px
   :height: 300px
   :scale: 100 %
   :alt: alternate text
   :align: left

Of course many other analysis can be done. The codes for creating the above comparisons are:

.. code-block:: python

   from process.agent import (
      get_agent_movement,
      get_all_agents,
      select_agents,
      update_link_name_with_nodes,
   )
   from process.facility import get_facility
   from process.network import (
      get_accumulated_traffic,
      get_link_density,
      get_links_with_the_same_nodes,
      get_network,
   )
   from process.plans import get_plans
   from process.utils import get_diags_time_range, setup_logging, str2datetime
   from process.vis.link_density import plot_link_density

   # export PYTHONPATH=/home/szhang/Github/matsim-vis:$PYTHONPATH
   # xml_path = "/home/szhang/Github/matsim-example-project/output/output_events.xml.gz"
   plans_path = "data/example2/output_plans.xml.gz"
   network_path = "data/example2/output_network.xml.gz"
   facility_path = "data/example2/output_facilities.xml.gz"
   diags_start_datetime = "07:30:00"
   diags_end_datetime = "08:30:00"
   output_interval_mins = 2
   accum_traffic = True

   logger = setup_logging()
   output_path = "docs/source/without_new_roads.gif"

   diags_start_datetime = str2datetime(diags_start_datetime)
   diags_end_datetime = str2datetime(diags_end_datetime)

   agents = select_agents(get_all_agents(plans_path))

   logger.info("read all facilities ...")
   all_facilities = get_facility(facility_path)

   logger.info("read all networks ...")
   all_links = get_network(network_path)

   logger.info("get links with the shared nodes ...")
   links_with_the_same_nodes = get_links_with_the_same_nodes(all_links)

   logger.info("obtain time range ...")
   all_times = get_diags_time_range(diags_start_datetime, diags_end_datetime)

   agent_movements = {}
   for proc_agent in agents:
      all_tasks, _ = get_plans(plans_path, proc_agent)
      agent_movements[proc_agent] = get_agent_movement(all_tasks, all_links)
      agent_movements[proc_agent] = update_link_name_with_nodes(
         agent_movements[proc_agent], links_with_the_same_nodes)



   link_density = get_link_density(
      diags_start_datetime, 
      diags_end_datetime, 
      output_interval_mins,
      agent_movements,
      list(links_with_the_same_nodes.keys()))

   if accum_traffic:
      link_density = get_accumulated_traffic(link_density)

   plot_link_density(link_density, all_links, all_facilities, accum_traffic=accum_traffic, output_path=output_path, density_max=50.0)
