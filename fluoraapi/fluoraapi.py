"""Python library to control Fluora LED plant."""

import logging

from fluoraapi.dataclasses import FluoraState

from fluoraapi.fluora_client import FluoraClient
from fluoraapi.fluora_server import FluoraStateServer


class FluoraAPI:
    """Main class for the Fluora Plant API."""

    def __init__(
        self, plant_ip: str, plant_port: int, server_address: str, server_port: int
    ) -> None:
        """Initialize the fluora client to send commands to the led plant.
        Initialize the Fluora state server to receive the state of the plant.

        Note: Call start_server() to begin listening for state updates.
        """
        self._client = FluoraClient(plant_ip, plant_port)
        self._state_server = FluoraStateServer(server_address, server_port)

    @property
    def plant_state(self) -> FluoraState | None:
        """Get the current state of the plant."""
        return self._state_server.fluora_state

    def available_animations(self) -> list[str]:
        """Get the list of available animations."""
        return self._client.effect_list

    def reboot(self) -> None:
        """Reboot the plant."""
        try:
            self._client.reboot()
        except Exception as e:
            logging.error("Failed to reboot plant: %s", e)
            raise

    def power(self, state: int) -> None:
        """Toggle the plant LED Power."""
        try:
            self._client.power(state)
        except Exception as e:
            logging.error("Failed to change power state: %s", e)
            raise

    def custom_command(self, route: str, value: float) -> None:
        """Send a custom command to the plant."""
        try:
            self._client.custom_command(route, value)
        except Exception as e:
            logging.error("Failed to send custom command: %s", e)
            raise

    def brightness_set(self, brightness: float) -> None:
        """Set the brightness of the plant."""
        try:
            self._client.brightness_set(brightness)
        except Exception as e:
            logging.error("Failed to change brightness: %s", e)
            raise

    def animation_set_mode(self, mode: str) -> None:
        """Set the animation mode."""
        try:
            self._client.animation_set_mode(mode)
        except Exception as e:
            logging.error("Failed to change animation mode: %s", e)
            raise

    def animation_set(self, animation_name: str) -> None:
        """Set the animation."""
        try:
            self._client.animation_set(animation_name)
        except Exception as e:
            logging.error("Failed to change animation: %s", e)
            raise

    def palette_hue_set(self, hue: float) -> None:
        """Set the palette hue."""
        try:
            self._client.palette_hue_set(hue)
        except Exception as e:
            logging.error("Failed to change palette hue: %s", e)
            raise

    def palette_saturation_set(self, saturation: float) -> None:
        """Set the palette saturation."""
        try:
            self._client.palette_saturation_set(saturation)
        except Exception as e:
            logging.error("Failed to change palette saturation: %s", e)
            raise

    def animation_speed_set(self, speed: float) -> None:
        """Set the animation speed."""
        try:
            self._client.animation_control_speed(speed)
        except Exception as e:
            logging.error("Failed to change animation speed: %s", e)
            raise

    def animation_size_set(self, size: float) -> None:
        """Set the animation size."""
        try:
            self._client.animation_control_size(size)
        except Exception as e:
            logging.error("Failed to change animation size: %s", e)
            raise

    def start_server(self, debug_mode: bool = False) -> None:
        """Start the UDP server to listen for state updates."""
        try:
            self._state_server.server_start(debug_mode=debug_mode)
        except Exception as e:
            logging.error("Failed to start state server: %s", e)
            raise

    def stop_server(self) -> None:
        """Stop the UDP server."""
        try:
            self._state_server.server_stop()
        except Exception as e:
            logging.error("Failed to stop state server: %s", e)
            raise

    def __enter__(self):
        """Context manager entry."""
        self.start_server()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_server()
