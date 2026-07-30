from fastapi import APIRouter, Depends, Response
from app.schemas.session import SessionParameters, RaceSessionParameters
from app.schemas.options import GroupOptions, DisplayOptions, BasisOptions
from app.services.analyze import (
    run_sector_analysis,
    run_strategy,
    run_overtakes,
    run_race_pace,
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
