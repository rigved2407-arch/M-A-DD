from app.models import Organization, PLANS


def get_plan(org: Organization) -> dict:
    return PLANS.get(org.plan, PLANS["free"])


def check_deal_limit(org: Organization) -> tuple[bool, str]:
    plan = get_plan(org)
    limit = plan["deals"]
    if limit == -1:
        return True, ""
    if org.deal_count >= limit:
        return False, f"Deal limit of {limit} reached for {org.plan} plan"
    return True, ""


def check_user_limit(org: Organization) -> tuple[bool, str]:
    plan = get_plan(org)
    limit = plan["users"]
    if limit == -1:
        return True, ""
    if org.user_count >= limit:
        return False, f"User limit of {limit} reached for {org.plan} plan"
    return True, ""


def check_document_limit(org: Organization) -> tuple[bool, str]:
    plan = get_plan(org)
    limit = plan["documents"]
    if limit == -1:
        return True, ""
    if org.document_count >= limit:
        return False, f"Document limit of {limit} reached for {org.plan} plan"
    return True, ""


def has_feature(org: Organization, feature: str) -> bool:
    plan = get_plan(org)
    features = plan["features"]
    if "all" in features:
        return True
    return feature in features
