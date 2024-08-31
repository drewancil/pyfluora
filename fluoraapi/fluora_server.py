"""Module that implements the Fluora State Server."""

import json
import logging
import socketserver

from box import Box

from .dataclasses import FluoraState
from .enums import FluoraAnimations


class FluoraStateServer(socketserver.UDPServer):
    """Starts UDP listener to receive state updates from the Fluora Plant.
    Sends state to MQTT for use in Home Assistant.
    """

    def __init__(self, server_address: str, server_port: int) -> None:
        """Initialize the UDP server to receive state updates from the plant.add()
        Plant will send updates to UDP:12345 by default.
        """
        self._json_payload: str = ""
        self._packet_assemble = {}

        self._fluora_state = FluoraState()
        try:
            server_addr_port = (server_address, server_port)
            socketserver.UDPServer.__init__(self, server_addr_port, FluoraUDPHandler)
        except OSError:
            logging.error("Server could not start as UDP address/port already in use")
            raise

    @property
    def effect_list(self) -> list[str]:
        """Return the list of supported effects."""
        return [effect.name.title() for effect in FluoraAnimations]

    @property
    def fluora_state(self) -> FluoraState:
        """Return the current state of the plant."""
        return self._fluora_state

    def server_start(self, poll_interval=0.5):
        """Start listening for UDP packets from the plant."""
        del poll_interval
        while True:
            self.handle_request()

    def server_stop(self):
        """Stop the UDP server from listening for plant updates."""
        logging.debug("Stopping UDP server")
        return socketserver.UDPServer.server_close(self)

    def _process_request(self, request, client_address):  # pylint: disable=R1710
        """Process incoming UDP datagrams from the plant.  A single state
        update is 12 datagrams, so they will be stored in memory and posted
        to plant_state after the final datagram in the series is received.
        """
        data = request[0]  # type: ignore
        # this bytes appears to be the UDP partial message number
        # data is bigger then 1024 byte packet
        udp_packet_seq = data[3]

        # strip bytes 0-3 to leave just json payload / decode to utf-8
        udp_payload_raw = data[4:]
        udp_payload = udp_payload_raw.decode("utf-8")

        # series of 12 udp datagrams with full plant light state (json)
        if udp_packet_seq == 0:
            # clear the packet_assemble data for a new state update
            self._packet_assemble.clear()
            self._packet_assemble[0] = udp_payload
        if udp_packet_seq == 12:
            # final message in state update (12/12) - process state update
            self._packet_assemble[12] = udp_payload
            msg_vals = self._packet_assemble.values()
            self._json_payload = "".join(msg_vals)
            logging.debug("json_payload: %s", self._json_payload)
            try:
                state_update = json.loads(self._json_payload)
                self._update_state(state_update)

            except json.JSONDecodeError as error:
                logging.error("JSON error: %s", error)
                return
            except TypeError as error:
                logging.error("JSON error: %s", error)
                return
        else:
            # store the partial state update
            self._packet_assemble[udp_packet_seq] = udp_payload

        return socketserver.UDPServer.process_request(self, request, client_address)

    def _update_state(self, state_update) -> None:
        """Update the plant state dataclass."""
        # experiment with python-box for nested dict access
        plant_box = Box(state_update)
        logging.debug(plant_box)

        self.fluora_state.model = state_update["model"]
        self.fluora_state.rssi = state_update["rssi"]
        self.fluora_state.mac_address = state_update["network"]["macAddress"]
        self.fluora_state.audio_filter = state_update["audio"]["filter"]["value"]
        self.fluora_state.audio_release = state_update["audio"]["release"]["value"]
        self.fluora_state.audio_gain = state_update["audio"]["gain"]["value"]
        self.fluora_state.audio_attack = state_update["audio"]["attack"]["value"]
        self.fluora_state.light_sensor_enabled = state_update["lightSensor"]["enabled"][
            "value"
        ]
        self.fluora_state.brightness = state_update["engine"]["brightness"]["value"]
        self.fluora_state.main_light = state_update["engine"]["isDisplaying"]["value"]
        self.fluora_state.animation_mode = state_update["engine"]["manualMode"][
            "loadedAnimationIndex"
        ]
        self.fluora_state.active_animation = state_update["engine"]["manualMode"][
            "activeAnimationIndex"
        ]["value"]

        dashboard: dict = state_update["engine"]["manualMode"]["dashboard"]
        if "Ve3ZS5tBUo4T" in dashboard:
            self.fluora_state.animation_bloom = dashboard["Ve3ZS5tBUo4T"]["value"]
        if "Ve3ZSfv3PK4T" in dashboard:
            self.fluora_state.animation_speed = dashboard["Ve3ZSfv3PK4T"]["value"]
        if "Ve3ZSfSgP54T" in dashboard:
            self.fluora_state.animation_size = dashboard["Ve3ZSfSgP54T"]["value"]

        palette: dict = state_update["engine"]["manualMode"]["palette"]
        if "saturation" in palette:
            self.fluora_state.palette_saturation = palette["saturation"]["value"]
        if "hue" in palette:
            self.fluora_state.palette_hue = palette["hue"]["value"]

    def _server_activate(self):
        """Activate the server."""
        socketserver.UDPServer.server_activate(self)

    def _handle_request(self):
        """Handle request."""
        return socketserver.UDPServer.handle_request(self)

    def _verify_request(self, request, client_address):
        """Verify request."""
        return socketserver.UDPServer.verify_request(self, request, client_address)

    def _finish_request(self, request, client_address):
        """Finish request."""
        return socketserver.UDPServer.finish_request(self, request, client_address)

    def _close_request_address(self, request_address):
        """Close request address."""
        logging.debug("close_request(%s)", request_address)
        return socketserver.UDPServer.close_request(self, request_address)


class FluoraUDPHandler(socketserver.BaseRequestHandler):
    """UDP server handler."""

    def __init__(self, request, client_address, fl_server) -> None:
        socketserver.BaseRequestHandler.__init__(
            self, request, client_address, fl_server
        )

    def setup(self):
        return socketserver.BaseRequestHandler.setup(self)

    def finish(self):
        return socketserver.BaseRequestHandler.finish(self)

    def handle(self):
        data: bytearray = self.request[0].strip()
        logging.debug("Handle UDP: %s", data)
