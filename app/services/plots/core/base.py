from abc import ABC, abstractmethod
from app.models.image import get_image
import fastf1
import matplotlib.pyplot as plt


class BaseAnalysis(ABC):
    def __init__(self, year: int, round_number: int, session: str):
        self.session = session
        self.year = year
        self.round_number = round_number
        self.event = fastf1.get_event(self.year, self.round_number)

    def load(self):
        self.data = fastf1.get_session(self.year, self.round_number, self.session)
        self.data.load()
        self.event_info = self.get_event_info()

    def get_event_info(self):
        return {
            "grand_prix": self.data.session_info["Meeting"]["Name"],
            "location": self.data.session_info["Meeting"]["Circuit"]["ShortName"],
            "country_name": self.data.session_info["Meeting"]["Country"]["Name"],
            "country_code": self.data.session_info["Meeting"]["Country"]["Code"],
            "round_number": self.event["RoundNumber"],
            "session": self.data.session_info["Name"],
            "year": self.data.session_info["StartDate"].year,
        }

    def process(self):
        pass

    @abstractmethod
    def plot(self):
        pass

    @property
    def cache_key(self) -> str:
        country = self.event["Country"]
        return f"{self.year}_R{self.round_number}_{country}_{self.session}_{type(self).__name__.lower()}"

    def run(self):
        cached = get_image(self.cache_key)
        if cached:
            return cached["data"]

        self.load()
        self.process()
        result = self.plot()
        plt.close("all")
        return result
