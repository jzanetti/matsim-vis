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