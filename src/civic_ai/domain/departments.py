DEPARTMENTS = {
    "business": {
        "name": "Business Registration Agent",
        "keywords": [
            "business", "company", "register", "registration", "license",
            "licence", "trade", "startup", "enterprise", "permit", "commercial"
        ],
        "knowledge": [
            "Business registration usually requires applicant details, business name, business type, and supporting documents.",
            "The user may need to clarify whether they are applying for a new registration, a renewal, or a document checklist.",
            "Business registration questions may later connect to tax obligations.",
            "Exact fees, deadlines, and legal requirements must be verified through official sources."
        ],
    },

    "tax": {
        "name": "Tax Agent",
        "keywords": [
            "tax", "revenue", "income", "payment", "pay", "vat", "gst",
            "return", "filing", "tin", "taxpayer", "salary"
        ],
        "knowledge": [
            "Tax questions depend on the user profile, income, business type, and official tax rules.",
            "The user may need to clarify whether the question is about personal tax, business tax, payment, or filing.",
            "Business registration and tax obligations may be connected.",
            "The assistant should not invent tax rates, exact deadlines, or official penalties."
        ],
    },

    "immigration": {
        "name": "Immigration & Documents Agent",
        "keywords": [
            "passport", "visa", "immigration", "citizenship", "document",
            "certificate", "id", "identity", "travel", "permit"
        ],
        "knowledge": [
            "Passport and document services usually require identity verification and supporting documents.",
            "The user may need to clarify whether they need a new document, renewal, replacement, or status tracking.",
            "The assistant should not ask for sensitive personal information in chat.",
            "Exact official requirements should be verified through the relevant office or portal."
        ],
    },

    "health": {
        "name": "Health Services Agent",
        "keywords": [
            "health", "hospital", "clinic", "doctor", "medical", "medicine",
            "appointment", "vaccine", "vaccination", "emergency"
        ],
        "knowledge": [
            "Health service questions should be handled safely and generally.",
            "The assistant can guide users toward appointments, hospital information, or vaccination guidance.",
            "The assistant should not provide diagnosis or replace professional medical advice.",
            "For urgent cases, the user should contact emergency services or a healthcare professional."
        ],
    },

    "education": {
        "name": "Education Services Agent",
        "keywords": [
            "education", "school", "student", "university", "college", "teacher",
            "enrollment", "admission", "exam", "scholarship", "course", "program"
        ],
        "knowledge": [
            "Education service questions may involve school enrollment, university admission, exams, scholarships, or programs.",
            "The assistant should clarify the level of education and the type of service needed.",
            "Specific enrollment rules, deadlines, and required documents must be checked through the relevant education authority.",
            "The assistant can help users understand what information they may need before contacting the service."
        ],
    },

    "general": {
        "name": "General Public Services Agent",
        "keywords": [
            "help", "service", "government", "portal", "application",
            "form", "support", "information", "department"
        ],
        "knowledge": [
            "The General Agent helps classify unclear public service requests.",
            "If the request is unclear, the assistant should ask a short clarification question.",
            "The assistant should not pretend to access real government databases.",
            "The assistant should clearly explain when official confirmation is needed."
        ],
    },
}