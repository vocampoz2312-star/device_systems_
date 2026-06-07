from typing import List, Dict, Any

# ──────────────────────────────────────────────
# Simulación de base de datos en memoria
# ──────────────────────────────────────────────

_users: List[Dict[str, Any]] = [
    {"id": 1, "name": "Ana Martínez",  "email": "ana.martinez@devicesystems.com",  "role": "admin",   "is_active": True},
    {"id": 2, "name": "Carlos Ruiz",   "email": "carlos.ruiz@devicesystems.com",   "role": "support", "is_active": True},
    {"id": 3, "name": "Laura Gómez",   "email": "laura.gomez@devicesystems.com",   "role": "user",    "is_active": False},
    {"id": 4, "name": "Pedro Sánchez", "email": "pedro.sanchez@devicesystems.com", "role": "user",    "is_active": True},
]

_counter: int = len(_users)


def get_all() -> List[Dict[str, Any]]:
    return _users


def get_by_id(user_id: int) -> Dict[str, Any] | None:
    return next((u for u in _users if u["id"] == user_id), None)


def email_exists(email: str, exclude_id: int | None = None) -> bool:
    return any(
        u["email"].lower() == email.lower()
        for u in _users
        if u["id"] != exclude_id
    )


def insert(user: Dict[str, Any]) -> Dict[str, Any]:
    global _counter
    _counter += 1
    user["id"] = _counter
    _users.append(user)
    return user


def update(user_id: int, data: Dict[str, Any]) -> Dict[str, Any] | None:
    user = get_by_id(user_id)
    if user is None:
        return None
    user.update(data)
    return user


def delete(user_id: int) -> bool:
    user = get_by_id(user_id)
    if user is None:
        return False
    _users.remove(user)
    return True