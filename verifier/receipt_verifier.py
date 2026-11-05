#!/usr/bin/env python3
"""Cross-check RPC observation consistency; does not validate consensus/inclusion proof."""
import argparse
import json
import re
import sys
from pathlib import Path
HEX=re.compile(r"^0x[0-9a-f]{64}$")
def valid_hash(x):return isinstance(x,str) and bool(HEX.fullmatch(x.lower()))
def verify(obs):
    errs=[]
    if obs.get("schema")!="nov-w1-rpc-observation/v1":errs.append("schema")
    tx=obs.get("transaction");rec=obs.get("receipt");block=obs.get("block")
    if not all(isinstance(x,dict) for x in [tx,rec,block]):return ["missing transaction/receipt/block objects"]
    th=tx.get("hash");rh=rec.get("transactionHash")
    bh=block.get("hash")
    if not valid_hash(th) or not valid_hash(rh) or th.lower()!=rh.lower():errs.append("transaction hash mismatch")
    if not valid_hash(bh) or not valid_hash(rec.get("blockHash")):errs.append("invalid block hash")
    elif bh.lower()!=rec["blockHash"].lower():errs.append("receipt block mismatch")
    if not valid_hash(tx.get("blockHash")) or not valid_hash(bh) or tx["blockHash"].lower()!=bh.lower():
        errs.append("tx block mismatch")
    if rec.get("blockNumber")!=block.get("number") or tx.get("blockNumber")!=block.get("number"):
        errs.append("block number mismatch")
    if not valid_hash(th) or th.lower() not in [x.lower() for x in block.get("transactions",[]) if isinstance(x,str)]:
        errs.append("transaction not listed in block")
    if rec.get("status") not in ["0x0","0x1","0x00","0x01"]:errs.append("receipt missing EVM status")
    if not isinstance(obs.get("chain_id"),str) or not obs["chain_id"].startswith("0x"):
        errs.append("chain ID missing")
    if not isinstance(rec.get("logs"),list):errs.append("receipt logs missing")
    else:
        for log in rec["logs"]:
            if not isinstance(log,dict) or log.get("transactionHash","").lower() != (th or "").lower():
                errs.append("log transaction hash mismatch")
                break
    return errs
def main():
    p=argparse.ArgumentParser()
    p.add_argument("observation",type=Path)
    args=p.parse_args()
    errors=verify(json.loads(args.observation.read_text()))
    print(json.dumps({"consistent":not errors,"errors":errors,
        "qualification":"RPC self-consistency only; external consensus not verified"}))
    return 0 if not errors else 1
if __name__=="__main__":sys.exit(main())
