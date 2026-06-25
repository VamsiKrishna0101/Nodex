# Changelog

## 0.1.1

### Fixed

- Fixed middleware state continuity across LangGraph node transitions.
- Middleware now receives the active `_current_node` and accumulated `_trace` instead of blank internal state.
- Routed nodes now update middleware-visible current-node state to the selected route target.

## 0.1.0

### Added

- Initial Nodex release with decorator-based nodes, middleware, routing, tracing, CLI helpers, examples, docs, and PyPI publishing.