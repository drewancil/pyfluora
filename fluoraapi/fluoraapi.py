"""Python library to control Fluora LED plant."""

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

    def reboot(self) -> None:
        """Reboot the plant."""
        self._client.reboot()

    def power(self, state: int) -> None:
        """Toggle the plant LED Power."""
        self._client.power(state)

    def brightness_set(self, brightness: float) -> None:
        """Set the brightness of the plant."""
        self._client.brightness_set(brightness)

    def animation_set_manual(self, animation_name: str) -> None:
        """Set the animation mode."""
        self._client.animation_set(animation_name)

    def start_server(self) -> None:
        """Start the UDP server to listen for state updates."""
        self._state_server.server_start()

    def stop_server(self) -> None:
        """Stop the UDP server."""
        self._state_server.server_stop()

    def __enter__(self):
        """Context manager entry."""
        self.start_server()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_server()
