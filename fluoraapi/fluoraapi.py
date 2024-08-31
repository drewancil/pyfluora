"""Python library to control Fluora LED plant."""

from .fluora_client import FluoraClient
from .fluora_server import FluoraStateServer


class FluoraAPI:
    """Main class for the Fluora Plant API."""

    def __init__(
        self, plant_ip: str, plant_port: int, server_address: str, server_port: int
    ) -> None:
        """Initialize the UDP server to receive state updates from the plant.add()
        Plant will send updates to UDP:12345 by default.
        """

        self._fluora_plant = FluoraClient(plant_ip, plant_port)
        self._fluora_server = FluoraStateServer(server_address, server_port)
