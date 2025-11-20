class UserPreferences:
    def __init__(self):
        self.preferences = {}

    def update_preference(self, user_id: int, feedback: str) -> None:
        if user_id not in self.preferences:
            self.preferences[user_id] = {"likes": 0, "dislikes": 0}
        if feedback == "like":
            self.preferences[user_id]["likes"] += 1
        elif feedback == "dislike":
            self.preferences[user_id]["dislikes"] += 1

    def get_preferences(self, user_id: int) -> dict:
        return self.preferences.get(user_id, {"likes": 0, "dislikes": 0})