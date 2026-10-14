# Security policy

## Reporting a vulnerability

Do not open a public issue for a security problem.

Report it privately through GitHub's private vulnerability reporting for this repository
(Security tab, then "Report a vulnerability"). Include the affected file, the steps to
reproduce, and the impact you expect.

We aim to acknowledge reports within 5 working days; this is a target, not a guaranteed response
window. Include the affected file, reproducible steps, and impact, but do not include live
credentials, access tokens, private keys, or unnecessary customer/personal data. Confirmed
issues are triaged, fixed and tested before coordinated disclosure when appropriate.

## Scope

This repository contains engineering guidance, gate scripts, and a conformance crate. It
does not run a service. Reports about a rule that is wrong or unsafe, an installer that writes to an unsafe destination,
or a gate that can be bypassed unexpectedly are in scope.
