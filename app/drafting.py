import json
from pathlib import Path
from .model import classify
from .schemas import DraftRequest, Proposal

ROOT = Path(__file__).resolve().parent.parent

def catalogue():
    return json.loads((ROOT / "data/catalogue.json").read_text(encoding="utf-8"))

def select(rows, identifier):
    return next((row for row in rows if row["id"] == identifier), None)

def draft(req: DraftRequest) -> Proposal:
    data = catalogue()
    package = select(data["packages"], req.package_id)
    template = select(data["templates"], req.template_id)
    if package is None or template is None:
        raise ValueError("Select an available package and template.")
    evidence = classify(req.notes)
    questions, missing, conflicts = [], [], []
    if package.get("recommended"):
        missing.append("Package recommendations need scope agreement")
        questions.append("Which recommended scope items and deliverables should be included in the agreed project?")
    for value, label, question in [
        (req.client_name, "Client name", "What is the client name?"),
        (req.target_timeline, "Target timeline", "What target timeline should be reviewed and confirmed?"),
        (req.approver, "Client approver", "Who will approve deliverables and confirm acceptance criteria?"),
    ]:
        if not value:
            missing.append(label)
            questions.append(question)
    price = package.get("pricing")
    if price and price.get("approved") is True and price.get("source") and price.get("text"):
        commercial = [price["text"], "Source: " + price["source"]]
    else:
        commercial = ["Pricing requires confirmation"]
        missing.append("Approved pricing")
        questions.append("What pricing has been authorized for this package?")
    for row in evidence:
        if row["category"] == "commercial_unverified":
            missing.append("Commercial information in notes is unverified")
            continue
        if any(word.lower() in row["text"].lower() for word in package.get("exclusion_keywords", [])):
            conflicts.append("Potential scope conflict — review this discovery statement against package exclusions: " + row["text"])
        if row["category"] == "question":
            questions.append("Please resolve this discovery item: " + row["text"])
    if conflicts:
        questions.append("How should the flagged discovery statements be reconciled with the package exclusions?")
    questions.append("Do the selected package scope, deliverables, dependencies and assumptions match the discovery requirements?")
    summary = [f"This proposal outlines the {package['name']} engagement for {req.client_name or 'the client'}. Review the proposed work and outputs below, then resolve the listed questions before agreeing delivery."]
    if req.target_timeline:
        summary.append("Requested timeline (not committed): " + req.target_timeline)
    elif package.get("recommended_timeline"):
        summary.append("Planning recommendation: " + package["recommended_timeline"] + ". Confirm after reviewing scope, access and client availability; this is not a committed deadline.")
    if req.approver:
        summary.append("User-supplied approver: " + req.approver)
    objectives = ["Unconfirmed discovery objective: " + x["text"] for x in evidence if x["category"] == "objective"]
    if not objectives:
        objectives = ["Objectives require confirmation"]
        missing.append("Confirmed objectives")
        questions.append("What project objectives should this proposal address?")
    sections = {
        "project_summary": summary, "objectives": objectives,
        "scope_items": package["scope"], "deliverables": package["deliverables"],
        "assumptions": package["assumptions"], "exclusions": package["exclusions"],
        "milestones": [m + " — [Date to be confirmed]" for m in package["milestones"]],
        "dependencies": package["dependencies"], "client_questions": list(dict.fromkeys(questions)),
        "commercial_details": commercial,
        "discovery_evidence": [f"[{x['category']}; unconfirmed] {x['text']}" for x in evidence],
        "missing_information": list(dict.fromkeys(missing)), "conflicts": conflicts or ["No keyword-based conflicts detected; manual scope review is required."],
    }
    return Proposal(title="Proposal & Scope of Work", client_name=req.client_name or None,
        template_id=template["id"], template_version=template["version"], template_approved=template["approved"],
        fixed_wording=template["fixed_wording"], section_order=template["section_order"], sections=sections,
        classified_notes=evidence, source_references=[
            {"source": "service_package", "id": package["id"], "version": package["version"], "status": "recommended" if package.get("recommended") else "sample" if package.get("sample") else "configured", "sections": "scope_items,deliverables,assumptions,exclusions,milestones,dependencies,commercial_details"},
            {"source": "approved_template" if template["approved"] else "neutral_template", "id": template["id"], "version": template["version"], "sections": "fixed_wording,section_order"},
            {"source": "discovery_note", "id": "current_input", "version": "1", "sections": "objectives,discovery_evidence"}])
