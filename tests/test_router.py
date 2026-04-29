from civic_ai.services.router import route_department


def test_routes_business_request():
    route = route_department("I want to register a business")
    assert route.department_key == "business"


def test_routes_tax_request():
    route = route_department("I need to pay company tax")
    assert route.department_key == "tax"


def test_routes_passport_request():
    route = route_department("I want to renew my passport")
    assert route.department_key == "immigration"


def test_routes_health_request():
    route = route_department("I need a hospital appointment")
    assert route.department_key == "health"


def test_routes_education_request():
    route = route_department("I need school admission information")
    assert route.department_key == "education"


def test_routes_unclear_request_to_general():
    route = route_department("I need help")
    assert route.department_key == "general"