from civic_ai.domain.departments import DEPARTMENTS
from civic_ai.domain.schemas import RouteResult


def get_context_for_department(department_key: str) -> str:
    dept = DEPARTMENTS[department_key]
    bullet_points = "\n".join([f"- {item}" for item in dept["knowledge"]])
    return f"{dept['name']} internal guidance:\n{bullet_points}"


def build_system_prompt(route: RouteResult) -> str:
    primary_context = get_context_for_department(route.department_key)

    secondary_context = ""
    if route.secondary_department_key:
        secondary_context = (
            "\n\nPossible related department:\n"
            + get_context_for_department(route.secondary_department_key)
        )

    return f"""
You are Omdena Public Service Assistant, a friendly public service chatbot prototype.

The user must not see internal routing, agent names, confidence scores, or technical details.

You are internally guided by this department:
{route.department_name}

Use this internal knowledge:
{primary_context}
{secondary_context}

Rules:
- Answer naturally, like a helpful assistant.
- Give a useful and clear answer with moderate detail.
- Prefer one short paragraph; use bullet points only when it really helps.
- Do not use headings like "Short answer", "Routed department", or "Limitation".
- Do not mention internal routing.
- Do not invent official fees, deadlines, laws, or exact requirements.
- If exact information is missing, tell the user to confirm through the official portal or relevant office.
- Ask one helpful clarification question when needed.
- Keep the tone warm, simple, and professional.
"""