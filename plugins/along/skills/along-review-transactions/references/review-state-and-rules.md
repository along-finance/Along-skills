# Review state, assignments and rules

Inspect the selected app's documented and observed capabilities for each operation. Treat `observed`, `documented-unverified`, `unsupported` and `unknown` separately. Capability discovery does not authorize a write.

## Native review operations

For marking a transaction reviewed or assigning it to a household member, use the exact app transaction IDs and show the current and proposed state. Do not infer a person from the account owner, merchant or login. A broad queue can be reviewed in one run, but a bulk state change needs a fixed observed set or a proposal naming the predicate, count and exclusions. Verify by reopening the rows after saving.

For every operation, preserve source identity, amount, account, date, category and existing relationships unless that field is explicitly in scope. If a split or another native operation clears a review flag, changes assignment, creates children or changes exclusions, treat that as a reported side effect. Reapply or accept the side effect only when the capability and approval cover it.

## Rule preview

Before creating or changing a rule, preview:

- the exact predicate, including merchant/description fields and case or substring semantics;
- observed historical matches, the predicate governing future arrivals, and rows excluded by account, category, owner or date;
- current rule order or precedence, conflicts and the fields that would change;
- exceptions the household wants preserved, including deliberate one-off categories;
- the reversibility path and the fixed approval scope.

One ambiguous transaction supports a question or one-off category, not a global rule. A repeated, explicit household preference can support a rule proposal. Apply only after the user has approved the preview or precisely requested that exact rule and its scope. If the app cannot expose affected rows or rule semantics, keep the preview provisional and do not mutate the rule.

