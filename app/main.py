from ha_mqtt_discoverable import Settings, DeviceInfo
from ha_mqtt_discoverable.sensors import SensorInfo, Sensor
import socket
import enum
import time
import typing
import getpass
import glob
import os

CONFIG_MQTT_HOST = "homeassistant.home"
CONFIG_UPDATE_INTERVAL_S = 20

class SensorInfoExtra(SensorInfo):
    options: typing.List[str]
    expire_after: int

class Status(enum.Enum):
    AVAILABLE = ("availability: Available", "available")
    BUSY = ("availability: Busy", "busy")
    DO_NOT_DISTURB = ("availability: DoNotDisturb", "do_not_disturb")
    BE_RIGHT_BACK = ("availability: BeRightBack", "be_right_back")
    #ON_THE_PHONE = ("Added DoNotDisturb", "on_the_phone")
    #PRESENTING = ("Added Presenting", "presenting")
    IN_A_MEETING = ("Added InAMeeting", "in_a_meeting")
    AWAY = ("availability: Away", "away")
    OFFLINE = ("availability: Offline", "offline")

    def __new__(cls, search_str, value):
        obj = object.__new__(cls)
        obj._value_ = value
        obj._search_str = search_str
        return obj
    
    def get_search_str(self) -> str:
        return self._search_str
    
    def get_state(self) -> str:
        return self._value_

class TeamsStatus():

    def __init__(self):
        
        user_name = getpass.getuser()

        # Intialize the filepath variable
        self._filepath = f"c:\\Users\\{user_name}\\AppData\\Local\\Packages\\MSTeams_8wekyb3d8bbwe\\LocalCache\\Microsoft\\MSTeams\\Logs\\"


    def find_newest_teams_log(self, log_folder) -> str|None:
        # Use glob to find all log files in the specified folder
        log_files = glob.glob(os.path.join(log_folder, 'MSTeams_*.log'))
        
        # Check if any log files were found
        if not log_files:
            print("No log files found in the specified folder.")
            return None
        
        # Sort log files by name and get the last one (newest)
        newest_log = sorted(log_files)[-1]
        return newest_log




    def get_status(self) -> Status:
        current_state = Status.OFFLINE

        # Look for this string in the MSFT Teams log file
        indicator = "native_modules::UserDataCrossCloudModule: Received Action: UserPresenceAction:"

        newest_log_file = self.find_newest_teams_log(self._filepath)
        if not newest_log_file:
            print(f"Failed to find teams log in {self._filepath}")
            return current_state
        print(f"The newest log file is: {newest_log_file}")

        # Open the log file
        log_file = open(newest_log_file, "r")

        # Loop through the file line by line
        last_line = ""
        for line in log_file:
            # Find
            if indicator in line:
                last_line = line

        # Loop through list of possible status, if the last instance indicator 
        # finds a match, return that status
        print(f"last indicator: {last_line}")
        for status in Status:
            if last_line.__contains__(status.get_search_str()):
                current_state = status
                print(f"Found Status: {current_state}")
                break
        # closing text file	
        log_file.close()
        return current_state

class TeamsStatePublisher():

    def __init__(self, mqtt_host: str) -> None:
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
    
    def send_state(self, state: Status) -> None:
        self._sensor.set_state(state.value)



def main():
    
    publisher = TeamsStatePublisher(CONFIG_MQTT_HOST)
    teamsStatus = TeamsStatus()
    while True:
        current_state = teamsStatus.get_status()
        publisher.send_state(current_state)
        time.sleep(CONFIG_UPDATE_INTERVAL_S)

if __name__ == "__main__":
    main()
