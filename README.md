# Homeassistant Teams Indicator

This projects reads the teams log file periodically and sets the status accordingly in Homeassistant via MQTT.

## Configuration

Set Homeassistant mqtt broker to connect to by modyfing the following variable to your broker host or ip:

```python
CONFIG_MQTT_HOST = "homeassistant.home"
```

## Run

Create a new environment.

```batch
python -m venv .venv
```

Install the dependencies

```batch
.\venv\Scripts\activate.bat
pip install -r requirements.txt
```

Run the script with

```batch
run.bat
```

If everything worked, you should see a new device in homeasssitant under Settings -> Devices & Servces -> Devices called **Microsft Teams on [host]** with a state entity that reflects the state currently set in Microsft Teams.
