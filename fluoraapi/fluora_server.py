"""Module that implements the Fluora State Server."""

import json
import logging
import socketserver
import threading
import socket

from box import Box

from fluoraapi.dataclasses import FluoraState
from fluoraapi.enums import FluoraAnimations


class FluoraStateServer(socketserver.ThreadingUDPServer):
    """Starts UDP listener to receive state updates from the Fluora Plant.
    Sends state to MQTT for use in Home Assistant.
    """

    def __init__(self, server_address: str, server_port: int) -> None:
        """Initialize the UDP server to receive state updates from the plant.add()
        Plant will send updates to UDP:12345 by default.
        """
        self._json_payload: str = ""
        self._packet_assemble = {}
        self._server_thread = None
        self._shutdown_event = threading.Event()
        self._fluora_state = FluoraState()

        logging.info("Starting server on %s:%d", server_address, server_port)
        try:
            server_addr_port = (server_address, server_port)
            socketserver.ThreadingUDPServer.__init__(
                self, server_addr_port, FluoraUDPHandler
            )
            # self.daemon_threads = True  # Allow threads to die when main thread dies
            self.daemon_threads = False  # This allows debugger to attach to threads
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

    def server_start(self, debug_mode: bool = False):
        """Start listening for UDP packets from the plant in a separate thread."""
        if debug_mode:
            # Run synchronously in main thread for debugging
            logging.info(
                "Starting UDP server in DEBUG MODE on %s:%d", *self.server_address
            )
            try:
                self.serve_forever()
            except KeyboardInterrupt:
                logging.info("Server interrupted")
            return

        if self._server_thread is not None and self._server_thread.is_alive():
            logging.warning("Server is already running")
            return

        def _run_server():
            """Internal method to run the server loop."""
            logging.info("Server thread running")
            while not self._shutdown_event.is_set():
                try:
                    self.handle_request()
                except OSError as e:
                    if not self._shutdown_event.is_set():
                        logging.error("Server error: %s", e)
                    break
            logging.info("UDP server stopped")

        self._shutdown_event.clear()
        self._server_thread = threading.Thread(target=_run_server, daemon=False)
        self._server_thread.start()

    def server_stop(self):
        """Stop the UDP server from listening for plant updates."""
        logging.debug("Stopping UDP server")
        self._shutdown_event.set()

        if self._server_thread and self._server_thread.is_alive():
            # Send a dummy packet to unblock handle_request if needed
            try:
                dummy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                dummy_socket.sendto(b"", self.server_address)
                dummy_socket.close()
            except (OSError, ConnectionError):
                pass  # Ignore errors when sending dummy packet

            self._server_thread.join(timeout=2.0)

        return socketserver.ThreadingUDPServer.server_close(self)

    def process_request(self, request, client_address):  # pylint: disable=R1710
        """Process incoming UDP datagrams from the plant."""
        logging.debug("Processing request from %s", client_address)
        data = request[0]  # type: ignore

        # byte #1: response_flag - whether or not the response is in response
        # to a request or being sent proactively because the state changed
        # (only used on a few occasions)
        response_flag = data[0]

        # byte #2: high level counter just to help put the packets back together for each response
        #  (just continuously overflows the 255 but is enough info to help)
        counter = data[1]

        # byte #3: num_packets - number of packets/fragments in the response
        num_packets = data[2]

        # byte #4: packet_seq - the index of this individual packet/fragment
        packet_seq = data[3]

        breakpoint()
        logging.debug(
            "UDP Packet - response_flag: %d, counter: %d, num_packets: %d, packet_seq: %d",
            response_flag,
            counter,
            num_packets,
            packet_seq,
        )

        # strip bytes 0-3 to leave just json payload / decode to utf-8
        udp_payload_raw = data[4:]
        udp_payload = udp_payload_raw.decode("utf-8")

        # series of 12 udp datagrams with full plant light state (json)
        if packet_seq == 0:
            # clear the packet_assemble data for a new state update
            self._packet_assemble.clear()
            self._packet_assemble[0] = udp_payload
        if packet_seq == 12:
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
            self._packet_assemble[packet_seq] = udp_payload

        return socketserver.ThreadingUDPServer.process_request(
            self, request, client_address
        )

    def _update_state(self, state_update: dict) -> None:
        """Update the plant state dataclass."""
        # experiment with python-box for nested dict access
        plant_box = Box(state_update)
        logging.debug(plant_box)

        fs = self.fluora_state  # alias for easier access
        state = state_update  # alias for easier access

        fs.model = state["model"]
        fs.rssi = state["rssi"]
        fs.mac_address = state["network"]["macAddress"]
        fs.audio_filter = state["audio"]["filter"]["value"]
        fs.audio_release = state["audio"]["release"]["value"]
        fs.audio_gain = state["audio"]["gain"]["value"]
        fs.audio_attack = state["audio"]["attack"]["value"]
        fs.light_sensor_enabled = state["lightSensor"]["enabled"]["value"]
        fs.brightness = state["engine"]["brightness"]["value"]
        fs.main_light = state["engine"]["isDisplaying"]["value"]
        fs.animation_mode = state["engine"]["manualMode"]["loadedAnimationIndex"]
        fs.active_animation = state["engine"]["manualMode"]["activeAnimationIndex"][
            "value"
        ]

        dashboard: dict = state["engine"]["manualMode"]["dashboard"]
        if "Ve3ZS5tBUo4T" in dashboard:
            fs.animation_bloom = dashboard["Ve3ZS5tBUo4T"]["value"]
        if "Ve3ZSfv3PK4T" in dashboard:
            fs.animation_speed = dashboard["Ve3ZSfv3PK4T"]["value"]
        if "Ve3ZSfSgP54T" in dashboard:
            fs.animation_size = dashboard["Ve3ZSfSgP54T"]["value"]

        palette: dict = state["engine"]["manualMode"]["palette"]
        if "saturation" in palette:
            fs.palette_saturation = palette["saturation"]["value"]
        if "hue" in palette:
            fs.palette_hue = palette["hue"]["value"]

    def _server_activate(self):
        """Activate the server."""
        socketserver.ThreadingUDPServer.server_activate(self)

    def _handle_request(self):
        """Handle request."""
        return socketserver.ThreadingUDPServer.handle_request(self)

    def _verify_request(self, request, client_address):
        """Verify request."""
        return socketserver.ThreadingUDPServer.verify_request(
            self, request, client_address
        )

    def _finish_request(self, request, client_address):
        """Finish request."""
        return socketserver.ThreadingUDPServer.finish_request(
            self, request, client_address
        )

    def _close_request_address(self, request_address):
        """Close request address."""
        logging.debug("close_request(%s)", request_address)
        return socketserver.ThreadingUDPServer.close_request(self, request_address)


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
        data = self.request[0]
        breakpoint()
        client_address = self.client_address
        logging.debug("Handling UDP request from %s", client_address)
        self.server.process_request((data, self.request[1]), client_address)
