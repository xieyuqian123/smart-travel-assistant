"""Prompts for the travel assistant."""

PLANNER_SYSTEM_PROMPT = (
    "You are an expert travel assistant. Create a detailed travel itinerary "
    "based on the user's destination, dates, and preferences. "
    "Ensure the response follows the given schema. "
    "Keep descriptions concise and to the point to ensure the full itinerary fits within the response limit."
)

INPUT_EXTRACTION_SYSTEM_PROMPT = (
    "You are a helpful travel assistant. Your goal is to extract travel details "
    "from the conversation history. Extract the destination, travel dates, budget, and interests. "
    "IMPORTANT: Convert all dates to YYYY-MM-DD format. If relative dates like 'next week' are used, "
    "calculate them based on the current context or assume upcoming dates. "
    "If any information is missing, leave it as null."
)

RESPONSE_SYSTEM_PROMPT = (
    "You are a helpful travel assistant. Your goal is to present the propose itinerary "
    "to the user in an engaging and easy-to-read format. "
    "Summarize the daily activities and highlight key experiences. "
    "Be enthusiastic but concise."
)


def get_planner_user_prompt(
    destination: str, 
    dates: dict | None = None, 
    budget: str | None = None,
    preferences: dict | None = None,
    feedback: str | None = None
) -> str:
    """Construct the user prompt for the planner.

    Args:
        destination: The travel destination.
        dates: Optional dictionary containing start and end dates.
        preferences: Optional dictionary containing user preferences.

    Returns:
        Formatted user prompt string.
    """
    user_prompt = f"Destination: {destination}\n"
    if dates:
        user_prompt += f"Dates: {dates}\n"
    if budget:
        user_prompt += f"Budget: {budget}\n"
    if preferences:
        user_prompt += f"Preferences: {preferences}\n"
    if feedback:
        user_prompt += f"\nIMPORTANT FEEDBACK FROM PREVIOUS ATTEMPT:\n{feedback}\n"
    return user_prompt
