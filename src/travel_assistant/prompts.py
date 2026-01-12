"""Prompts for the travel assistant."""

PLANNER_SYSTEM_PROMPT = (
    "You are an expert travel assistant. Create a detailed travel itinerary "
    "based on the user's destination, dates, and preferences. "
    "Ensure the response follows the given schema."
)


def get_planner_user_prompt(
    destination: str, dates: dict | None = None, preferences: dict | None = None
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
    if preferences:
        user_prompt += f"Preferences: {preferences}\n"
    return user_prompt
