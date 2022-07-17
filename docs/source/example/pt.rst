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
