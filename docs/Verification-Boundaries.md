---
layout: research-page
title: "Independent Verification Boundaries"
doc_number: "03"
doc_kind: "VERIFICATION METHOD"
doc_filename: "Verification-Boundaries.md"
summary: "Trace which checks establish archive consistency, independently executed code behavior, executable identity, and the public testnet commitment."
---

# Independent Verification Boundaries

There are four distinct checks in this research package. They have different evidentiary force and must not be described as interchangeable.

## Archived local-chain evidence

The original source, Hub and destination nodes were controlled by the experiment operator. The fifty-one saved EVM receipt observations were re-queried while those nodes were live; transaction and receipt roots were independently recomputed against the headers returned by those same local networks. Historical balances, supply changes, application calls and refunds reconcile across twelve measured trials.

That verifies consistency of the captured local ledgers. It does not independently authenticate validator consensus outside the operator's environment.

## Hosted verification of the archive

GitHub Actions checks out the published, disclosure-reviewed evidence package on a newly provisioned runner. It validates file digests and the complete local trial accounting without using the original Ubuntu workspace. This is independently executed verification code applied to previously captured evidence.

It does not convert the source data into an externally governed blockchain history.

## Hosted contract and relayer tests

Separate GitHub-hosted jobs use the exact upstream Rayls contracts and relayer revision. The Solidity tests exercise transaction-level mint and program-call behavior, including repeated dispatch. The Go receiver test exercises the pending-recovery decision with mock service dependencies.

These tests establish a reproducible code-level mechanism. They do not represent a newly initialized network running a real source transfer through Hub proofs, encrypted messaging, CTS and a destination relayer.

## Hosted relayer binary reconstruction

The experimental runtime executable was first compared byte-for-byte with a local build from pinned official source and the opt-in fault-injection tag. A separate GitHub job rebuilt both binaries inside the exact original Go 1.26.4 Bookworm toolchain image. Both complete SHA-256 digests matched the original executables: normal build 22818e7004ede76190e345475d32b48ec40fb80c38895d1ce8d52e42b6f430c0; fault-injection build e2afba6b1e4124277f65d2d8ccf7526410a10423fd12ea77a4af24c946833856. The independent run is recorded at https://github.com/Glimorr/enygma-programmable-recovery/actions/runs/41898148540 .

The first hosted build did not match because its build environment differed; the failure was preserved and the exact original container build was rerun. The passing result is reproducibility of the executables, not independent reproduction of the private networks.

## Full independent network replication

A second complete three-chain Enygma deployment on independently operated infrastructure has **not** been executed. The original Docker environment used eighteen concurrent runtime containers and multiple stateful volumes. The standard private GitHub-hosted Linux runner offers 2 CPUs, 8 GB RAM and 14 GB SSD; this is smaller than the original environment's operational footprint, before accounting for full proof and chain state.

A complete independent replication would require a separately provisioned host with suitable disk and memory, a fresh pinned deployment, independently controlled signing keys, template authorization, newly initiated original payment references and a separate witness package. The private reproduction steps must remain under disclosure controls. Replaying an existing receipt, rerunning an offline mock or starting more containers on the same operator host would not constitute that independent test.

## Public testnet digest

The sealed 32-byte SHA-256 manifest digest was included in [Rayls Public Testnet transaction 0x397f1979a00ad430f1b925c62d3b14ced83eb294ebc775269865a38d87e855db](https://testnet-explorer.rayls.com/tx/0x397f1979a00ad430f1b925c62d3b14ced83eb294ebc775269865a38d87e855db), block 22,398,118, on November 4, 2026 at 19:57:39 UTC. Both public explorer data and direct RPC transaction/receipt queries confirm the same input digest and successful zero-value transaction. It establishes a public timestamp for the final archived digest, not independent private-chain settlement, truth of the underlying local results or preregistration before the experiment. The public receipt is preserved at audit/enygma-public-testnet-commitment.json; its metadata can be checked offline or re-queried online via scripts/verify_public_commitment.py.

The original comprehensive archive remains privately preserved. The public evidence subset and all deliberately withheld archive artifacts are tracked in the release disposition index. Any claim that requires the withheld control logs is explicitly labeled as a private observation, not public independent reproduction.

No conclusion in the research report relies on an unsupported claim that these mechanisms provide the same kind of evidence.
