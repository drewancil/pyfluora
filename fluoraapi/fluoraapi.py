"""Python library to control Fluora LED plant."""

import logging

from fluoraapi.dataclasses import FluoraState
from fluoraapi.fluora_client import FluoraClient
from fluoraapi.fluora_server import FluoraStateServer


class FluoraAPI:
    """Main class for the Fluora Plant API."""

    def __init__(
        self,
        plant_ip_port: tuple[str, int],
        server_ip_port: tuple[str, int],
        api_callback=None,
    ) -> None:
        """Initialize the fluora client to send commands to the led plant.
        Initialize the Fluora state server to receive the state of the plant.

        Note: Call start_server() to begin listening for state updates.
        Update: Context manager support added to automatically start/stop server.
        """

        self._api_callback = api_callback
        self._client = FluoraClient(plant_ip_port)
        self._state_server = FluoraStateServer(
            server_ip_port, state_callback=self._handle_state_update
        )
        # root = logging.getLogger()
        # logging.debug("FluoraAPI: Logging handlers configured: %s", root.handlers)

    def _handle_state_update(self, state: dict) -> None:
        """Handle state update messages from the plant.
        The server module calls this function on each state update.
        It is passed on to the user-defined callback if available.
        """

        logging.debug("API: State update received")
        if self._api_callback:
            logging.debug("API: State received - sending FluoraState via callback")
            self._api_callback(state)
        else:
            logging.warning("API: State received (no callback available)")

    def start_server(self) -> None:
        """Start the UDP server to listen for state updates."""
        try:
            self._state_server.server_start()
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
        """Context manager entry for FluoraAPI."""
        self.start_server()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit for FluoraAPI."""
        self.stop_server()

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

    def light_sensor(self, state: int) -> None:
        """Toggle the plant LED Light Sensor."""
        try:
            self._client.light_sensor(state)
        except Exception as e:
            logging.error("Failed to change light sensor state: %s", e)
            raise

    def custom_command_float(self, route: str, value: float) -> None:
        """Send a custom command to the plant."""
        try:
            self._client.custom_command_float(route, value)
        except Exception as e:
            logging.error("Failed to send custom command: %s", e)
            raise

    def custom_command_int(self, route: str, value: int) -> None:
        """Send a custom command to the plant."""
        try:
            self._client.custom_command_int(route, value)
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

    def audio_gain_set(self, audio_gain: float) -> None:
        """Set the audio gain."""
        try:
            self._client.audio_gain_set(audio_gain)
        except Exception as e:
            logging.error("Failed to change audio gain: %s", e)
            raise

    def audio_attack_set(self, audio_attack: float) -> None:
        """Set the audio gain attack."""
        try:
            self._client.audio_attack_set(audio_attack)
        except Exception as e:
            logging.error("Failed to change audio attack: %s", e)
            raise

    def audio_release_set(self, audio_release: float) -> None:
        """Set the audio gain release."""
        try:
            self._client.audio_release_set(audio_release)
        except Exception as e:
            logging.error("Failed to change audio release: %s", e)
            raise

    def audio_filter_set(self, audio_filter: float) -> None:
        """Set the audio filter."""
        try:
            self._client.audio_filter_set(audio_filter)
        except Exception as e:
            logging.error("Failed to change audio filter: %s", e)
            raise
