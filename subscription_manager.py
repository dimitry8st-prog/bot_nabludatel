class SubscriptionManager:
    def __init__(self):
        self.subscribers = set()

    def subscribe(self, user_id: int) -> None:
        self.subscribers.add(user_id)

    def unsubscribe(self, user_id: int) -> None:
        self.subscribers.discard(user_id)

    def is_subscribed(self, user_id: int) -> bool:
        return user_id in self.subscribers

    def get_subscribers(self) -> set:
        return self.subscribers