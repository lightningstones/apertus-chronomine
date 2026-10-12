"""
Script to run Apertus v1.5-70B on the evaluation dataset and produce model_response.json
Meets Hack Apertus Track 2 requirement:
"Upload your dataset. It should consist of:
1. evaluation dataset (individual test cases)
2. model response dataset (the model response to each test case)
3. metadata file (licensing and dataset information)"
"""
import asyncio
import json
import os
import sys
from pathlib import Path

# Add track_2b to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.backend.provider import apertus_engine
from src.backend.models import BautagebuchRequest, SuvaAuditRequest

async def main():
    hf_dir = Path(__file__).resolve().parent.parent / "data" / "huggingface"
    eval_file = hf_dir / "evaluation_dataset.json"
    output_file = hf_dir / "model_response.json"

    with open(eval_file, "r", encoding="utf-8") as f:
        cases = json.load(f)

    responses = []
    print(f"Running evaluation benchmark on {len(cases)} cases using Apertus v1.5-70B ({apertus_engine.provider_mode})...")

    for case in cases:
        cid = case["id"]
        text = case["input"]
        lang = case.get("language", "de")
        domain = case["domain"]

        print(f"Evaluating {cid} [{domain}]...")

        if "SIA 118" in domain:
            req = BautagebuchRequest(
                raw_text=text,
                author_name="Frontline Miner / Chef de poste",
                author_role="Mineur",
                location_pk="PK 3.200",
                target_language="de" if lang != "de" else "fr"
            )
            res = await apertus_engine.generate_bautagebuch(req)
            resp_dict = {
                "id": cid,
                "domain": domain,
                "input": text,
                "model": apertus_engine.model,
                "model_output": res.model_dump(),
                "evaluation": {
                    "delay_detected_hours": res.delay_hours,
                    "regierapport_required": res.regierapport.is_required,
                    "sia_norm_referenced": res.regierapport.sia_reference,
                    "passed": res.regierapport.is_required == case.get("ground_truth_regie_required", True)
                }
            }
        else:
            req = SuvaAuditRequest(description=text)
            res = await apertus_engine.audit_suva_safety(req)
            resp_dict = {
                "id": cid,
                "domain": domain,
                "input": text,
                "model": apertus_engine.model,
                "model_output": res.model_dump(),
                "evaluation": {
                    "stop_work_order": res.stop_work_order,
                    "infracted_rules": [r.norm for r in res.infracted_rules],
                    "passed": res.stop_work_order == case.get("ground_truth_safety_hazard", True)
                }
            }

        responses.append(resp_dict)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(responses, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Model responses saved to: {output_file}")
    passed_count = sum(1 for r in responses if r["evaluation"]["passed"])
    print(f"Benchmark Accuracy: {passed_count}/{len(cases)} ({passed_count/len(cases)*100:.1f}%)")

if __name__ == "__main__":
    asyncio.run(main())
