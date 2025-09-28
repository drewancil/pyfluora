"""Python library to control Fluora LED plant."""

import logging
import time

from pythonosc.udp_client import SimpleUDPClient
from fluoraapi.enums import AnimationMode, FluoraAnimations


class FluoraClient:
    """Class to issue commands with the Fluora plant API via OSC/UDP."""

    def __init__(self, plant_ip: str, plant_port: int) -> None:
        self.client_ip_address = plant_ip
        self.client_udp_port = plant_port
        self.client = SimpleUDPClient(plant_ip, plant_port)
        self._animation_mode: int = 0

        root = logging.getLogger()
        logging.debug("FluoraClient: Logging handlers configured: %s", root.handlers)

    @property
    def effect_list(self) -> list[str]:
        """Return the list of supported effects."""
        return [effect.name.title() for effect in FluoraAnimations]

    def custom_command(self, route: str, value: float) -> None:
        """Send a custom command to the plant."""
        logging.info("Client: Command custom: (%s) %0.f", route, value)
        try:
            self.client.send_message(route, [value, 0])
        except Exception as e:
            logging.error("Failed to send custom command: %s", e)
            raise

    def power(self, power_state: int) -> None:
        """Change the power state of the plant."""
        if power_state in (0, 1):
            logging.info("Client: Power %s", power_state)
            try:
                self.client.send_message("/SyYOTiXjQBjW", [power_state, power_state])
            except Exception as e:
                logging.error("Failed to change power state: %s", e)
                raise
        else:
            raise ValueError("Power must be 0 (Off) or 1 (On)")

    def light_sensor(self, sensor_state: int) -> None:
        """Change the light sensor state of the plant."""
        if sensor_state in (0, 1):
            logging.info("Client: Light sensor %s", sensor_state)
            try:
                self.client.send_message("/S53upLXAu7vg", [sensor_state, sensor_state])
            except Exception as e:
                logging.error("Failed to change light sensor state: %s", e)
                raise
        else:
            raise ValueError("Light Sensor must be 0 (Off) or 1 (On)")

    def reboot(self) -> None:
        """Reboot the plant."""
        logging.info("Client: Reboot")
        try:
            self.client.send_message("/pixelair/engine/reboot", [1, 0])
        except Exception as e:
            logging.error("Failed to reboot plant: %s", e)
            raise

    def brightness_set(self, brightness_level: float) -> None:
        """Set the brightness level of the plant."""
        if brightness_level < 0.00 or brightness_level > 1.00:
            raise ValueError("Brightness must be between 0 and 1")
        logging.info("Client: Set Brightness %s", brightness_level)
        try:
            self.client.send_message("/Uv7aMFw5P2lX", [brightness_level, 0])
        except Exception as e:
            logging.error("Failed to set brightness: %s", e)
            raise

    def animation_set_mode(self, mode: str) -> None:
        """Set the animation mode."""
        if any(x for x in AnimationMode if x.name == mode):
            try:
                logging.info("Client: Set mode %s", mode)
                self.client.send_message(
                    "/iwaaMkVzOfUM", [AnimationMode[mode].value, 0]
                )
                self._animation_mode = AnimationMode[mode].value
            except Exception as e:
                logging.error("Failed to set animation mode: %s", e)
                raise
        else:
            raise LookupError(f"Animation mode {mode} is unknown.")

    def animation_set(self, animat_name: str) -> None:
        """Set an animation."""
        if any(x for x in FluoraAnimations if x.name == animat_name.upper()):
            animation_num = int(FluoraAnimations[animat_name.upper()].value)

            # auto mode
            if animation_num == 0:
                try:
                    self.animation_set_mode("AUTO")
                    logging.info("Client: Set animation %s", animat_name)
                except Exception as e:
                    logging.error("Failed to set animation mode to AUTO: %s", e)
                    raise

            # manual mode animations
            if animation_num in range(100, 199):
                try:
                    self.animation_set_mode("MANUAL")
                    self.client.send_message("/tdU63ENxy4UG", [animation_num - 100, 0])
                    logging.info("Client: Set animation %s", animat_name)
                except Exception as e:
                    logging.error("Failed to set animation mode to MANUAL: %s", e)
                    raise

            # scene mode animations
            if animation_num in range(200, 299):
                try:
                    self.animation_set_mode("SCENE")
                    self.client.send_message("/EpUwZA1GSPjO", [animation_num - 200, 0])
                    logging.info("Client: Set animation %s", animat_name)
                except Exception as e:
                    logging.error("Failed to set animation mode to SCENE: %s", e)
                    raise
        else:
            raise LookupError(f"Animation {animat_name} is unknown.")

    def animation_control_speed(self, speed: float) -> None:
        """Control the speed level of the animation."""
        if speed < 0.00 or speed > 1.00:
            raise ValueError("Speed must be between 0 and 1")
        logging.info("Client: Set Speed %s", speed)

        route: str
        if self._animation_mode == 2:  # manual mode
            route = "/Vd72e0D61BuM"
        else:
            route = "/Ve3ZSfSgP54T"

        try:
            self.client.send_message(route, [speed, 0])
        except Exception as e:
            logging.error("Failed to set speed: %s", e)
            raise

    def animation_control_size(self, size: float) -> None:
        """Control the size of the animation."""
        if size < 0.00 or size > 1.00:
            raise ValueError("Size must be between 0 and 1")
        logging.info("Client: Set Size %s", size)

        route: str
        if self._animation_mode == 2:  # manual mode
            route = "/Vd7XP0X61BuM"
        else:
            route = "/Ve3ZSfSgP54T"

        try:
            self.client.send_message(route, [size, 0])
        except Exception as e:
            logging.error("Failed to set size: %s", e)
            raise

    def animation_control_bloom(self, bloom: float) -> None:
        """Control the bloom level of the animation."""
        if bloom < 0.00 or bloom > 1.00:
            raise ValueError("Bloom must be between 0 and 1")
        logging.info("Client: Set Bloom %s", bloom)
        try:
            self.client.send_message("/Ve3ZS5tBUo4T", [bloom, 0])
        except Exception as e:
            logging.error("Failed to set bloom: %s", e)
            raise

    def palette_hue_set(self, palette_hue: float) -> None:
        """Set the palette hue level."""
        if palette_hue < 0.00 or palette_hue > 1.00:
            raise ValueError("Hue must be between 0 and 1")
        logging.info("Client: Set Palette Hue %s", palette_hue)

        route: str
        if self._animation_mode == 2:  # manual mode
            route = "/VdV1IeK61BuM"
        else:
            route = "/ThWnxs65l0sj"

        try:
            self.client.send_message(route, [palette_hue, 0])
        except Exception as e:
            logging.error("Failed to set palette hue: %s", e)
            raise

    def palette_saturation_set(self, palette_saturation: float) -> None:
        """Set the palette saturation level."""
        if palette_saturation < 0.00 or palette_saturation > 1.00:
            raise ValueError("Saturation must be between 0 and 1")
        logging.info("Client: Set Palette Saturation %s", palette_saturation)

        route: str
        if self._animation_mode == 2:  # manual mode
            route = "/UH9E69aUREEb"
        else:
            route = "/y687U4Zgymsj"
        try:
            self.client.send_message(route, [palette_saturation, 0])
        except Exception as e:
            logging.error("Failed to set palette saturation: %s", e)
            raise

    def audio_gain_set(self, audio_gain: float) -> None:
        """Set the audio gain level."""
        if audio_gain < 0.00 or audio_gain > 1.00:
            raise ValueError("Gain must be between 0 and 1")
        logging.info("Client: Set Audio Gain %s", audio_gain)
        try:
            self.client.send_message("/HwBeJeS0ufSp", [audio_gain, 0])
        except Exception as e:
            logging.error("Failed to set audio gain: %s", e)
            raise

    def audio_attack_set(self, audio_attack: float) -> None:
        """Set the audio attack level."""
        if audio_attack < 0.00 or audio_attack > 1.00:
            raise ValueError("Attack must be between 0 and 1")
        logging.info("Client: Set Audio Attack %s", audio_attack)
        try:
            self.client.send_message("/HwBeGOxYN5Sp", [audio_attack, 0])
        except Exception as e:
            logging.error("Failed to set audio attack: %s", e)
            raise

    def audio_release_set(self, audio_release: float) -> None:
        """Set the audio release level."""
        if audio_release < 0.00 or audio_release > 1.00:
            raise ValueError("Release must be between 0 and 1")
        logging.info("Client: Set Audio Release %s", audio_release)
        try:
            self.client.send_message("/HwBeogt1MBDp", [audio_release, 0])
        except Exception as e:
            logging.error("Failed to set audio release: %s", e)
            raise

    def audio_filter_set(self, audio_filter: float) -> None:
        """Set the audio filter level."""
        if audio_filter < 0.00 or audio_filter > 1.00:
            raise ValueError("Filter must be between 0 and 1")
        logging.info("Client: Set Audio Filter %s", audio_filter)
        try:
            self.client.send_message("/HwBeiitcOaSp", [audio_filter, 0])
        except Exception as e:
            logging.error("Failed to set audio filter: %s", e)
            raise


def main():
    """Demonstrate basic usage of the FluoraAPI."""
    plant_ip = "192.168.4.172"
    plant_port = 6767
    api = FluoraClient(plant_ip, plant_port)
    api.power(1)
    api.brightness_set(0.72)
    time.sleep(1)
    # api.animation_set("CHILL")


if __name__ == "__main__":
    main()
