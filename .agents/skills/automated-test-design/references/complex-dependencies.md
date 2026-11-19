# Test with Complex Dependencies

Identify which semantics the test needs. A double can exercise how the caller handles a documented timeout. A distinct test may need the actual engine to verify null handling, transaction isolation, scheduling, or data types. Use the least costly option that preserves the semantics in question. Keep a fast suite for independent behavior where possible.

## When the dependency contract is small and a double is faithful

- Reuse a project-supported or upstream fake, emulator, or mocking library. For a new third-party dependency, verify package identity, trusted distribution, maintenance, compatible version, and project dependency rules. Use the project's test dependency lock or pinning practice.
- Stub the public boundary and model only relevant requests, responses, and failures. Make unexpected calls fail and disable pass-through to live systems. Use synthetic fixtures and test credentials. Document which semantics the double omits.
- When drift could hide a defect, verify applicable expectations against a provider contract or a small real-service test. An HTTP double such as WireMock can exercise request and error handling at an HTTP boundary. It cannot establish the behavior of the service implementation. [Software Engineering at Google, Test Doubles](https://abseil.io/resources/swe-book/html/ch13.html) · [WireMock stubbing](https://wiremock.org/docs/stubbing/)

## When a real service can run locally

- Use a supported local mode or the project's existing fixture for a single dependency. Use Docker Compose when a self-hosted service or small stack can reproduce the relevant behavior. Choose trusted images and engine versions or extensions that match the behavior under test.
- Give each run its own Compose project name and data. Avoid shared external volumes, fixed container names, and conflicting host ports. Prefer internal networking and synthetic seed data. Set a bounded readiness check for the actual dependency and capture useful logs on failure.
- Run assertions through the production adapter or application entry point. Clean up on success, failure, and interruption, and remove only resources created for the run. Confirm teardown and surface leftovers. [Compose project names](https://docs.docker.com/compose/how-tos/project-name/) · [Compose startup and shutdown ordering](https://docs.docker.com/compose/how-tos/startup-order/) · [Compose teardown](https://docs.docker.com/reference/cli/docker/compose/down/)

## When the behavior requires the managed dev platform

- Use the project's supported, authorized ephemeral deployment procedure. Deploy only what the test needs. Isolate each run with a unique namespace and temporary resources, minimally scoped dev credentials, and synthetic data. Verify that the deployed runtime and service features match the contract under test.
- Set bounded provisioning and test timeouts. Record resource identifiers for teardown. Collect test results and diagnostic logs, then clean up resources owned by the run even when provisioning or tests fail. Use expiry or a cleanup job when supported as a fallback for interrupted runs. Verify deletion and report any leftovers.
- Keep service-backed checks identifiable in CI. If the environment is unavailable, run the tests that still cover independent behavior and record the remaining integration gap. Avoid silently substituting a double for behavior that requires the real platform.

## Spark example

Unit-test independent logic such as input validation or parameter selection with regular values. For DataFrame transformations, run the real transformation on small, explicit-schema inputs with a compatible local Spark runtime where supported. Force evaluation and compare rows, multiplicity, and relevant schema. Check order only when it is promised. Exercise relevant nulls, duplicates, or types. Use the version's DataFrame comparison utilities when available. Avoid mocking Spark's fluent calls to infer transformation correctness.

Use the actual connector or a temporary dev deployment for guarantees that require it, such as a managed catalog's permissions, a platform-specific job runtime, or a distributed behavior that local mode cannot reproduce. [Apache Spark, Testing PySpark](https://spark.apache.org/docs/latest/api/python/getting_started/testing_pyspark.html)
