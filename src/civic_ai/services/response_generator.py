from civic_ai.domain.schemas import RouteResult
from civic_ai.infrastructure.mistral_client import get_mistral_client
from civic_ai.services.agents import generate_agent_response


def fallback_response(route: RouteResult) -> str:
    if route.department_key == "business":
        return (
            "For business registration, you may usually need details such as the business name, "
            "type of activity, applicant information, and supporting documents. "
            "The exact requirements can vary depending on the type of business, so it is best to confirm them through the official portal or relevant office. "
            "Are you trying to register a new business, renew a license, or check required documents?"
        )

    if route.department_key == "tax":
        return (
            "For tax-related services, the process depends on whether you are asking about personal tax, "
            "business tax, payment, or filing. Exact rates, deadlines, and official requirements should be checked with the relevant tax authority. "
            "Are you trying to pay tax, file a return, or understand your obligations?"
        )

    if route.department_key == "immigration":
        return (
            "For passport or official document services, you may usually need an application form, "
            "identity proof, and supporting documents. The exact process depends on whether this is a new application, renewal, or replacement. "
            "Please confirm final requirements with the official office or portal."
        )

    if route.department_key == "health":
        return (
            "For health services, I can help with general guidance such as appointments, hospital information, or vaccination support. "
            "For urgent or medical cases, it is better to contact a healthcare professional or emergency service directly. "
            "What type of health service are you looking for?"
        )

    if route.department_key == "education":
        return (
            "For education services, I can help with general information about schools, admissions, programs, exams, or scholarships. "
            "Specific deadlines, rules, and required documents should be confirmed with the relevant education authority or institution. "
            "Are you asking about enrollment, admission, scholarships, or exams?"
        )

    return (
        "I can help you with general public service information. "
        "Please tell me what you want to do, for example applying for a document, registering a business, paying tax, or checking required documents."
    )


def generate_response(user_message: str, route: RouteResult) -> str:
    llm = get_mistral_client()
    safe_fallback = fallback_response(route)

    return generate_agent_response(
        user_message=user_message,
        route=route,
        llm=llm,
        fallback_response=safe_fallback,
    )