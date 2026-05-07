# Contributing

Keep cloud infrastructure, runtime configuration and operating procedures aligned. Add behavioral coverage when changing identity, storage, TLS, networking or maintenance behavior. Never commit real credentials or TLS payloads. Run the commands in [testing](docs/testing.md) before proposing a change.

Describe the failure or operator need, resulting behavior, test evidence and remaining live-environment limitations. Document migration and rollback steps for existing clusters. Avoid weakening deletion, authorization or formatting guards to make a test pass. Open a focused issue for changes that need workload benchmarks or cloud acceptance evidence.
