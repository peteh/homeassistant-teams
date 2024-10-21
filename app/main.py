from ha_mqtt_discoverable import Settings, DeviceInfo
from ha_mqtt_discoverable.sensors import SensorInfo, Sensor
import socket
import enum
import time
import typing
import getpass

class SensorInfoExtra(SensorInfo):
    options: typing.List[str]
    expire_after: int

class Status(enum.Enum):
    AVAILABLE = ("Added Available", "available")
    BUSY = ("Added Busy", "busy")
    DO_NOT_DISTURB = ("Added DoNotDisturb", "do_not_disturb")
    BE_RIGHT_BACK = ("Added BeRightBack", "be_right_back")
    ON_THE_PHONE = ("Added DoNotDisturb", "on_the_phone")
    PRESENTING = ("Added Presenting", "presenting")
    IN_A_MEETING = ("Added InAMeeting", "in_a_meeting")
    AWAY = ("Added Away", "away")
    OFFLINE = ("Offline", "offline")

    def __new__(cls, search_str, value):
        obj = object.__new__(cls)
        obj._value_ = value
        obj._search_str = search_str
        return obj
    
    def get_search_str(self) -> str:
        return self._search_str
    
    def get_state(self) -> str:
        return self._value_

# Helper class with functions parse the Teams log file and assign an RGB value to the current status.

class TeamsStatus():

    def __init__(self, ):
        
        user_name = getpass.getuser()

        # Intialize the filepath variable
        self._filepath = f"C:\\Users\\{user_name}\\AppData\\Roaming\\Microsoft\\Teams\\logs.txt"
        #self._filepath = "c:\\Users\\micro\\AppData\\Local\\Packages\\MSTeams_8wekyb3d8bbwe\\LocalCache\\Microsoft\\MSTeams\\Logs\\MSTeams_2024-10-21_20-33-49.00.log"
        

    def get_status(self):
        # Look for this string in the MSFT Teams log file
        indicator = "StatusIndicatorStateService: Added "

        # Open the log file
        log_file = open(self._filepath, "r")

        # Loop through the file line by line
        last_line = ""
        for line in log_file:
            # Find
            if indicator in line:
                last_line = line

        # Loop through list of possible status's, if the last instance indicator 
        # finds a match, return that status
        current_state = Status.OFFLINE
        for status in Status:
            if last_line.__contains__(status.get_search_str()):
                current_state = status
                break
        # closing text file	
        log_file.close()
        return current_state

class TeamsStatePublisher():
    def __init__(self, mqtt_host: str, sensor_name: str) -> None:
        self._mqtt_settings = Settings.MQTT(host=mqtt_host)
        self._hostname = socket.gethostname()
        device_info = DeviceInfo(name=f"Microsoft Teams on {self._hostname}" , identifiers=f"msteams-{self._hostname}")
        
        
        # Associate the sensor with the device via the `device` parameter
        # `unique_id` must also be set, otherwise Home Assistant will not display the device in the UI
        sensor_info = SensorInfoExtra(name=f"State", 
                                            device_class="enum",
                                            unique_id=f"msteams-{self._hostname}-state",
                                            icon="mdi:microsoft-teams",
                                            options = [status.value for status in Status],
                                            device=device_info,
                                            expire_after=10 * 60
                                            )
        sensor_settings = Settings(mqtt=self._mqtt_settings, entity=sensor_info)

        # Instantiate the sensor
        self._sensor = Sensor(sensor_settings)
        self._sensor.write_config()
    
    def send_state(self, state: Status):
        self._sensor.set_state(state.value)


publisher = TeamsStatePublisher("homeassistant.home")
teamsStatus = TeamsStatus()
while True:
    current_state = teamsStatus.get_status()
    publisher.send_state(current_state)
    time.sleep(10)