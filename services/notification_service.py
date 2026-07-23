# -*- coding: utf-8 -*-
from models.notification import Notification
from repositories import notification_repo, client_repo
from datetime import datetime

def envoyer_notification(client_id: int, type_notif: str, message: str, canal: str = 'email') -> Notification:
    """
    Enregistre et "envoie" une notification au client.
    Dans un environnement reel, on ferait un appel API SMTP, Twilio, etc.
    """
    client = client_repo.get_by_id(client_id)
    if not client:
        raise ValueError("Client introuvable pour la notification.")

    # Création de la notification en attente
    n = Notification(
        client_id=client_id,
        type_notification=type_notif,
        canal=canal,
        message=message,
        statut='en_attente'
    )
    n = notification_repo.create(n)
    
    # Simulation d'envoi immédiat
    # Si on avait un système asynchrone (ex: Celery), l'envoi se ferait en background
    _simulation_envoi(n)
    
    return n

def _simulation_envoi(n: Notification):
    """Simule l'appel externe pour envoyer le SMS/Email."""
    # Ici, l'API externe (SMTP, Twilio) serait appelee
    # On marque directement comme envoye pour l'exemple
    notification_repo.mark_as_sent(n.id)
    n.statut = 'envoye'
