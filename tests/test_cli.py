from pathlib import Path

from plumeviz.cli import build_parser


def test_cli_accepts_template_sweep():
    args = build_parser().parse_args(
        [
            "sweep",
            "--input",
            "case.inp",
            "--vary",
            "vent_velocity=75,100",
        ]
    )

    assert args.input == Path("case.inp")
    assert args.vary == [
        "vent_velocity=75,100",
    ]


def test_cli_accepts_generated_sweep():
    args = build_parser().parse_args(
        [
            "sweep",
            "--vent-diameter",
            "10",
            "--magma-temperature",
            "900",
            "--vary",
            "vent_velocity=75,100",
        ]
    )

    assert args.vent_diameter == 10
    assert args.magma_temperature == 900
