Traffic load
=====

We can calculate the number of vehicles passing through a link during a period.

First we need to import necessary dependancies

.. code-block:: python

    from process.agent import get_agent_movement, get_all_agents, select_agents
    from process.facility import get_facility
    from process.network import get_accumulated_traffic, get_link_density, get_network
    from process.plans import get_plans
    from process.utils import get_diags_time_range, setup_logging, str2datetime
    from process.vis.link_density import plot_link_density


Input files, including the simulation period must be defined

.. code-block:: python

    plans_path = "data/example1/output_plans.xml.gz"
    network_path = "data/example1/output_network.xml.gz"
    facility_path = "data/example1/output_facilities.xml.gz"
    output_path = "etc/animation2.gif"
    diags_start_datetime = "07:30:00"
    diags_end_datetime = "08:30:00"
    output_interval_mins = 2

Finally we can produce the animation for links (``vehicles/output_interval_mins``) with:

.. code-block:: python

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

    accum_traffic = False

    if accum_traffic:
        link_density = get_accumulated_traffic(link_density)

    plot_link_density(link_density, all_links, all_facilities, accum_traffic=accum_traffic, output_path=output_path)

.. only:: html

   .. figure:: animation4.gif

      The instantaneous traffic load between 07:30:00 and 08:30:00

Note that if we set ``accum_traffic=True``, we can get the accumulated traffic load as:

.. only:: html

   .. figure:: animation2.gif

      The accumulated traffic load between 07:30:00 and 08:30:00
