#!/usr/bin/env python3
"""UDP debugging test for Fluora server.

This script helps debug UDP server activation issues by:
1. Starting a Fluora UDP server
2. Sending test packets to verify _process_request is called
3. Showing detailed debug logs
"""

import socket
import time
import logging
import threading
from fluoraapi import FluoraStateServer


def setup_logging():
    """Configure detailed logging for debugging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
    )


def send_test_packets(server_address, server_port, delay=1):
    """Send test UDP packets to the server."""
    logger = logging.getLogger(__name__)
    time.sleep(delay)  # Wait for server to start
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        logger.info("Sending test packet to %s:%d", server_address, server_port)
        
        # Create a proper test packet with valid header
        test_data = bytearray([0, 1, 12, 0])  # response_flag=0, counter=1, num_packets=12, packet_seq=0
        test_data.extend(b'{"test": "UDP server is working"}')
        
        sock.sendto(test_data, (server_address, server_port))
        logger.info("Test packet sent successfully")
        
    except Exception as e:
        logger.error("Error sending test packet: %s", e)
    finally:
        sock.close()


def main():
    """Run the UDP debugging test."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Fluora UDP Server Debug Test")
    logger.info("=" * 50)
    
    server_address = "127.0.0.1"
    server_port = 12345
    
    try:
        # Create and start server
        logger.info("Creating UDP server on %s:%d", server_address, server_port)
        server = FluoraStateServer(server_address, server_port)
        
        logger.info("Starting server...")
        server.server_start()
        
        # Start test packet sender in separate thread
        sender_thread = threading.Thread(
            target=send_test_packets, 
            args=(server_address, server_port, 2)
        )
        sender_thread.start()
        
        # Let it run for a few seconds
        logger.info("Waiting for packet processing...")
        time.sleep(5)
        
        # Stop server
        logger.info("Stopping server...")
        server.server_stop()
        
        # Wait for sender thread
        sender_thread.join(timeout=5)
        
        logger.info("Test completed!")
        print("\n" + "=" * 50)
        print("✓ UDP Debug Test Completed")
        print("If you see '_process_request' debug logs above, the server is working correctly!")
        
    except OSError as e:
        if "Address already in use" in str(e):
            logger.error("Port %d is already in use. Try a different port or stop other services.", server_port)
        else:
            logger.error("Server error: %s", e)
    except Exception as e:
        logger.error("Test failed: %s", e)


if __name__ == "__main__":
    main()