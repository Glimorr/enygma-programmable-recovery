# Research scope and responsible disclosure

This is independent research on Rayls Enygma using locally operated development chains and pinned publicly available implementation sources.

The local experiment found a separation between protected settlement minting and repeated execution of an approved, intentionally non-idempotent application action during receiver recovery. It did not demonstrate a production exploit, an attacker-controlled trigger, a second mint or financial loss on deployed infrastructure.

The underlying observation was forwarded privately to Rayls maintainers for technical assessment. An ongoing or unanswered security report should not be described as maintainer confirmation of a bug. This public report does not require maintainer endorsement, nor does it imply endorsement.

The public repository includes the financial-state observations, locally mined transactions and receipt/root reports, derived results, code-level test mechanisms, integrity manifest and public post-experiment digest transaction. It excludes detailed fault-controller commands, operational reproduction scripts and some native service logs. Those files are preserved privately and accounted for in the release-disposition index.

An application-level logical-ID replay guard passed a supplementary hosted contract-level test. This is a demonstration of a possible mitigation, not a deployed protocol fix.

If new evidence changes the interpretation, corrections should be made as dated additions while preserving original measurements and cryptographic digests. The private archive should not be republished in full solely to improve a contributor evaluation.

For original architecture and source context, see [the official Rayls Enygma documentation](https://docs.rayls.com/docs/how-enygma-works) and the pinned [contracts](https://github.com/raylsnetwork/rayls-sovereign-contracts) and [relayer](https://github.com/raylsnetwork/rayls-sovereign-relayer) repositories.
