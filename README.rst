==========
pyfluora
==========

Python library for controlling Fluora LED plant fixtures via UDP communication.

Features
========

* Send commands to Fluora LED plants (power, brightness, animations, etc.)
* Receive real-time state updates from the plant
* Thread-safe UDP communication
* Context manager support for automatic resource cleanup

Installation
============

.. code-block:: bash

    pip install pyfluora

Basic Usage
===========

.. code-block:: python

    from fluoraapi import FluoraAPI

    # Initialize the API (does not start server automatically)
    api = FluoraAPI(
        plant_ip="192.168.1.100",
        plant_port=4210,
        server_address="0.0.0.0",
        server_port=12345
    )

    # Start listening for state updates
    api.start_server()

    # Send commands
    api.power(1)  # Turn on
    api.brightness_set(0.8)  # Set brightness to 80%
    api.animation_set_manual("RAINBOW")

    # Get current state
    state = api.plant_state
    if state:
        print(f"Brightness: {state.brightness}")
        print(f"Animation: {state.active_animation}")

    # Stop the server when done
    api.stop_server()

Context Manager Usage
=====================

.. code-block:: python

    from fluoraapi import FluoraAPI

    # Automatically starts/stops server
    with FluoraAPI("192.168.1.100", 4210, "0.0.0.0", 12345) as api:
        api.power(1)
        api.brightness_set(0.5)
        # Server automatically stopped when exiting context

Requirements
============

* Python 3.10+
* python-osc
* python-box

License
=======

This project is licensed under the MIT License.
