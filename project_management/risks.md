# Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| Assigned maze generator incompatible interface | High | Adapted our loader to their API |
| Circular imports between engine/ghost/player | Medium | Used `TYPE_CHECKING` guard |
| mypy strict mode failures close to deadline | Medium | Fixed incrementally per module |
| Git merge conflicts (two active contributors) | Low | Frequent pulls, small commits |