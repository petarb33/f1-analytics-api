from abc import ABC
import fastf1


class BaseAnalysis(ABC):
    def __init__(self, year: int, round_number: int, session: str):
        self.session = session
        self.year = year
        self.round_number = round_number

    def load(self):
        self.data = fastf1.get_session(self.year, self.round_number, self.session)
        self.data.load()

    def process(self):
        pass

    def plot(self):
        pass

    def run(self):
        self.load()
        self.process()
        self.plot()
