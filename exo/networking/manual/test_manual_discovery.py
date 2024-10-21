import asyncio
import unittest
from unittest import mock
from exo.networking.manual.manual_discovery import ManualDiscovery
from exo.networking.manual.network_topology_config import NetworkTopology
from exo.networking.grpc.grpc_peer_handle import GRPCPeerHandle
from exo.networking.grpc.grpc_server import GRPCServer
from exo.orchestration.node import Node

root_path = "./exo/networking/manual/test_data/test_config.json"


@unittest.skip("Skipping test for now")
class TestSingleNodeManualDiscovery(unittest.IsolatedAsyncioTestCase):
  async def asyncSetUp(self):
    self.peer1 = mock.AsyncMock()
    self.peer1.connect = mock.AsyncMock()
    self.discovery1 = ManualDiscovery(root_path, "node1", create_peer_handle=lambda peer_id, address, device_capabilities: self.peer1)
    print("SETUP")
    x = self.discovery1.start()
    print("DISCOVERY1 FINISHED")

  async def asyncTearDown(self):
    print("TEARDOWN")
    await self.discovery1.stop()
    print("TEARDOWN FINISHED")

  async def test_discovery(self):
    print("START TEST")
    peers1 = await self.discovery1.discover_peers(wait_for_peers=0)
    assert len(peers1) == 0
    print("END TEST")

    # connect has to be explicitly called after discovery
    self.peer1.connect.assert_not_called()


@unittest.skip("Skipping test for now")
class TestManualDiscovery(unittest.IsolatedAsyncioTestCase):
  async def asyncSetUp(self):
    self.peer1 = mock.AsyncMock()
    self.peer2 = mock.AsyncMock()
    self.peer1.connect = mock.AsyncMock()
    self.peer2.connect = mock.AsyncMock()
    self.discovery1 = ManualDiscovery(root_path, "node1", create_peer_handle=lambda peer_id, address, device_capabilities: self.peer1)
    self.discovery2 = ManualDiscovery(root_path, "node2", create_peer_handle=lambda peer_id, address, device_capabilities: self.peer2)
    print("SETUP")
    await self.discovery1.start()
    print("DISCOVERY1 FINISHED")
    await self.discovery2.start()
    print("DISCOVERY2 FINISHED")

  async def asyncTearDown(self):
    print("TEARDOWN")
    await self.discovery1.stop()
    await self.discovery2.stop()
    print("TEARDOWN FINISHED")

  async def test_discovery(self):
    print("START TEST")
    peers1 = await self.discovery1.discover_peers(wait_for_peers=1)
    assert len(peers1) == 1
    peers2 = await self.discovery2.discover_peers(wait_for_peers=1)
    assert len(peers2) == 1
    print("END TEST")

    # connect has to be explicitly called after discovery
    self.peer1.connect.assert_not_called()
    self.peer2.connect.assert_not_called()


# @unittest.skip("Skipping test for now")
class TestManualDiscoveryWithGRPCPeerHandle(unittest.IsolatedAsyncioTestCase):
  async def asyncSetUp(self):
    config = NetworkTopology.from_path(root_path)
    print(config)

    self.node1 = mock.AsyncMock(spec=Node)
    self.node2 = mock.AsyncMock(spec=Node)
    self.server1 = GRPCServer(self.node1, config.peers["node1"].address, config.peers["node1"].port)
    self.server2 = GRPCServer(self.node2, config.peers["node2"].address, config.peers["node2"].port)
    await self.server1.start()
    await self.server2.start()
    self.discovery1 = ManualDiscovery(root_path, "node1", create_peer_handle=lambda peer_id, address, device_capabilities: GRPCPeerHandle(peer_id, address, device_capabilities))
    self.discovery2 = ManualDiscovery(root_path, "node2", create_peer_handle=lambda peer_id, address, device_capabilities: GRPCPeerHandle(peer_id, address, device_capabilities))
    print("START DISCOVERY")
    await self.discovery1.start()
    print("DISCOVERY1 FINISHED")
    await self.discovery2.start()
    print("DISCOVERY2 FINISHED")

  async def asyncTearDown(self):
    print("TEARDOWN")
    await self.discovery1.stop()
    await self.discovery2.stop()
    await self.server1.stop()
    await self.server2.stop()
    print("TEARDOWN FINISHED")

  async def test_grpc_discovery(self):
    print("START TEST")
    peers1 = await self.discovery1.discover_peers(wait_for_peers=1)
    assert len(peers1) == 1
    peers2 = await self.discovery2.discover_peers(wait_for_peers=1)
    assert len(peers2) == 1
    assert not await peers1[0].is_connected()
    assert not await peers2[0].is_connected()

    # Connect
    await peers1[0].connect()
    await peers2[0].connect()
    assert await peers1[0].is_connected()
    assert await peers2[0].is_connected()

    # Kill server1
    await self.server1.stop()

    assert await peers1[0].is_connected()
    assert not await peers2[0].is_connected()


if __name__ == "__main__":
  asyncio.run(unittest.main())
