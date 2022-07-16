Installation
=====

**MATSim-VIS** should be installed through conda

First we need to create an environment containing all the dependancies:

.. code-block:: bash

    conda env create -f env.yml


Then the package can be installed via:

.. code-block:: bash

    conda build .
    conda install -f <build_path>

where ``<build_path>`` is the zipped package path, e.g., ``conda-bld/linux-64/matsim-vis-0.0.1-py310_0.tar.bz2``
