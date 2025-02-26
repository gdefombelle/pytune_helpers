# PyTune Helpers - Documentation et README

## 📌 Introduction
**PyTune Helpers** est un package utilitaire conçu pour centraliser et simplifier l'envoi d'e-mails avec support de Celery pour l'envoi différé.

📌 **Fonctionnalités principales**
- Envoi immédiat d'e-mails via SMTP
- Support de l'envoi différé avec **Celery + RabbitMQ + Redis**
- Centralisation des logs avec **pytune_logger**
- Configuration dynamique via **pytune_configuration**

## 📂 Organisation du projet

```bash
pytune_helpers/
│── pytune_helpers/
│   ├── __init__.py   # Expose EmailService et CeleryClient
│   ├── email_helper.py  # Service pour gérer l'envoi d'e-mails
│   ├── celery_client.py # Client Celery pour l'envoi d'e-mails en arrière-plan
│── tests/  # Tests unitaires
│── README.md  # Documentation du projet
│── pyproject.toml  # Configuration du package avec Poetry
│── .env.example  # Exemple des variables d'environnement
```

## 🚀 Installation

PyTune Helpers est conçu pour fonctionner avec **Poetry**.

```bash
poetry add pytune_helpers
```

### 📦 Dépendances

- **pytune_configuration** : Gestion des paramètres de configuration
- **pytune_logger** : Gestion des logs
- **Celery** : Système de tâches en arrière-plan
- **aiosmtplib** : Envoi d'e-mails asynchrone

## ⚙️ Configuration

### 1️⃣ Variables d'environnement
Créer un fichier `.env` dans le projet avec les informations suivantes :

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=yourpassword
FROM_EMAIL=your_email@gmail.com

RABBIT_BROKER_URL=pyamqp://admin:MyStr0ngP@ss2024!@localhost//
RABBIT_BACKEND=redis://127.0.0.1:6379/0
```

📌 **Remarque :** Ces valeurs doivent être définies aussi dans `docker-compose.yml` en production.

## 📧 Utilisation

### 1️⃣ Envoi immédiat d'un e-mail
```python
from pytune_helpers import EmailService

email_service = EmailService()
email_service.send_email(
    to_email="user@example.com",
    subject="Bienvenue sur PyTune!",
    body="<h1>Bienvenue!</h1><p>Merci de nous rejoindre.</p>",
    is_html=True,
    send_background=False  # Envoi immédiat
)
```

### 2️⃣ Envoi différé avec Celery
```python
email_service.send_email(
    to_email="user@example.com",
    subject="Email en arrière-plan",
    body="Cet email est envoyé via Celery",
    is_html=True,
    send_background=True  # Envoi en différé avec Celery
)
```

## 🛠️ Structure des classes

### **1️⃣ CeleryClient** - Gestion des tâches Celery
```python
class CeleryClient:
    def __init__(self):
        self.celery_client = Celery(
            "pytune",
            broker=config.RABBIT_BROKER_URL,
            backend=config.RABBIT_BACKEND,
        )
```
📌 **Utilisation:**
```python
celery_client = CeleryClient()
celery_client.send_mail.delay("user@example.com", "Sujet", "Contenu HTML", True)
```

### **2️⃣ EmailService** - Gestion de l'envoi d'e-mails
```python
class EmailService:
    async def send_email(self, to_email, subject, body, is_html=False, send_background=False):
        if send_background:
            self.celery_client.send_mail.delay(to_email, subject, body, is_html)
        else:
            await self._send_email_task(to_email, subject, body, is_html)
```

## 🐳 Dockerisation

En production, ce module est utilisé dans un **worker Celery** tournant dans Docker.

📌 **Exemple docker-compose.yml** pour déployer un worker Celery qui envoie des e-mails :
```yaml
services:
  email_worker:
    image: pytune_email_worker:latest
    restart: always
    environment:
      - RABBIT_BROKER_URL=${RABBIT_BROKER_URL}
      - REDIS_BACKEND=${REDIS_BACKEND}
      - SMTP_SERVER=${SMTP_SERVER}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - FROM_EMAIL=${FROM_EMAIL}
    depends_on:
      - rabbitmq
      - redis
```

## ✅ Conclusion

Avec **pytune_helpers**, l'envoi d'e-mails devient simple et efficace, avec un support de l'envoi différé grâce à Celery et RabbitMQ. 🚀

🔥 **Prochaines étapes :** Ajouter des tests unitaires et améliorer les logs d'e-mails envoyés. 📊

