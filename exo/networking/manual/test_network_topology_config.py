import unittest
import json
from exo.networking.manual.network_topology_config import NetworkTopology

root_path = "./exo/networking/manual/test_data/"


class TestNetworkTopologyConfig(unittest.TestCase):
  def test_from_path_invalid_path(self):
    with self.assertRaises(FileNotFoundError) as e:
      NetworkTopology.from_path("invalid_path")
    self.assertEqual(e.exception.args[0], "Config file not found at invalid_path")

  def test_from_path_invalid_json(self):
    with self.assertRaises(json.JSONDecodeError) as e:
      NetworkTopology.from_path(root_path + "invalid_json.json")
    self.assertEqual(e.exception.args[0], "Error decoding JSON data from ./exo/networking/manual/test_data/invalid_json.json: Expecting value: line 1 column 1 (char 0): line 1 column 1 (char 0)")

  def test_from_path_invalid_config(self):
    with self.assertRaises(TypeError) as e:
      NetworkTopology.from_path(root_path + "invalid_config.json")
    self.assertEqual(
      e.exception.args[0], "Error parsing networking config from ./exo/networking/manual/test_data/invalid_config.json: NetworkTopology.__init__() got an unexpected keyword argument 'not_peers'"
    )

  def test_from_path_valid(self):
    config = NetworkTopology.from_path(root_path + "test_config.json")
    self.assertEqual(
      config.peers,
      {
        "node1": {"address": "localhost", "port": 50051, "device_capabilities": {"model": "Unknown Model", "chip": "Unknown Chip", "memory": 0, "flops": {"fp32": 0, "fp16": 0, "int8": 0}}},
        "node2": {"address": "localhost", "port": 50052, "device_capabilities": {"model": "Unknown Model", "chip": "Unknown Chip", "memory": 0, "flops": {"fp32": 0, "fp16": 0, "int8": 0}}},
      },
    )


if __name__ == "__main__":
  unittest.main()
