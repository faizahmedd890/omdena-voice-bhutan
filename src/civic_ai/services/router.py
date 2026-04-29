from civic_ai.domain.departments import DEPARTMENTS
from civic_ai.domain.schemas import RouteResult


def route_department(user_message: str) -> RouteResult:
    text = user_message.lower()
    scores = {}

    for dept_key, dept_data in DEPARTMENTS.items():
        matches = [kw for kw in dept_data["keywords"] if kw in text]
        scores[dept_key] = {
            "count": len(matches),
            "matches": matches,
        }

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1]["count"],
        reverse=True
    )

    top_dept, top_data = ranked[0]
    second_dept, second_data = ranked[1]

    if top_data["count"] == 0:
        return RouteResult(
            department_key="general",
            department_name=DEPARTMENTS["general"]["name"],
            confidence=0.35,
            matched_keywords=[]
        )

    confidence = min(0.95, 0.45 + 0.12 * top_data["count"])

    secondary_key = None
    secondary_name = None

    if second_data["count"] > 0:
        secondary_key = second_dept
        secondary_name = DEPARTMENTS[second_dept]["name"]

    return RouteResult(
        department_key=top_dept,
        department_name=DEPARTMENTS[top_dept]["name"],
        confidence=confidence,
        matched_keywords=top_data["matches"],
        secondary_department_key=secondary_key,
        secondary_department_name=secondary_name
    )