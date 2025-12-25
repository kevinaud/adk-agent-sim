# Contracts: E2E Test Suite

**Feature**: 002-e2e-test-suite  
**Date**: 2024-12-23

## Not Applicable

The E2E Test Suite does not expose any APIs or contracts.

This feature is **test infrastructure** that:
- Consumes the existing NiceGUI application via browser automation
- Validates the Simulator Run feature (Spec 001) via black-box testing
- Does not introduce new endpoints, schemas, or interfaces

### What Would Be Here for Other Features

For features that expose APIs, this directory would contain:
- OpenAPI specifications for REST endpoints
- GraphQL schemas for GraphQL APIs
- Protocol buffer definitions for gRPC services
- JSON Schema definitions for data formats

### Related Contracts

The application this test suite validates uses:
- NiceGUI's internal websocket protocol (not documented externally)
- ADK's `FunctionDeclaration` schemas (defined by Google ADK)
- Golden Trace JSON format (defined in Spec 001)

These are not documented here as they are external dependencies, not contracts exposed by this feature.
