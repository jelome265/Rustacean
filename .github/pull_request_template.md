## Summary

<!-- What changes, and why. Link the requirement or issue. -->

## Checklist

- [ ] Every required CI check is green (ci, security, codeql).
- [ ] No rule relaxed. Any exception is recorded as an ADR with owner and expiry.
- [ ] If a skill changed: `tools/validate_skills.py skills` passes and rule IDs resolve.
- [ ] If a framework policy changed: the change is justified, and the gate test cases still pass.
- [ ] No secret, token, or personal data in the diff, the logs, or the test fixtures.
- [ ] No requested production behavior is represented by a placeholder, stub, no-op, or hard-coded success.
- [ ] Integration/contract/E2E claims use real adapters and dependencies; mocks are limited to isolated unit tests.
- [ ] Claims in this PR map to actual verification results; skipped or blocked checks are disclosed.
- [ ] Documentation updated where behaviour changed.

## Merge

This pull request is **not merged by automation**. A code owner reviews and merges it.
