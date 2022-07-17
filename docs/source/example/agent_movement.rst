Agents movements
=====

Here is an example showing the movements for all the agents in a map:

First we need to import the necessary dependancies:

.. code-block:: python

    from process.agent import (
        get_agent_movement,
        get_all_agents,
        interp_agent_movement,
        select_agents,
    )
    from process.facility import get_facility
    from process.network import get_network
    from process.plans import get_plans
    from process.utils import get_diags_time_range, setup_logging, str2datetime
    from process.vis.agent import plot_agent_movement

The path from the MATSim model output (including ``plan``, ``network`` and ``facility``) must be defined. We also need to define a period
covering the start and end time for the analysis.

.. code-block:: python

    plans_path = "data/example1/output_plans.xml.gz"
    network_path = "data/example1/output_network.xml.gz"
    facility_path = "data/example1/output_facilities.xml.gz"
    diags_start_datetime = "07:30:00"
    diags_end_datetime = "08:30:00"
    agents_ratio = 1.0
    output_path = "etc/animation.gif"

It may take a long period to extract and produce the movements for every agent in a simulation. In order to reduce the demands for 
computational resources, we can define how many agents we want to use in the analysis (defined by ``agents_ratio``, for example, 30%
agents will be used if we have ``agents_ratio = 0.3``).

We also need to specify the output path, where you can set the output format in either ``gif`` or ``mp4``.

The codes below will produce the animation for the agents movements:

.. code-block:: python

    diags_start_datetime = str2datetime(diags_start_datetime)
    diags_end_datetime = str2datetime(diags_end_datetime)

    agents = select_agents(get_all_agents(plans_path), agents_ratio)

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

    plot_agent_movement(agent_movements, {}, all_links, all_facilities, output_path=output_path)

.. only:: html

   .. figure:: animation.gif

      The agents movements between 07:30:00 and 08:30:00
