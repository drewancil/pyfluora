"""Module that implements the Fluora State Server."""

import json
import logging
import socketserver
import threading
import socket
import time

try:  # package execution: python -m fluoraapi.fluora_server
    from .dataclasses import FluoraState
    from .enums import FluoraAnimations, AnimationModeScene
    from .config_decoder import FluoraConfigDecoder
except ImportError:  # direct script execution: python fluora_server.py
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from fluoraapi.dataclasses import FluoraState
    from fluoraapi.enums import FluoraAnimations, AnimationModeScene
    from fluoraapi.config_decoder import FluoraConfigDecoder


class FluoraStateServer(socketserver.ThreadingUDPServer):
    """Starts UDP listener to receive state updates from the Fluora Plant.
    Takes an optional callback function to alert on each state update."""

    allow_reuse_address = True

    def __init__(self, address_with_port: tuple[str, int], state_callback=None) -> None:
        self._json_payload: str = ""
        self._packet_assemble: dict[int, bytes] = {}
        self._server_thread: threading.Thread | None = None
        self._shutdown_event = threading.Event()
        self._fluora_state = FluoraState()
        self._state_callback = state_callback
        super().__init__(address_with_port, FluoraUDPHandler)
        self.daemon_threads = True

        root = logging.getLogger()
        logging.debug(
            "FluoraStateServer: Logging handlers configured: %s", root.handlers
        )

    @property
    def effect_list(self) -> list[str]:
        """Returns a list of available animation effects."""
        return [effect.name.title() for effect in FluoraAnimations]

    @property
    def fluora_state(self) -> FluoraState:
        """Returns the current FluoraState dataclass instance."""
        return self._fluora_state

    def server_start(self) -> None:
        """Starts the UDP server in a background thread."""
        if self._server_thread and self._server_thread.is_alive():
            logging.warning("Server already running")
            return

        def _run():
            logging.info("UDP server listening on %s:%d", *self.server_address)
            while not self._shutdown_event.is_set():
                try:
                    self.handle_request()
                except OSError as e:
                    if not self._shutdown_event.is_set():
                        logging.error("Server error: %s", e)
                        break
            logging.info("UDP server stopped")

        self._shutdown_event.clear()
        self._server_thread = threading.Thread(
            target=_run, daemon=True, name="FluoraUDP"
        )
        self._server_thread.start()

    def server_stop(self) -> None:
        """Stops the UDP server."""
        logging.info("Stopping UDP server")
        self._shutdown_event.set()
        # unblock handle_request
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(b"", self.server_address)
        except OSError:
            pass
        if self._server_thread:
            self._server_thread.join(timeout=2)
        self.server_close()

    def process_datagram(self, data: bytes, client_address) -> None:
        """Processes incoming UDP datagram.
        This is not socketserver's process_request; it's our datagram parser.
        """
        if not data:
            return
        if len(data) < 5:
            logging.debug("Ignoring short packet from %s: %r", client_address, data)
            return
        response_type = data[0]  # if response to a command or just periodic update
        counter = data[1]  # some kind of counter - not needed withy below
        packet_count = data[2]  # total packets in this message
        packet_sequence = data[3]  # sequence number of this packet
        payload_raw = data[4:]  # bytes of the actual payload
        del response_type, counter

        # start of new multi-packet message
        if packet_sequence == 0:
            self._packet_assemble.clear()
            self._packet_assemble[0] = payload_raw

        # final packet of multi-packet message
        if packet_sequence == (packet_count - 1):
            self._packet_assemble[packet_count - 1] = payload_raw

            # reassemble full message from packets
            byte_message = b"".join(self._packet_assemble.values())
            logging.debug("Reassembled message (%d bytes)", len(byte_message))

            # decode the binary message using FluoraConfigDecoder
            with open("fluora-config.txt", encoding="utf-8") as f:
                my_schema = json.load(f)
                decoder = FluoraConfigDecoder(my_schema)
                try:
                    state_update = decoder.decode(byte_message)
                    self._update_state(state_update)
                except Exception as e:  # pylint: disable=W0718
                    logging.error("Failed to decode state update: %s", e)
                    raise

        else:  # intermediate packet
            self._packet_assemble[packet_sequence] = payload_raw

    def _update_state(self, state: dict) -> None:
        """Updates the FluoraState dataclass from the decoded state dictionary."""
        # general settings - same for all modes

        # light sensor setting
        self._fluora_state.light_sensor_enabled = (
            state.get("lightSensor", {}).get("enabled", {}).get("value")
        )
        # nickname of plant
        self._fluora_state.nickname = state.get("nickname", {}).get("value", "")
        # audio settings
        d_audio = state.get("audio", {})
        f_filter = float(d_audio.get("filter", {}).get("value"))
        self._fluora_state.audio_filter = round(f_filter, 4)
        f_release = float(d_audio.get("release", {}).get("value"))
        self._fluora_state.audio_release = round(f_release, 4)
        f_gain = float(d_audio.get("gain", {}).get("value"))
        self._fluora_state.audio_gain = round(f_gain, 4)
        f_attack = float(d_audio.get("attack", {}).get("value"))
        self._fluora_state.audio_attack = round(f_attack, 4)

        # engine updates
        d_engine = state.get("engine", {})
        f_brightness = float(d_engine.get("brightness", {}).get("value"))
        self._fluora_state.brightness = round(f_brightness, 4)
        self._fluora_state.main_light = d_engine.get("isDisplaying", {}).get("value")
        self._fluora_state.mode = d_engine.get("mode", {}).get("value")

        # animation details depend on mode
        if self._fluora_state.mode == 0:  # auto mode
            self._fluora_state.animation_index = 0
            self._fluora_state.animation_name = "Auto"

        elif self._fluora_state.mode == 1:  # scene mode
            d_scenemode = d_engine.get("sceneMode", {})
            scene_index: int = d_scenemode.get("activeSceneIndex", {}).get("value")
            item = AnimationModeScene(scene_index)
            self._fluora_state.animation_index = scene_index
            self._fluora_state.animation_name = item.name.title()

            d_sweep = (
                d_scenemode.get("scenes", {})
                .get(f"{self._fluora_state.animation_name}", {})
                .get("sweep", {})
            )
            d_dashboard = d_sweep.get("dashboard", {})
            self._fluora_state.animation_size = d_dashboard.get("gCr38w5FkQeK", {}).get(
                "value"
            )
            self._fluora_state.animation_speed = d_dashboard.get(
                "Kwr38w5FkQeK", {}
            ).get("value")

            d_palette = (
                d_scenemode.get("scenes", {})
                .get(f"{self._fluora_state.animation_name}", {})
                .get("palette", {})
            )
            f_hue = float(d_palette.get("hue", {}).get("value"))
            self._fluora_state.hue = round(f_hue, 4)
            f_saturation = float(d_palette.get("saturation", {}).get("value"))
            self._fluora_state.saturation = round(f_saturation, 4)

        elif self._fluora_state.mode == 2:  # manual mode
            self._fluora_state.animation_index = 2

        if self._state_callback:  # send via callback if available
            self._state_callback(self._fluora_state)
            logging.debug("Updated FluoraState: %s", self._fluora_state)
        else:
            logging.warning("Callback unavailable: %s", self._fluora_state)

    # wrappers
    def _server_activate(self):
        return super().server_activate()

    def _handle_request(self):
        return super().handle_request()

    def _verify_request(self, request, client_address):
        return super().verify_request(request, client_address)

    def _finish_request(self, request, client_address):
        return super().finish_request(request, client_address)

    def _close_request_address(self, request_address):
        logging.debug("close_request(%s)", request_address)
        return super().close_request(request_address)


class FluoraUDPHandler(socketserver.BaseRequestHandler):
    """Handles each UDP datagram."""

    def handle(self):
        data = self.request[0]  # (bytes, socket)
        logging.debug("Datagram from %s length=%d", self.client_address, len(data))
        self.server.process_datagram(data, self.client_address)  # type: ignore[attr-defined]


def main():
    """Test function to demonstrate use of class."""

    logging.basicConfig(
        level=getattr(logging, "DEBUG", logging.INFO),
        format="%(asctime)s %(levelname)s %(threadName)s %(message)s",
    )

    ip_port: tuple[str, int] = ("0.0.0.0", 12345)

    server = FluoraStateServer(ip_port)
    server.server_start()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        logging.info("Interrupted, shutting down")
    finally:
        server.server_stop()


if __name__ == "__main__":
    main()
