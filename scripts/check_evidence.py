#!/usr/bin/env python3
"""Inspect the released local-chain research evidence without any network requests.

Verifies the published *recorded local* receipts and saved root reconstruction
reports against the locally returned block headers. This is evidence
self-consistency, not independent consensus attestation or a live retry.
"""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"verifier"))
from receipt_verifier import verify as check_observation

AMOUNT=10**17
CODES={"C0":(3,1,1,0),"C1":(3,0,0,3),"F1":(3,1,2,0),"F2":(3,1,2,0)}

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def verify():
    src=ROOT/"evidence/raw/measured"
    report=load(ROOT/"evidence/derived/2026-11-04-confirmatory-results.json")
    assert report["trial_count"]==12 and len(report["rows"])==12
    assert set(report["conditions"])==set(CODES)
    assert len([x for x in src.iterdir() if x.is_dir()])==12

    source_n=0;receipt_n=0;seen=set();refund_n=0
    for row in report["rows"]:
        code=row["condition"];trial=row["trial"]
        assert code in CODES and trial.startswith(code+"-")
        n,mints,effects,refunds=CODES[code]
        assert len([x for x in report["rows"] if x["condition"]==code])==n
        assert row["destination_mints"]==mints,trial
        assert row["application_effects"]==effects,trial
        assert bool(row["refund_verified"])==(refunds>0),trial

        directory=src/trial
        state=load(directory/"historical-state.json")
        assert state["passed"] is True and not state["errors"]
        assert state["trial_id"]==trial and state["condition"]==code
        source=state["source"]
        assert source["balance_before"]-source["balance_after"]==AMOUNT,trial
        assert source["supply_before"]-source["supply_after"]==AMOUNT,trial
        destinations=state["destination"]
        assert len(destinations)==effects,trial
        assert sum(x["observer_after"]-x["observer_before"] for x in destinations)==effects,trial
        assert sum(x["token_supply_after"]-x["token_supply_before"] for x in destinations)==AMOUNT*mints,trial
        assert sum(x["token_balance_after"]-x["token_balance_before"] for x in destinations)==AMOUNT*mints,trial
        assert len({x["tx"] for x in destinations})==len(destinations),trial
        for x in destinations:
            assert x["observer_after"]-x["observer_before"]==1,trial
        if code in ("F1","F2"):
            assert [x["token_supply_after"]-x["token_supply_before"] for x in destinations]==[AMOUNT,0],trial
            assert [x["observer_after"]-x["observer_before"] for x in destinations]==[1,1],trial
        if code=="C1":
            refunded=state["refund"]
            assert refunded is not None
            assert refunded["balance_after"]==source["balance_before"],trial
            assert refunded["supply_after"]==source["supply_before"],trial
            assert refunded["balance_after"]-refunded["balance_before"]==AMOUNT,trial
            correlated=load(directory/"refund-correlated.json")
            assert correlated["refund_amount_base_units"]==str(AMOUNT) or correlated["refund_amount_base_units"]==AMOUNT
            assert correlated["refund_tx_hash"]==refunded["tx"],trial
            refund_n+=1
        else:
            assert state["refund"] is None,trial
        source_n+=1

        obs=list(directory.glob("*-rpc.json"))
        obs+= [p for p in (directory/"receipts").glob("*.json") if not p.name.endswith("-roots.json")]
        assert len(obs)>=2,(trial,len(obs))
        for file in sorted(obs):
            observation=load(file)
            errs=check_observation(observation)
            assert not errs,(str(file.relative_to(ROOT)),errs)
            rootfile=file.with_name(file.stem+"-roots.json")
            assert rootfile.exists(),str(rootfile)
            roots=load(rootfile)
            block=observation["block"];receipt=observation["receipt"];tx=observation["transaction"]
            assert roots["matched"] is True
            assert roots["receipt_root"].lower()==roots["calculated_receipt_root"].lower()==block["receiptsRoot"].lower()
            assert roots["transactions_root"].lower()==roots["calculated_transactions_root"].lower()==block["transactionsRoot"].lower()
            assert roots["block_hash"].lower()==block["hash"].lower()
            assert roots["target_transaction_hash"].lower()==tx["hash"].lower()
            assert roots["target_receipt_status"]==int(receipt["status"],16)
            assert roots["block_number"]==int(block["number"],16)
            assert int(roots["chain_id"])==int(observation["chain_id"],16)
            assert tx["hash"] not in seen,tx["hash"]
            seen.add(tx["hash"])
            receipt_n+=1

    for code,(n,mints,effects,refunds) in CODES.items():
        c=report["conditions"][code]
        assert c["n"]==n
        assert c["destination_mints"]==[mints]*n
        assert c["app_effects"]==[effects]*n
        assert c["successful_refunds"]==refunds
    assert source_n==12 and refund_n==3 and receipt_n==51
    return {"result":"PASS","trial_count":source_n,"refunded_controls":refund_n,
      "unique_local_transactions":len(seen),"receipt_header_consistency_checks":receipt_n,
      "status":"LOCAL OPERATOR-LEDGER EVIDENCE; NOT INDEPENDENT OUTSIDE CONSENSUS"}

if __name__=="__main__":
    try:print(json.dumps(verify(),sort_keys=True))
    except Exception as e:
        print("PUBLIC_EVIDENCE_VERIFICATION_FAILED",type(e).__name__,str(e),file=sys.stderr)
        raise SystemExit(1)
