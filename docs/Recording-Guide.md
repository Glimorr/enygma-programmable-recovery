# Three silent research videos

Record the actual evidence displays without repeating transfers or performing interventions during capture. Voiceover can be written after the three silent recordings are finished.

## Video 1 — Does settlement imply exactly-once application execution?

Open with the practical question, then show the local Sovereign-to-Hub-to-Sovereign architecture. Explain the deliberately non-idempotent approved observer application. Display the normal controls and rejected-action compensation conditions.

Use the public historical-state files and the results table to show three ordinary transfers with one destination mint and one application action, and three rejected applications with mined source refunds and zero destination application effects.

State plainly that these are locally executed development-chain observations.

## Video 2 — What did recovery change?

Show the two separate receiver-interruption conditions and the six preserved outcomes. Contrast the first and retry destination transactions for one representative trial, including distinct transaction hashes and identical approved program input. Display the mint/action bar chart and the block-time retry intervals.

The conclusion is narrow: in the six controlled local interruption observations, the second destination execution repeated the application effect but not the settlement mint. Do not claim a second mint, a public-chain private settlement or an exploitable production deployment. Do not demonstrate fault-injection commands publicly.

## Video 3 — Can the evidence be checked?

Run the public, read-only release verifier:

    python3 -B scripts/check_evidence.py
    python3 -B scripts/check_release.py
    python3 -B scripts/verify_public_commitment.py --online

Show the GitHub Actions jobs for the pinned contract-level and relayer code tests and the independent byte-identical executable rebuild. Open the Rayls Public Testnet transaction, explain its exact SHA-256 input, and identify it as a post-experiment integrity commitment only.

Close with the unresolved boundaries: the original ledgers were operator-controlled, the initial plan lacked a pre-experiment external timestamp, and no externally operated full-network reproduction has been completed.

## Capture review

Screen-record at a legible resolution. Inspect every terminal and browser scene for credentials, local private-key files, confidential fault-controller endpoints or unrelated personal information. Check all links and numerical claims against the public evidence index.

These videos describe completed measurements. They must not present the separately prepared, unexecuted fresh-genesis trials as a confirmation.
