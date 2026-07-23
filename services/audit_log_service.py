# -*- coding: utf-8 -*-
from models.audit_log import AuditLog
from repositories import audit_log_repo

def log_action(user_id: int, action: str, entity: str, entity_id: int, details: str = "") -> AuditLog:
    """Convenient wrapper to log an action performed by a user.
    Parameters
    ----------
    user_id: int
        Identifier of the user performing the action.
    action: str
        One of 'CREATE', 'UPDATE', 'DELETE', ...
    entity: str
        Name of the model/table (e.g. 'OrdreReparation').
    entity_id: int
        Primary key of the affected row.
    details: str, optional
        Free‑form description of what changed.
    """
    log = AuditLog(user_id=user_id, action=action, entity=entity,
                   entity_id=entity_id, details=details)
    return audit_log_repo.create(log)
