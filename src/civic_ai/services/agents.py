from dataclasses import dataclass
from typing import Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage

from civic_ai.domain.departments import DEPARTMENTS
from civic_ai.domain.schemas import RouteResult


@dataclass
class DepartmentAgent:
    """
    Lightweight department-specific agent.

    This is not a fully autonomous agent yet.
    It is a specialized response agent with:
    - a department role
    - department-specific context
    - response rules
    - optional awareness of a related department
    """

    key: str
    name: str
    role: str
    knowledge: List[str]

    def build_context(self) -> str:
        return "\n".join([f"- {item}" for item in self.knowledge])

    def build_system_prompt(self, route: RouteResult) -> str:
        secondary_context = ""

        if route.secondary_department_key:
            secondary_department = DEPARTMENTS[route.secondary_department_key]
            secondary_knowledge = "\n".join(
                [f"- {item}" for item in secondary_department["knowledge"]]
            )

            secondary_context = f"""
Possible related service area:
{secondary_department["name"]}

Related guidance:
{secondary_knowledge}
"""

        return f"""
You are the {self.name} inside the Omdena Public Service Assistant.

Your role:
{self.role}

Important:
The user must not see internal routing, confidence scores, technical details, or agent names.

Department guidance:
{self.build_context()}

{secondary_context}

Response rules:
- Answer naturally, like a helpful public service assistant.
- Use the department guidance to answer the user's question.
- Give a clear and useful answer with moderate detail.
- Use bullet points only when they make the answer easier to understand.
- Do not mention that you are an internal agent.
- Do not mention routing.
- Do not invent official fees, laws, deadlines, or exact requirements.
- When information needs official confirmation, tell the user to verify through the official portal or relevant office.
- Ask one helpful clarification question if the user's request is incomplete.
"""


def build_agents() -> Dict[str, DepartmentAgent]:
    return {
        "business": DepartmentAgent(
            key="business",
            name="Business Registration Agent",
            role="Help users with business registration, licenses, company setup, and commercial permits.",
            knowledge=DEPARTMENTS["business"]["knowledge"],
        ),
        "tax": DepartmentAgent(
            key="tax",
            name="Tax Agent",
            role="Help users understand tax services, filing, payments, and tax-related obligations.",
            knowledge=DEPARTMENTS["tax"]["knowledge"],
        ),
        "immigration": DepartmentAgent(
            key="immigration",
            name="Immigration and Documents Agent",
            role="Help users with passports, visas, identity documents, certificates, and document services.",
            knowledge=DEPARTMENTS["immigration"]["knowledge"],
        ),
        "health": DepartmentAgent(
            key="health",
            name="Health Services Agent",
            role="Help users navigate public health services, appointments, hospital guidance, and vaccination information.",
            knowledge=DEPARTMENTS["health"]["knowledge"],
        ),
        "education": DepartmentAgent(
            key="education",
            name="Education Services Agent",
            role="Help users with school admission, university admission, exams, scholarships, and education services.",
            knowledge=DEPARTMENTS["education"]["knowledge"],
        ),
        "general": DepartmentAgent(
            key="general",
            name="General Public Services Agent",
            role="Help users clarify their request and guide them toward the right public service area.",
            knowledge=DEPARTMENTS["general"]["knowledge"],
        ),
    }


AGENTS = build_agents()


def get_agent(department_key: str) -> DepartmentAgent:
    return AGENTS.get(department_key, AGENTS["general"])


def generate_agent_response(
    user_message: str,
    route: RouteResult,
    llm: Optional[object],
    fallback_response: str,
) -> str:
    agent = get_agent(route.department_key)

    if llm is None:
        return fallback_response

    try:
        response = llm.invoke(
            [
                SystemMessage(content=agent.build_system_prompt(route)),
                HumanMessage(content=user_message),
            ]
        )

        return response.content.strip()

    except Exception:
        return fallback_response