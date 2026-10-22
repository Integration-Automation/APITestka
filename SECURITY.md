# Security policy

## Supported versions

Security fixes are provided for the latest release and the default
branch. Older releases are not supported. Upgrade before reporting
an issue that may already be fixed.

## Reporting a vulnerability

Do not open a public issue, pull request, or discussion for a suspected
vulnerability.

Use either private channel:

- **GitHub Security Advisories.** Open a private report from this
  repository's Security tab, **Report a vulnerability**. This is the
  preferred channel.
- **Email.** `jechenmailman@gmail.com`, with a subject line that begins
  with `[SECURITY]`.

Include the affected version, platform, impact, and steps to reproduce.
Do not attach credentials, tokens, or unredacted logs.

The maintainers aim to acknowledge a report within 5 business days, and
to coordinate a fix and disclosure within 90 days. There is no bug-bounty
promise.

## Operational notes

Request arguments and assertion results are written to the INFO log, under
the home directory or at ``APITESTKA_LOG_FILE``. Do not put live credentials
in a run whose log will be shared.

TLS certificate verification stays on unless the caller turns it off.

Until a host closes the package gate, an action list can still import an
arbitrary package; the loader warns and continues. Close the gate before
running an action list you do not trust.

A SOAP call rebuilds request headers. Do not assume headers you passed in
are still present when SOAP is enabled.
