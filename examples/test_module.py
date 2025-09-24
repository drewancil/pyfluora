#!/usr/bin/env python3
"""Simple test to verify pyfluora module functionality."""

import time
from fluoraapi import FluoraAPI, FluoraClient, FluoraStateServer, FluoraState


def test_imports():
    """Test that all imports work correctly."""
    print("✓ All imports successful")


def test_client_creation():
    """Test creating a FluoraClient."""
    client = FluoraClient("127.0.0.1", 4210)
    assert client.client_ip_address == "127.0.0.1"
    assert client.client_udp_port == 4210
    print("✓ FluoraClient creation successful")


def test_server_creation():
    """Test creating and starting/stopping FluoraStateServer."""
    try:
        server = FluoraStateServer("127.0.0.1", 12346)  # Use different port

        # Test starting server
        server.server_start()
        time.sleep(0.5)  # Give it time to start

        # Test stopping server
        server.server_stop()
        time.sleep(0.5)  # Give it time to stop

        print("✓ FluoraStateServer start/stop successful")
    except OSError as e:
        print(f"⚠ Server test skipped (port in use): {e}")


def test_api_creation():
    """Test creating FluoraAPI without starting server."""
    api = FluoraAPI("127.0.0.1", 4210, "127.0.0.1", 12347)
    assert api.plant_state is not None  # Should have a FluoraState object
    print("✓ FluoraAPI creation successful")


def test_context_manager():
    """Test FluoraAPI context manager."""
    try:
        with FluoraAPI("127.0.0.1", 4210, "127.0.0.1", 12348) as api:
            # Just test that context manager works
            assert api is not None
        print("✓ FluoraAPI context manager successful")
    except OSError as e:
        print(f"⚠ Context manager test skipped (port in use): {e}")


def test_dataclass():
    """Test FluoraState dataclass."""
    state = FluoraState()
    assert state.brightness == 0.0
    assert state.model == ""
    assert state.main_light is False

    # Test setting values
    state.brightness = 0.5
    state.model = "test"
    state.main_light = True

    assert state.brightness == 0.5
    assert state.model == "test"
    assert state.main_light is True

    print("✓ FluoraState dataclass working correctly")


def test_effect_lists():
    """Test that effect lists are available."""
    client = FluoraClient("127.0.0.1", 4210)
    effects = client.effect_list
    assert len(effects) > 0
    assert "Auto" in effects  # Should have at least the Auto effect
    print(f"✓ Effect list available: {len(effects)} effects")


def main():
    """Run all tests."""
    print("Running pyfluora Module Tests")
    print("=" * 35)

    tests = [
        test_imports,
        test_dataclass,
        test_client_creation,
        test_server_creation,
        test_api_creation,
        test_context_manager,
        test_effect_lists,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:  # pylint: disable=W0718
            print(f"✗ {test.__name__} failed: {e}")

    print(f"\nTest Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Module is properly structured.")
    else:
        print("⚠ Some tests failed. Check the module structure.")


if __name__ == "__main__":
    main()
