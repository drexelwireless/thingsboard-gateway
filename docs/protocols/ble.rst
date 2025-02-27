BLE Setup
====================


Installation Guide
--------------
1. Install linux and python libraries

.. code-block:: sh

    sudo apt install -y libglib2.0-dev zlib1g-dev
    sudo pip3 install bleak

Connector Configuration:
--------------
1. Open tb_gateway.yaml

.. code-block:: sh

    cd thingsboard-gateway/thingsboard-gateway/thingsboard_gateway/config/
    nano tb_gateway.yaml
    
2. Uncomment the following section:

.. code-block::

    -
        name: BLE Connector
        type: ble
        configuration: ble.json
        
3. Save and close the file. Afterward, you must restart the thingsboard service before the changes take effect.

JSON File Configuration Guide
--------------
1. Navigate and open ble.json file with text editor

.. code-block:: sh

    cd thingsboard-gateway/thingsboard-gateway/thingsboard_gateway/config/
    nano ble.json

This is sample basic configuration JSON file for BLE.

.. code-block:: sh

    {
    "name": "BLE Connector",
    "passiveScanMode": true,
    "showMap": false,
    "scanner": {
        "timeout": 10000
    },
    "devices": [
        {
        "name": "SENSOR_NAME",
        "MACAddress": "MAC_ADDRESS",
        "pollPeriod": 10000,
        "showMap": false,
        "timeout": 10000,
        "telemetry": [
            {
            "key": "TELEMETRY_NAME",
            "method": "METHOD",
            "characteristicUUID": "UUID",
            "valueExpression": "VALUE_EXPRESSION"
            }
        ],
        "attributes": [
            {
            "key": "Device Name",
            "method": "read",
            "characteristicUUID": "00002a00-0000-1000-8000-00805f9b34fb",
            "valueExpression": "[:]"
            }
        ],
        "attributeUpdates": [
            {
            }
        ],
        "serverSideRpc": [
            {
            }
        ]
        }
    ]
    }

2. Edit device object

* Enter the name of device where ``SENSOR_NAME`` is, in double quotes, as you want it to appear in Thingsboard
* Enter the BLE hardware  mac address of the device in ``MAC_ADDRESS``

3. Telemetry

**All four fields in telemetry, key, method, characteristicUUID, and valueExpression, need to be filled out.**

* Key or ``TELEMETRY_NAME`` is the name of the telemetry that will be shown in thingsboard.
* ``METHOD`` is how the gateway will retrieve  the data. (read, write, or notify)
* CharacteristicUUID or ``UUID`` is the UUID where the telemetry is store on the senor.
* ``VALUE_EXPRESSION`` is how the byte data from the senor will be displayed in thingsboard. This is similar to python.
    * ("[0:1]", "[:]", "[0, 1, 2, 3]")


Web Portal Configuration Guide
--------------

The other way to connect a BLE senors is to use our `VarIoT web portal <http://variot.ece.drexel.edu:5500/>`_. The same information will be needed as in the JSON configuration method, however this is a more friendly GUI way.

#. Once at the VarIoT portal, login and click ``Add Device``.
#. Select the gateway you want to add the BLE sensor too from the drop down.
#. Type in senor name in the ``Device name`` field and select the BLE protocol from the dropdown.
#. When ``Bluetooth`` is selected ``MAC Address`` and ``Attribute UUID`` will appear. Enter the device's BLE hardware MAC address for the MAC address and ``00002a00-0000-1000-8000-00805f9b34fb`` for the Attribute UUID.
#. Enter number of telemetry UUIDs you will be using then click ``Next``.
    * Number of differnet UUIDs to collect telemetry from.
#. On the next page fill in the ``Telemetry UUID``, ``Telemetry key``, ``Telemetry value expression``. and ``Telemetry method``.
    * ``Telemetry UUID`` is the UUID address where the telemetry is located on the sensor.
    * ``Telemetry key`` is the name for the telemetry how it will be displayed in thingsboard.
    * ``Telemetry value expression`` is the python bracket represtention of how you want to show the bytes in the dashboard.
    * ``Telemetry method`` is how the gateway will retrieve  the data. (read, write, or notify)
#. When complete submit form.
