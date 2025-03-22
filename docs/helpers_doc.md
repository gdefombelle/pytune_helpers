# 📌 PyTune Helpers

## 📝 Introduction
`pytune_helpers` est un module utilitaire conçu pour centraliser et faciliter l'envoi des emails dans PyTune. Il permet d'envoyer des emails immédiatement ou en tâche de fond via Celery, RabbitMQ et Redis.

Ce module est **dépendant de `pytune_configuration`** pour récupérer les paramètres SMTP et de `simple_logger` pour la journalisation.

---

## ⚙️ Installation

### 1️⃣ Prérequis
Assurez-vous que vous avez installé `pytune_helpers` avec ses dépendances.

```sh
pip install pytune_helpers
```

Ou si vous utilisez Poetry :

```sh
poetry add pytune_helpers
```

### 2️⃣ Dépendances
`pytune_helpers` dépend de **deux autres packages PyTune** :
- [`pytune_configuration`](https://github.com/gdefombelle/pytune_configuration) (récupération des paramètres SMTP, RabbitMQ, Redis)
- [`simple_logger`](https://github.com/gdefombelle/simple_logger) (journalisation des événements)

Assurez-vous qu'ils sont bien installés.

---

## 🛠️ Fonctionnalités principales

### ✉️ Envoi d'email immédiat

```python
from pytune_helpers import EmailService

email_service = EmailService()
await email_service.send_email(
    to_email="user@example.com",
    subject="Bienvenue sur PyTune",
    body="Merci de vous être inscrit !",
    is_html=True
)
```

### ⏳ Envoi d'email en arrière-plan (via Celery)

```python
await email_service.send_email(
    to_email="user@example.com",
    subject="Confirmation",
    body="Votre demande a été reçue !",
    is_html=True,
    send_background=True
)
```

---

## 📦 Structure du module

```
pytune_helpers/
│── __init__.py   # Importe EmailService et CeleryClient
│── email_helper.py   # Service principal pour l'envoi d'emails
│── celery_client.py   # Gestionnaire Celery pour les tâches en arrière-plan
```

- `email_helper.py` : Gère la construction et l'envoi des emails.
- `celery_client.py` : Initialise Celery pour permettre l'envoi différé d'emails.

---

## ⚙️ Configuration

### 📜 Gestion des paramètres (via `pytune_configuration`)

Ce module ne contient **aucune configuration locale**. Tous les paramètres (SMTP, RabbitMQ, Redis) sont **stockés en base de données** et lus via `pytune_configuration`.

Si vous utilisez une configuration locale sans base de données, ajoutez ces valeurs dans le `.env` de `pytune_configuration` :

```ini
# Exemple de configuration pour pytune_configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=yourpassword
FROM_EMAIL=your_email@gmail.com

RABBIT_BROKER_URL=pyamqp://admin:MyStr0ngP@ss2024!@localhost//
RABBIT_BACKEND=redis://127.0.0.1:6379/0
```

📌 **En production, ces valeurs doivent être stockées en base et non dans un fichier `.env` !**

---

## 🚀 Déploiement

Pour utiliser `pytune_helpers` dans un environnement Docker, assurez-vous que :
- `pytune_configuration` est bien déployé avec accès à la base de données
- Un service **RabbitMQ** et **Redis** sont en place pour Celery

Exemple d'utilisation dans un `docker-compose.yml` :

```yaml
services:
  email_worker:
    image: pytune-email-worker:latest
    depends_on:
      - rabbitmq
      - redis
    environment:
      - RABBIT_BROKER_URL=pyamqp://admin:MyStr0ngP@ss2024!@rabbitmq//
      - RABBIT_BACKEND=redis://redis:6379/0
```

---

## 🛠 Débogage & Logs

Toutes les actions du module sont journalisées avec `simple_logger`.

📌 Les logs seront visibles dans **OpenSearch** si configuré.

En cas d’erreur, consultez les logs avec :

```python
from simple_logger import get_logger
logger = get_logger("pytune", "email_service")
await logger.ainfo("Test de log")
```

---

## 📌 Conclusion

`pytune_helpers` permet une gestion efficace des emails et leur envoi en arrière-plan via Celery.
Il s'intègre parfaitement avec `pytune_configuration` et `simple_logger` pour centraliser la gestion des paramètres et la journalisation.

🚀 **Prochaine étape** : Déploiement du worker Celery sur le serveur ! 🎯

