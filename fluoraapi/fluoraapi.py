"""Python library to control Fluora LED plant."""

from .fluora_client import FluoraClient
from .fluora_server import FluoraStateServer


class FluoraAPI:
    """Main class for the Fluora Plant API."""

    def __init__(
        self, plant_ip: str, plant_port: int, server_address: str, server_port: int
    ) -> None:
        """Initialize the fluora client to send commands to the led plant.
        Initialize the Fluora state server to receive the state of the plant.
        """

        self._client = FluoraClient(plant_ip, plant_port)
        self._state_server = FluoraStateServer(server_address, server_port)
