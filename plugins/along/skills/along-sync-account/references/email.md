# Scoped email evidence or MFA

Email is optional. Use existing receipts, app attachments, merchant evidence or user context when sufficient. Read [authentication](authentication.md); mailbox access is not implied by finance-app access.

1. Establish one authorized purpose: receipt/context search for named merchant/transaction, amount and date window; or current MFA retrieval for a named service. Resolve missing owner/service/scope before access. Reuse valid authorization within its recorded scope, not a blanket historical permission.
2. Prefer an available supported read-only mail connector; otherwise use the user's browser/password-manager route. Verify mailbox owner, intended sender/service domain, message recency and transaction/challenge context. If verification fails, request a verified route or user-provided receipt/code; do not widen the search.
3. Extract only fields needed for the case. Match receipt tenders to the actual charged transaction; one receipt may support several transactions only with an evidenced allocation. For MFA use only the current code for that verified challenge and keep it out of saved records, logs and reports. Respect human-required security challenges.
4. Keep this procedure read-only: no sending/forwarding, deleting/archiving, filtering-rule or credential changes. Native receipt forwarding is a separate explicitly authorized send, not part of evidence retrieval. Preserve existing user-managed sessions. Revoke task-specific access only when the user requested that cleanup and the target is unambiguous.
5. Save a minimal checkpoint under the private root: purpose/scope, verified owner/service, route reference, observed time, result/limitations and revocation state. Store receipt facts needed for the case rather than unrelated bodies; never save passwords, codes, recovery keys or session tokens. Pass receipt provenance to transaction review; MFA results only to the named service flow.

Finish with the scoped result or specific missing human action. A saved route is not permanent access or permission for a new search.
