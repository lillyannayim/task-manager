from utils.errors import NotFoundError, ValidationError

VALID_NOTIFICATION_PREFS = ("email", "sms", "none")

USERS: dict[int, dict] = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "notification_pref": "none"},
    2: {"id": 2, "name": "Bob",   "email": "bob@example.com",   "notification_pref": "none"},
}

def get_user(user_id: int) -> dict:
    """Retrieve a user by ID.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        The user record as a dictionary.

    Raises:
        NotFoundError: If no user exists with the given ID.
    """
    if user_id not in USERS:
        raise NotFoundError("User")
    return USERS[user_id]

def create_user(name: str, email: str) -> dict:
    """Create a new user.

    Args:
        name: The user's display name.
        email: The user's email address.

    Returns:
        The newly created user record.

    Raises:
        ValidationError: If name or email is empty.
    """
    if not name or not name.strip():
        raise ValidationError("name", "cannot be empty")
    if not email or "@" not in email:
        raise ValidationError("email", "must be a valid email address")
    new_id = max(USERS.keys()) + 1
    USERS[new_id] = {
        "id": new_id,
        "name": name,
        "email": email,
        "notification_pref": "none",
    }
    return USERS[new_id]

def get_notification_pref(user_id: int) -> str:
    """Retrieve a user's notification preference.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        The user's notification preference string.

    Raises:
        NotFoundError: If no user exists with the given ID.
    """
    if user_id not in USERS:
        raise NotFoundError("User")
    return USERS[user_id]["notification_pref"]

def update_notification_pref(user_id: int, pref: str) -> str:
    """Update a user's notification preference.

    Args:
        user_id: The unique identifier for the user.
        pref: The new notification preference. Must be one of
            VALID_NOTIFICATION_PREFS.

    Returns:
        The updated notification preference string.

    Raises:
        NotFoundError: If no user exists with the given ID.
        ValidationError: If pref is not in VALID_NOTIFICATION_PREFS.
    """
    if user_id not in USERS:
        raise NotFoundError("User")
    if pref not in VALID_NOTIFICATION_PREFS:
        raise ValidationError(
            "notification_pref",
            f"must be one of {', '.join(VALID_NOTIFICATION_PREFS)}",
        )
    USERS[user_id]["notification_pref"] = pref
    return pref
