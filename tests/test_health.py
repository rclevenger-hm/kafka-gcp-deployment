import unittest
from helpers import load
health=load("tools/health.py","health")
class HealthTests(unittest.TestCase):
    def test_healthy_quorum(self):
        self.assertEqual(health.parse_quorum('LeaderId: 100\nMaxFollowerLag: 0\nCurrentVoters: [{"id":100},{"id":101},{"id":102}]')["voters"],3)
    def test_lagged_quorum_rejected(self):
        with self.assertRaises(ValueError): health.parse_quorum('LeaderId: 100\nMaxFollowerLag: 5\nCurrentVoters: [100,101,102]')
    def test_missing_leader_rejected(self):
        with self.assertRaises(ValueError): health.parse_quorum('LeaderId: -1\nMaxFollowerLag: 0\nCurrentVoters: [100,101,102]')
    def test_missing_voter_rejected(self):
        with self.assertRaises(ValueError): health.parse_quorum('LeaderId: 100\nMaxFollowerLag: 0\nCurrentVoters: [100,101]')
    def test_empty_output_rejected(self):
        with self.assertRaises(ValueError): health.parse_quorum('')
