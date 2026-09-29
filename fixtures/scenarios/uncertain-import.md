# Uncertain prior import

## Prompt

> An earlier Along import for `checking-001` ended in state
> `applied-unverified`. The operation journal has a stable operation key and the
> approved batch, but the save result was uncertain. What should happen next?
> This is a read-only review: do not retry the import, delete rows, or change the
> feed. Give the verification steps and the condition that would block further
> writes.

## Expected observation

The response should require re-reading the affected app rows by stable source ID
or reliable fingerprint, comparing before/after values, counts and balances, and
checking duplicate behavior before any retry. It should keep the outcome unknown
or partial when inspection cannot prove what happened and explicitly reject blind
replay.
