#!/usr/bin/env python3
"""Verify a post-experiment Rayls testnet digest commitment.

Default mode verifies the pinned archive and the saved public-chain proof metadata.
With --online, independently requery the live Rayls Testnet JSON-RPC receipt,
transaction and block header. No private keys, writes or transactions.
"""
import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"audit/novw1-private-evidence-manifest.json"
RECORD=ROOT/"audit/enygma-public-testnet-commitment.json"
EXPECTED_CHAIN_ID=7295799
EXPECTED_WALLET="0xfe64d1860ee4bf7986d165ad105d2ed404e7a1f2"
RPC_URL="https://testnet-rpc.rayls.com/"

def rpc(method,params):
    allow={"eth_chainId","eth_getTransactionByHash","eth_getTransactionReceipt","eth_getBlockByHash"}
    if method not in allow:raise ValueError("RPC method not permitted in read-only verifier")
    payload=json.dumps({"jsonrpc":"2.0","id":7,"method":method,"params":params}).encode()
    request=urllib.request.Request(RPC_URL,data=payload,headers={
        "Content-Type":"application/json","User-Agent":"EnygmaRecovery-ReadOnly-EvidenceVerifier/1.0"
    })
    with urllib.request.urlopen(request,timeout=15) as stream:data=json.load(stream)
    if data.get("error"):raise ValueError("RPC error "+str(data["error"])[:160])
    return data["result"]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--online",action="store_true",help="Query public RPC instead of relying on saved metadata")
    args=parser.parse_args()
    saved=json.loads(RECORD.read_text())
    digest="0x"+hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    assert saved["schema"]=="enygma-public-testnet-evidence-digest/v1"
    assert saved["chainId"]==EXPECTED_CHAIN_ID
    assert saved["from"].lower()==saved["to"].lower()==EXPECTED_WALLET
    assert saved["valueWei"]==0
    assert saved["input"].lower()==saved["expectedManifestSha256"].lower()==digest
    assert saved["explorerUrl"]=="https://testnet-explorer.rayls.com/tx/"+saved["transactionHash"]
    assert len(saved["transactionHash"])==66
    assert saved["checks"] and all(saved["checks"].values())
    assert saved["blockNumber"]>0 and saved["gasUsed"]>0
    if args.online:
        chain=int(rpc("eth_chainId",[]),16)
        tx=rpc("eth_getTransactionByHash",[saved["transactionHash"]])
        receipt=rpc("eth_getTransactionReceipt",[saved["transactionHash"]])
        assert tx and receipt
        block=rpc("eth_getBlockByHash",[receipt["blockHash"],False])
        assert chain==EXPECTED_CHAIN_ID
        assert int(receipt["status"],16)==1
        assert tx["from"].lower()==tx["to"].lower()==EXPECTED_WALLET
        assert int(tx["value"],16)==0
        assert tx["input"].lower()==digest
        assert receipt["transactionHash"].lower()==saved["transactionHash"].lower()
        assert receipt["blockHash"].lower()==block["hash"].lower()==saved["blockHash"].lower()
        assert int(receipt["blockNumber"],16)==saved["blockNumber"]
        assert saved["transactionHash"].lower() in [x.lower() for x in block["transactions"]]
    print(json.dumps({
        "public_commitment":"VERIFIED" if args.online else "SAVED_PROOF_AND_DIGEST_MATCHED",
        "mode":"LIVE_PUBLIC_TESTNET_RPC" if args.online else "OFFLINE_SAVED_METADATA",
        "chainId":saved["chainId"],"txHash":saved["transactionHash"],
        "block":saved["blockNumber"],"digest":digest,
        "classification":"POST-EXPERIMENT PUBLIC EVIDENCE HASH, NOT PRIVATE TRANSFER CONSENSUS"
    }))
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("ANCHOR_VERIFICATION_FAILED "+str(exc),file=sys.stderr)
        raise SystemExit(1)
