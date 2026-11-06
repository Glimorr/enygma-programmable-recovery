#!/usr/bin/env python3
"""Verify the post-experiment Rayls testnet archive-digest commitment.

Default mode verifies saved proof metadata against the sealed original
manifest. --online independently re-queries the official public testnet RPC
for the transaction, inclusion block and digest, and for the receipt status.
If that RPC omits a historical receipt, a separate Rayls Blockscout explorer
API supplies the publicly indexed success status. The resulting source is
always disclosed in the output; it is NOT private-chain consensus or trial
preregistration. No credentials, writes or transaction submissions.
"""
import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "audit/novw1-private-evidence-manifest.json"
RECORD = ROOT / "audit/enygma-public-testnet-commitment.json"
EXPECTED_CHAIN_ID = 7295799
EXPECTED_WALLET = "0xfe64d1860ee4bf7986d165ad105d2ed404e7a1f2"
RPC_URL = "https://testnet-rpc.rayls.com/"
EXPLORER_API = "https://testnet-explorer.rayls.com/api/v2/transactions/"


def rpc(method, params):
    allowed = {
        "eth_chainId", "eth_getTransactionByHash",
        "eth_getTransactionReceipt", "eth_getBlockByHash"
    }
    if method not in allowed:
        raise ValueError("RPC method not permitted in read-only verifier")
    payload = json.dumps({
        "jsonrpc": "2.0", "id": 7, "method": method, "params": params
    }).encode()
    request = urllib.request.Request(
        RPC_URL, data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "EnygmaRecovery-ReadOnly-EvidenceVerifier/1.0"
        }
    )
    with urllib.request.urlopen(request, timeout=15) as stream:
        data = json.load(stream)
    if data.get("error"):
        raise ValueError("RPC error " + str(data["error"])[:160])
    if "result" not in data:
        raise ValueError("Missing RPC result for " + method)
    return data["result"]


def explorer_transaction(txhash):
    """Read an independently served Blockscout transaction index record."""
    request = urllib.request.Request(
        EXPLORER_API + txhash,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
    )
    with urllib.request.urlopen(request, timeout=15) as stream:
        return json.load(stream)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--online", action="store_true",
        help="Query live Rayls Testnet RPC, with explorer-status fallback "
             "if the public RPC does not provide the historical receipt"
    )
    args = parser.parse_args()

    saved = json.loads(RECORD.read_text())
    digest = "0x" + hashlib.sha256(MANIFEST.read_bytes()).hexdigest()

    assert saved["schema"] == "enygma-public-testnet-evidence-digest/v1"
    assert saved["chainId"] == EXPECTED_CHAIN_ID
    assert saved["from"].lower() == saved["to"].lower() == EXPECTED_WALLET
    assert saved["valueWei"] == 0
    assert saved["input"].lower() == saved["expectedManifestSha256"].lower() == digest
    assert saved["explorerUrl"] == (
        "https://testnet-explorer.rayls.com/tx/" + saved["transactionHash"]
    )
    assert len(saved["transactionHash"]) == 66
    assert saved["checks"] and all(saved["checks"].values())
    assert saved["blockNumber"] > 0 and saved["gasUsed"] > 0

    status_source = "OFFLINE_SAVED_METADATA"
    if args.online:
        chain = int(rpc("eth_chainId", []), 16)
        tx = rpc("eth_getTransactionByHash", [saved["transactionHash"]])
        assert tx, "Public RPC did not return the transaction"

        block = rpc("eth_getBlockByHash", [tx["blockHash"], False])
        assert block, "Public RPC did not return the inclusion block"

        assert chain == EXPECTED_CHAIN_ID
        assert tx["hash"].lower() == saved["transactionHash"].lower()
        assert tx["from"].lower() == tx["to"].lower() == EXPECTED_WALLET
        assert int(tx["value"], 16) == 0
        assert tx["input"].lower() == digest
        assert tx["blockHash"].lower() == block["hash"].lower() == saved["blockHash"].lower()
        assert int(block["number"], 16) == saved["blockNumber"]
        assert saved["transactionHash"].lower() in [
            h.lower() for h in block["transactions"]
        ]

        # Some public RPC backends currently return null for older receipts
        # although they return the transaction and containing block.
        receipt = rpc("eth_getTransactionReceipt", [saved["transactionHash"]])
        if receipt:
            assert int(receipt["status"], 16) == 1
            assert receipt["transactionHash"].lower() == saved["transactionHash"].lower()
            assert receipt["blockHash"].lower() == block["hash"].lower()
            assert int(receipt["blockNumber"], 16) == saved["blockNumber"]
            status_source = "LIVE_PUBLIC_RPC_RECEIPT"
        else:
            explorer = explorer_transaction(saved["transactionHash"])
            assert explorer["hash"].lower() == saved["transactionHash"].lower()
            assert explorer["raw_input"].lower() == digest
            assert explorer["status"] == "ok"
            assert explorer["result"] == "success"
            assert str(explorer["value"]) in ("0", "0x0")
            status_source = "LIVE_PUBLIC_EXPLORER_STATUS"
        mode = "LIVE_PUBLIC_RPC_TX_BLOCK_WITH_" + status_source
    else:
        mode = "OFFLINE_SAVED_METADATA"

    print(json.dumps({
        "public_commitment": "VERIFIED" if args.online else "SAVED_PROOF_AND_DIGEST_MATCHED",
        "mode": mode,
        "status_source": status_source,
        "chainId": saved["chainId"],
        "txHash": saved["transactionHash"],
        "block": saved["blockNumber"],
        "digest": digest,
        "classification": "POST-EXPERIMENT PUBLIC EVIDENCE HASH, NOT PRIVATE TRANSFER CONSENSUS"
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("ANCHOR_VERIFICATION_FAILED " + repr(exc), file=sys.stderr)
        raise SystemExit(1)
