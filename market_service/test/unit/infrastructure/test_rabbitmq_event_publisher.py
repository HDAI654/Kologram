from src.infrastructure.messaging.rabbitmq_event_publisher import RabbitMQEventPublisher


def test_rabbitmq_publisher_constructs() -> None:
    pub = RabbitMQEventPublisher(
        url="amqp://guest:guest@localhost:5672/",
        exchange_name="listing.events",
    )
    assert pub is not None
