Installation of Flask Web Portal
================================

Here you will find instructions on how to install Flask web portal.

Prerequisite 
------------
#. Clone the repository :code:`git clone https://github.com/drexelwireless/VarIOT_Portal.git`
#. Install Python 3.7 or higher
#. (Linux) Might require to install :code:`apt-get install python-venv`

Setting up Virtual Environment
------------------------------
Windows
^^^^^^^
.. code-block:: sh

  virtualenv variot_portal_env
  ./variot_portal_env/source variot_portal_env/Scripts/activate
  pip install -r requirements.txt

Linux/Mac
^^^^^^^^^
.. code-block:: sh

  virtualenv -p <python_version> variot_portal_env
  source variot_portal_env/bin/activate
  variot_portal_env/bin/pip3 install -r requirements.txt

Example of <python_version>: :code:`virtualenv -p python3.7 variot_portal_env`

Configuration
-------------
#. Edit the :code:`zigbee2mqtt` configuration file (on Linux this is probably :code:`/opt/zigbee2mqtt/data/configuration.yaml`) to reflect the following in the :code:`advanced` section:
    ::

      advanced:
        log_level: debug
#. Append the following lines to :code:`/etc/mosquitto/mosquitto.conf`:
    ::

      listener 1883
      protocol mqtt
      allow_anonymous true

Run
---
.. code-block:: sh

  python run.py

Trouble Shooting - Linux
------------------------
If you get an error about "No module named ..." try

.. code-block:: sh

  variot_portal_env/bin/python3 run.py


Setup for ssh
-------------
Non-Linux
^^^^^^^^^
#. Generate public/private rsa key pair using :code:`ssh-keygen` if you don't have on your machine.
#. Go to :code:`~/.ssh`
#. Copy the content of your :code:`id_rsa.pub` file.
#. SSH to whichever gateway you are trying to access via ssh on the portal (such as adding a BLE device)
#. Go to :code:`~/.ssh` on the gateway
#. Add copied content from step 3 to the bottom of :code:`authorized_keys`

Linux
^^^^^
#. Generate public/private rsa key pair using :code:`ssh-keygen` if you don't have on your machine.
#. Run the following from your own machine: :code:`ssh-copy-id <user>@<host>` where :code:`<user>` is the username on the remote host, and :code:`<host>` is the host name or IP of the remote host