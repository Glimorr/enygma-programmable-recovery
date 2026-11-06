---
layout: research-page
title: "Claims and Evidence"
doc_number: "04"
doc_kind: "CLAIMS & SOURCES"
doc_filename: "Claims-and-Evidence.md"
summary: "A claim-by-claim map of observed results, supporting records, and the difference between measurements and interpretation."
---

# Claims and Evidence

This document separates observed behavior from interpretation and open questions.

## Supported findings

- On the original operator-controlled source and destination Sovereign chains, twelve measured transfers completed the planned observation windows. Six fault-instrumented cases produced two successful application-observer executions for one logical payment. Local token settlement still minted once per payment.
- Three normal controls produced one destination application effect per payment. Three deliberately rejected applications produced no destination effect and completed mined refunds restoring their source balance.
- Fifty-one locally re-queried transaction receipts and root reports match the corresponding local chain headers. Twelve historical balance and supply reconciliations passed.
- The executable bytes of the original normal and test-only instrumented relayers were reconstructed on a GitHub-hosted machine with the same SHA-256 digests. Hosted Go and Solidity tests exercise the relevant recovery and settlement mechanisms.
- The sealed archive manifest hash was committed to Rayls Public Testnet in transaction 0x397f1979a00ad430f1b925c62d3b14ced83eb294ebc775269865a38d87e855db, block 22,398,118. This is a post-experiment digest commitment.

## What these results do not establish

- They do not establish that any deployed production application was exploited, that the original local ledgers were independently validated by outside consensus, or that Rayls Public Testnet contains the private Enygma payment receipts.
- They do not establish an external timestamp for the original trial plan before the measured experiments.
- They do not show a second token mint; the observed divergence concerns an application effect.
- The test-only relayer interruption is not proof an unprivileged actor can induce the same condition on a production deployment.
- The second fresh-genesis stack was initialized, but its planned eight measured transfers were not executed. It is not a second confirmation.

## Technical interpretation

The research question is whether transaction-level atomicity and token reference-ID deduplication should imply at-most-once execution of approved programmable actions across receiver recovery. Our instrumented local evidence demonstrates that these properties can diverge. A guarded application control, run in the hosted Solidity test, suppresses the repeated side effect for the same logical ID.

Whether the protocol promises at-most-once application execution, or instead delegates that property to the application author, is not settled by our experiment. The finding was privately forwarded to maintainers as a security-relevant observation; no maintainer determination has been recorded.

A credible public research description should say **observed replay of an approved application effect in a controlled local receiver-recovery experiment**, not **confirmed Rayls production vulnerability**. Attribution and severity must be kept conditional.

## External verification

The public GitHub repository contains a disclosure-reviewed set of local receipts, historical state, original figures, hosted code tests and the public digest receipt. The full original archive remains private. A hosted verifier independently executes the checks against the saved evidence. That increases auditability but does not change who operated the original chain.

A fully independently operated multi-chain replication remains an open scientific improvement, not a completed result.
