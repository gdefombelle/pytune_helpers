import os
from celery import Celery
from pytune_configuration.sync_config_singleton import config, SimpleConfig
from simple_logger.logger import SimpleLogger, get_logger

if config is None:
    config = SimpleConfig()

logger : SimpleLogger = get_logger("email_worker")

class CeleryInitializationError(Exception):
    """
    Exception raised when Celery client initialization fails.
    """
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


class CeleryClient:
    """
    A lightweight Celery client that directly exports task signatures
    and performs a health check at initialization.
    """

    def __init__(self):
        """
        Initialize the Celery client with configuration from .env and perform a health check.
        """
        broker_url = os.getenv("RABBIT_BROKER_URL")
        backend_url = os.getenv("RABBIT_BACKEND")
        logger.info(f"Celery Client, brocker_url: {broker_url} , backend_url: url: {backend_url} ")

        # Initialize the Celery client
        self.celery_client = Celery(
            "pytune",
            broker=broker_url,
            backend=backend_url,
        )

        # Additional configuration
        self.celery_client.conf.update(
            worker_pool=config.RABBIT_WORKER_POOL,
            task_serializer="json",
            accept_content=["json"],
            result_serializer="json",
            broker_transport_options={
                "visibility_timeout": config.RABBIT_VISIBILITY_TIMEOUT
            },
            timezone="UTC",
            enable_utc=True,
        )

        # Expose task signatures
        self.health_check = self.celery_client.signature("email_tasks.health_check")
        self.send_mail = self.celery_client.signature("email_tasks.send_mail")

        # Perform health check during initialization
        try:
            self.health_status = self.check_health()

            if self.health_status["status"] != "OK":
                raise CeleryInitializationError(
                    f"Initialization failed: {self.health_status['message']}"
                )
        except CeleryInitializationError as e:
            logger.error(f"Error during Celery initialization: {e}")
            raise

    def check_health(self):
        """
        Executes the health_check task and returns the result.
        """
        try:
            # Submit the health_check task
            result = self.health_check.delay()
            logger.info(f"Health check task submitted with ID: [{result.id}]")

            # Retrieve the result
            res = result.get(timeout=10)
            logger.info(f"Health check result: {res}")
            return res
        except Exception as e:
            error_message = {
                "status": "ERROR",
                "message": f"Health check task failed: {str(e)}",
            }
            logger.error(error_message)
            return error_message
