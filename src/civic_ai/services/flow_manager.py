from dataclasses import dataclass, field
from typing import Dict, List, Optional

from civic_ai.domain.schemas import RouteResult
from civic_ai.services.router import route_department


@dataclass
class ConversationFlowState:
    """
    Conversation flow state inspired by Team 2's public-service conversation-flow research.

    The flow follows this pattern:
    1. Open user input
    2. Department classification
    3. Classification confirmation
    4. Slot filling
    5. Final response
    6. Fallback / handoff if unclear
    """

    stage: str = "open"
    original_message: Optional[str] = None

    department_key: Optional[str] = None
    department_name: Optional[str] = None
    confidence: float = 0.0
    matched_keywords: List[str] = field(default_factory=list)

    secondary_department_key: Optional[str] = None
    secondary_department_name: Optional[str] = None

    confirmed_department: bool = False
    collected_slots: Dict[str, str] = field(default_factory=dict)
    fallback_count: int = 0


def create_initial_flow_state() -> ConversationFlowState:
    return ConversationFlowState()


def handle_flow_turn(user_message: str, state: ConversationFlowState) -> Dict:
    """
    Handles one user turn using a lightweight Team 2-style conversation flow.

    Returns:
        {
            "should_answer": bool,
            "message": Optional[str],
            "answer_input": Optional[str],
            "state": ConversationFlowState
        }

    If should_answer is False:
        The UI should display "message" directly.

    If should_answer is True:
        The UI should send "answer_input" to the response generator.
    """

    user_message = user_message.strip()
    normalized = user_message.lower()

    if not user_message:
        return {
            "should_answer": False,
            "message": "Please type or say your question first.",
            "answer_input": None,
            "state": state,
        }

    # -----------------------------------------------------
    # Stage 1: Open input
    # -----------------------------------------------------
    if state.stage == "open":
        route = route_department(user_message)

        # Store the first user request because we will use it later
        # after confirmation and slot filling.
        state.original_message = user_message
        _update_state_from_route(state, route)

        if route.confidence >= 0.45:
            state.stage = "confirm_department"

            return {
                "should_answer": False,
                "message": (
                    f"I understood that your request is related to "
                    f"**{_friendly_department_name(route.department_key)}**. "
                    f"Is that correct?"
                ),
                "answer_input": None,
                "state": state,
            }

        state.stage = "fallback"
        state.fallback_count += 1

        return {
            "should_answer": False,
            "message": _fallback_message(state),
            "answer_input": None,
            "state": state,
        }

    # -----------------------------------------------------
    # Stage 2: Confirm detected department
    # -----------------------------------------------------
    if state.stage == "confirm_department":
        if _is_yes(normalized):
            state.confirmed_department = True
            state.stage = "collect_service_type"

            return {
                "should_answer": False,
                "message": _slot_question_for_department(state.department_key),
                "answer_input": None,
                "state": state,
            }

        if _is_no(normalized):
            state.stage = "fallback"
            state.fallback_count += 1

            return {
                "should_answer": False,
                "message": (
                    "No problem. Could you describe the service you need "
                    "in another way?"
                ),
                "answer_input": None,
                "state": state,
            }

        # If the user replies with another full request instead of yes/no,
        # route that new message again.
        if len(normalized.split()) >= 4:
            route = route_department(user_message)
            state.original_message = user_message
            _update_state_from_route(state, route)

            if route.confidence >= 0.45:
                return {
                    "should_answer": False,
                    "message": (
                        f"I understood that your request is related to "
                        f"**{_friendly_department_name(route.department_key)}**. "
                        f"Is that correct?"
                    ),
                    "answer_input": None,
                    "state": state,
                }

        return {
            "should_answer": False,
            "message": "Please answer with **yes** or **no** so I can guide you correctly.",
            "answer_input": None,
            "state": state,
        }

    # -----------------------------------------------------
    # Stage 3: Slot filling
    # -----------------------------------------------------
    if state.stage == "collect_service_type":
        state.collected_slots["service_type"] = user_message

        answer_input = _build_answer_input(state)

        # Reset after collecting enough information.
        new_state = create_initial_flow_state()

        return {
            "should_answer": True,
            "message": None,
            "answer_input": answer_input,
            "state": new_state,
        }

    # -----------------------------------------------------
    # Stage 4: Fallback handling
    # -----------------------------------------------------
    if state.stage == "fallback":
        menu_route = _route_from_menu_choice(normalized)

        if menu_route is not None:
            _update_state_from_route(state, menu_route)
            state.original_message = f"The user selected {_friendly_department_name(menu_route.department_key)}."
            state.stage = "collect_service_type"

            return {
                "should_answer": False,
                "message": _slot_question_for_department(state.department_key),
                "answer_input": None,
                "state": state,
            }

        route = route_department(user_message)

        if route.confidence >= 0.45:
            state.original_message = user_message
            _update_state_from_route(state, route)
            state.stage = "confirm_department"

            return {
                "should_answer": False,
                "message": (
                    f"I understood that your request is related to "
                    f"**{_friendly_department_name(route.department_key)}**. "
                    f"Is that correct?"
                ),
                "answer_input": None,
                "state": state,
            }

        state.fallback_count += 1

        return {
            "should_answer": False,
            "message": _fallback_message(state),
            "answer_input": None,
            "state": state,
        }

    # Safe default
    return {
        "should_answer": True,
        "message": None,
        "answer_input": user_message,
        "state": create_initial_flow_state(),
    }


def _update_state_from_route(state: ConversationFlowState, route: RouteResult) -> None:
    state.department_key = route.department_key
    state.department_name = route.department_name
    state.confidence = route.confidence
    state.matched_keywords = route.matched_keywords
    state.secondary_department_key = route.secondary_department_key
    state.secondary_department_name = route.secondary_department_name


def _build_answer_input(state: ConversationFlowState) -> str:
    original_message = state.original_message or ""
    service_type = state.collected_slots.get("service_type", "")

    return (
        f"User request: {original_message}\n"
        f"Confirmed public service area: {_friendly_department_name(state.department_key)}\n"
        f"Additional user detail: {service_type}\n"
        "Please provide helpful public-service guidance based on this context."
    )


def _friendly_department_name(department_key: Optional[str]) -> str:
    names = {
        "business": "business registration or licenses",
        "tax": "tax services",
        "immigration": "passport, immigration, or official documents",
        "health": "health services",
        "education": "education services",
        "general": "general public services",
    }

    return names.get(department_key or "general", "general public services")


def _slot_question_for_department(department_key: Optional[str]) -> str:
    if department_key == "business":
        return (
            "Is this about a **new business registration**, **license renewal**, "
            "**required documents**, or **tax-related next steps**?"
        )

    if department_key == "tax":
        return (
            "Is this about **paying tax**, **filing a return**, "
            "**understanding obligations**, or **checking required documents**?"
        )

    if department_key == "immigration":
        return (
            "Is this for a **new application**, **renewal**, **replacement**, "
            "or **status tracking**?"
        )

    if department_key == "health":
        return (
            "Is this about an **appointment**, **hospital information**, "
            "**vaccination**, or another health service?"
        )

    if department_key == "education":
        return (
            "Is this about **school enrollment**, **university admission**, "
            "**exams**, **scholarships**, or another education service?"
        )

    return (
        "Could you tell me what type of service you need: **application**, "
        "**renewal**, **documents**, **payment**, **status tracking**, or "
        "**general information**?"
    )


def _fallback_message(state: ConversationFlowState) -> str:
    if state.fallback_count == 1:
        return (
            "I’m not fully sure which public service you need. "
            "Could you describe your request in another way?"
        )

    if state.fallback_count == 2:
        return (
            "Please choose the closest option:\n\n"
            "1. Business registration or license\n"
            "2. Tax service\n"
            "3. Passport, immigration, or documents\n"
            "4. Health service\n"
            "5. Education service\n"
            "6. Other public service"
        )

    return (
        "I’m still not fully sure which service this belongs to. "
        "This may need human support or confirmation from the relevant public office."
    )


def _route_from_menu_choice(text: str) -> Optional[RouteResult]:
    mapping = {
        "1": "business",
        "business": "business",
        "business registration": "business",
        "license": "business",
        "licence": "business",

        "2": "tax",
        "tax": "tax",

        "3": "immigration",
        "passport": "immigration",
        "documents": "immigration",
        "document": "immigration",
        "immigration": "immigration",

        "4": "health",
        "health": "health",
        "hospital": "health",

        "5": "education",
        "education": "education",
        "school": "education",

        "6": "general",
        "other": "general",
        "general": "general",
    }

    department_key = mapping.get(text)

    if department_key is None:
        return None

    # Route a synthetic message so we reuse the existing router logic.
    return route_department(department_key)


def _is_yes(text: str) -> bool:
    return text in [
        "yes",
        "yeah",
        "yep",
        "correct",
        "right",
        "true",
        "sure",
        "ok",
        "okay",
        "exactly",
    ]


def _is_no(text: str) -> bool:
    return text in [
        "no",
        "nope",
        "wrong",
        "not correct",
        "incorrect",
        "not really",
    ]