Public transportation
=====

A simple (unrealistic) example is used to show how the village moves with and without public transportation

In MATSim, the following scoring scheme is used (again, it is not realistic ...)

.. code-block:: xml

    <module name="planCalcScore">
        <param name="learningRate" value="1.0" />
        <param name="BrainExpBeta" value="2.0" />
        <param name="lateArrival" value="-18" />
        <param name="earlyDeparture" value="-0" />
        <param name="performing" value="+6" />
        <param name="waiting" value="-1" />

        <parameterset type="modeParams">
            <param name="mode" value="car"/>
            <param name="marginalUtilityOfDistance_util_m" value="-10.0" />
        </parameterset>

        <parameterset type="modeParams">
            <param name="mode" value="walk"/>
            <param name="marginalUtilityOfDistance_util_m" value="5.0" />
        </parameterset>

        <parameterset type="modeParams">
            <param name="mode" value="pt"/>
            <param name="marginalUtilityOfDistance_util_m" value="10.0" />
        </parameterset>

In terms of replanning, the following strategy is used:

.. code-block:: xml

	<module name="strategy">
		<param name="maxAgentPlanMemorySize" value="5" /> <!-- 0 means unlimited -->

		<param name="ModuleProbability_1" value="0.8" />
		<param name="Module_1" value="BestScore" />

		<param name="ModuleProbability_2" value="0.2" />
		<param name="Module_2" value="ChangeTripMode" />

		<param name="ModuleProbability_3" value="0.0" />
		<param name="Module_3" value="TimeAllocationMutator" />

	</module>

See the relevant `transitSchedule <https://github.com/jzanetti/matsim-vis/blob/master/etc/matsim/transitSchedule.xml>`_ 
and `transitVehicles <https://github.com/jzanetti/matsim-vis/blob/master/etc/matsim/transitVehicles.xml>`_ for more details.

.. only:: html

   .. figure:: animation_pt.gif
   .. figure:: animation_without_pt.gif

      The vehicles movements between 07:30:00 and 08:00:00
