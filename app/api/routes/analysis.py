from fastapi import APIRouter, Depends, Response, Query, HTTPException
from typing import Annotated
from app.schemas.session import (
    SessionParameters,
    RaceSessionParameters,
    QualifyingSessionParameters,
)
from app.schemas.options import (
    GroupOptions,
    DisplayOptions,
    BasisOptions,
    LapModeOptions,
)
from app.services.analyze import (
    run_sector_analysis,
    run_strategy,
    run_overtakes,
    run_race_pace,
    run_gap_to_pole,
    run_lap_by_lap_pace,
    run_laptime_heatmap,
)

router = APIRouter()


@router.get("/overtakes")
def get_overtakes_graph(params: RaceSessionParameters = Depends()):
    image_bytes = run_overtakes(params.year, params.round_number, params.session)
    return Response(content=image_bytes, media_type="image/png")


@router.get("/sectors")
def get_sectors_graph(
    params: SessionParameters = Depends(),
    group_options: GroupOptions = Depends(),
    display_options: DisplayOptions = Depends(),
    basis_options: BasisOptions = Depends(),
):
    image_bytes = run_sector_analysis(
        params.year,
        params.round_number,
        params.session,
        group_options.group,
        display_options.display,
        basis_options.basis,
    )
    return Response(content=image_bytes, media_type="image/png")


@router.get("/racepace")
def get_race_pace_graph(
    params: RaceSessionParameters = Depends(), group_options: GroupOptions = Depends()
):
    image_bytes = run_race_pace(
        params.year, params.round_number, params.session, group_options.group
    )
    return Response(content=image_bytes, media_type="image/png")


@router.get("/strategy")
def get_strategy_graph(params: RaceSessionParameters = Depends()):
    image_bytes = run_strategy(params.year, params.round_number, params.session)
    return Response(content=image_bytes, media_type="image/png")


@router.get("/paceByLaps")
def get_pace_by_laps_graph(params: RaceSessionParameters = Depends()):
    image_bytes = run_lap_by_lap_pace(params.year, params.round_number, params.session)
    return Response(content=image_bytes, media_type="image/png")


@router.get("/qualiGap")
def get_quali_gap_graph(params: QualifyingSessionParameters = Depends()):
    image_bytes = run_gap_to_pole(
        year=params.year, round_number=params.round_number, session=params.session
    )
    return Response(content=image_bytes, media_type="image/png")


@router.get("/heatmap")
def get_laptime_heatmap_graph(
    params: RaceSessionParameters = Depends(),
    drivers: Annotated[list[str] | None, Query()] = None,
    mode_options: LapModeOptions = Depends(),
):
    try:
        image_bytes = run_laptime_heatmap(
            params.year, params.round_number, params.session, drivers, mode_options.mode
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return Response(content=image_bytes, media_type="image/png")
