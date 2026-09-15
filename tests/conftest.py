from pathlib import Path

import pytest


@pytest.fixture
def plumeria_template(tmp_path: Path) -> Path:
    path = tmp_path / "template.inp"

    path.write_text(
        """# input file
# output file name
old_output.txt
#
# atmospheric input
no
input/metdata/garbage.txt
#
15.0                  #Air temperature at vent, Celsius.
0.0                   #Air relative humidity
-0.0065               #thermal lapse rate in troposphere
11000.0               #Elevation of tropopause
9000.0                #Tropopause thickness
0.001                 #thermal lapse rate above tropopause
10.0   0.002   90.0   #wind speed, m/s, [optional wind slope, m/s per m], wind dir (deg. E of N)
#
0.0                   #Vent elevation (m asl)
50.0                  #vent diameter (m)
200.0                 #exit velocity (m/s)
0.1    15.0           #mass fraction added water, (optional) water temperature C
#
900.0                 #magma temperature
0.03                  #mass fraction gas in magma
1000.0                #magma specific heat, J/kg K
2500.0                #magma density (DRE), kg/m3
#
0.1 0.2 0.3
""",
        encoding="utf-8",
    )

    return path
