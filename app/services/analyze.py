from app.services.plots.analyzers.overtakes import Overtakes


def run_overtakes(year: int, round_number: int, session: str):
    overtakes = Overtakes(year=year, round_number=round_number, session=session)
    return overtakes.run()
