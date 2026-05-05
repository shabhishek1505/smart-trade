
from worker.kafka.consumer.plan_processing_consumer import start_strategy_plan_consumer
from worker.kafka.consumer.signal_processing_consumer import start_signal_consumer

if __name__ == "__main__":
    start_strategy_plan_consumer();
    start_signal_consumer()
