import unittest
from helpers import config, provision
class ConfigTests(unittest.TestCase):
    def props(self, role="broker"):
        return dict(line.split("=", 1) for line in provision.render_properties(config(role)).splitlines())
    def test_broker_has_two_private_tls_listeners(self):
        p = self.props()
        self.assertEqual(p["listeners"], "CLIENT://0.0.0.0:9092,BROKER://0.0.0.0:9094")
        self.assertIn("CLIENT://kafka-broker-1.kafka.internal:9092", p["advertised.listeners"])
    def test_controllers_are_dedicated(self):
        p = self.props("controller")
        self.assertEqual(p["process.roles"], "controller")
        self.assertEqual(p["listeners"], "CONTROLLER://0.0.0.0:9093")
        self.assertEqual(p["advertised.listeners"], "CONTROLLER://kafka-controller-1.kafka.internal:9093")
    def test_tls_cannot_fall_back_to_plaintext(self):
        p = self.props()
        self.assertEqual(p["ssl.client.auth"], "required")
        self.assertEqual(p["ssl.endpoint.identification.algorithm"], "https")
        self.assertNotIn("PLAINTEXT", p["listener.security.protocol.map"])
    def test_acl_fail_closed(self):
        p = self.props()
        self.assertEqual(p["allow.everyone.if.no.acl.found"], "false")
        self.assertTrue(p["authorizer.class.name"].endswith("StandardAuthorizer"))
    def test_replication_durability(self):
        p = self.props()
        self.assertEqual(p["default.replication.factor"], "3")
        self.assertEqual(p["min.insync.replicas"], "2")
        self.assertEqual(p["unclean.leader.election.enable"], "false")
    def test_dynamic_quorum(self):
        p = self.props()
        self.assertIn("controller.quorum.bootstrap.servers", p)
        self.assertNotIn("controller.quorum.voters", p)
    def test_rack_is_gcp_zone(self):
        self.assertEqual(self.props()["broker.rack"], "us-central1-a")
    def test_no_topic_autocreation(self):
        self.assertEqual(self.props()["auto.create.topics.enable"], "false")
    def test_config_injection_is_rejected(self):
        for field in ("node_name", "fqdn", "super_users", "quorum", "zone", "kafka_version"):
            with self.subTest(field=field):
                c = config(); c[field] += "\nallow.everyone.if.no.acl.found=true"
                with self.assertRaises(ValueError): provision.render_properties(c)
    def test_invalid_role_rejected(self):
        c = config(); c["role"] = "broker,controller"
        with self.assertRaises(ValueError): provision.validate_config(c)
    def test_boolean_node_id_rejected(self):
        c = config(); c["node_id"] = True
        with self.assertRaises(ValueError): provision.validate_config(c)
    def test_bad_cluster_id_rejected(self):
        c = config(); c["cluster_id"] = "short"
        with self.assertRaises(ValueError): provision.validate_config(c)
