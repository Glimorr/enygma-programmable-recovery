# Evidence register

This register distinguishes independently readable records from evidence that remains in the researcher's confidential archive.

## What is publicly inspectable

| Evidence | Location | Scope |
| --- | --- | --- |
| Twelve measured trial rows, condition summaries and original order | [Confirmatory results](../evidence/derived/2026-11-04-confirmatory-results.json) | Three controls or interventions per condition |
| Six local retry block-time intervals | [Timeline data](../evidence/derived/2026-11-04-fault-retry-timelines.json) | Local destination timestamps, not independent wall clocks |
| Historical state for all twelve payments | [Measured directories](../evidence/raw/measured/) | Source debit, destination token supply, application effect, source refunds |
| 51 unique transaction/receipt/block observations | [Measured directories](../evidence/raw/measured/) | Local chain RPC evidence, including original transaction hashes |
| 51 saved transaction and receipt root reconstruction reports | [Measured directories](../evidence/raw/measured/) | Local header/root consistency |
| Three source refund correlations | [Measured directories](../evidence/raw/measured/) | Mined compensation transactions and balances |
| Five intentionally corrupted-copy sensitivity outcomes | [Sensitivity results](../evidence/derived/F2-02-forensic-sensitivity.json) | Forensic verifier detection test |
| Contract and receiver tests | [Research tests](../lab/) | Independent hosted computation against pinned official source |
| Post-experiment public hash transaction | [Rayls Testnet record](../audit/enygma-public-testnet-commitment.json) | Existence of the final archive-manifest SHA-256 by its block |
| Original 289-artifact archive manifest | [Original manifest](../audit/novw1-private-evidence-manifest.json) | Hashes of all original archived files, including withheld ones |
| Public release completeness and withholding disposition | [Public file index](../audit/public-file-index.json) and [Disposition](../audit/archive-disposition.json) | Exact mapping from original artifacts to published or withheld status |

All original receipt/root reports are preserved byte-for-byte. No local private-chain transaction is represented as a Rayls Public Testnet transfer.

## Verify the released data

From a fresh clone of this public repository, run:

    python3 -B scripts/check_evidence.py
    python3 -B scripts/check_release.py
    python3 -B scripts/verify_public_commitment.py

The first command checks twelve historical-state reconciliations and 51 unique locally captured transaction/receipt/block records and their **saved, locally computed** root reports. The second validates every published artifact against the release index, including all 289 original-file dispositions. The third checks the committed manifest hash against the saved Rayls Public Testnet record. Add --online to the third command for a live public RPC query.

GitHub Actions also runs the released-data checker and independently executes source-pinned contract and receiver tests. This is an independently run analysis of archived researcher-controlled evidence; it does not reproduce an externally operated three-chain network.

## Intentionally withheld material

The original archive also contains detailed receiver fault-controller instructions and session records, native relayer/CTS operational logs, internal runner commands and other privileged setup materials. They remain in the researcher's preserved private archive because a security-relevant observation is still under assessment.

The complete [archive disposition](../audit/archive-disposition.json) identifies **each** of the 289 original manifest entries as either publicly released (with its original hash) or explicitly withheld. Therefore a missing referenced public file is detectable, and a deliberately withheld file is not misleadingly presented as independently inspectable.

The original manifest is committed publicly as a single digest **after** the experiment. Public availability of that digest cannot prove the contents of a withheld file. It protects byte identity of files that are made available and supports later comparisons with the sealed archive.

## Remaining evidence boundary

The original source, Hub and destination validators were operated by the researcher. Root comparison against those nodes is local-chain integrity verification, not third-party consensus. A complete independently operated full-network reproduction has not been completed.

The original trial plan had no independent pre-experiment timestamp, and three repetitions per condition limit generalization. The findings should be understood as a documented behavior of this particular controlled deployment, not a demonstrated production-wide failure rate.
