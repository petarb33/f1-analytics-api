from fastf1.core import Session
import fastf1.plotting


def get_drivers_colors(session: Session) -> dict[str, str]:
    return fastf1.plotting.get_driver_color_mapping(session)


def get_compound_colors(session: Session) -> dict[str, str]:
    return fastf1.plotting.get_compound_mapping(session)


def get_teams_colors(session: Session) -> dict[str, str]:
    team_colors = {}
    teams = []

    for team in session.results["TeamName"]:
        if team not in teams:
            teams.append(team)

    for team in teams:
        team_colors[team] = fastf1.plotting.get_team_color(team, session)

    return team_colors


def get_drivers_style(
    session: Session, drivers: list[str]
) -> dict[str, dict[str, str]]:
    drivers_styles = {}
    for driver in drivers:
        drivers_styles[driver] = fastf1.plotting.get_driver_style(
            identifier=driver, session=session, style=["color", "linestyle"]
        )

    return drivers_styles
