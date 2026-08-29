"""Export the BU-22 Display Controller Rev B fabrication files for JLCPCB."""

from pathlib import Path
import sys

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = (
    ROOT / "display-controller-rev-b" /
    "BU-22-Display-Controller-Rev-B.kicad_pcb"
)
OUTPUT_DIR = (
    ROOT / "display-controller-rev-b" / "fabrication" /
    "jlcpcb-rev-b-2026-08-16"
)


LAYERS = (
    (pcbnew.F_Cu, "F_Cu", "Front copper"),
    (pcbnew.In1_Cu, "In1_Cu", "Ground plane"),
    (pcbnew.In2_Cu, "In2_Cu", "5 V plane"),
    (pcbnew.B_Cu, "B_Cu", "Back copper"),
    (pcbnew.F_Mask, "F_Mask", "Front solder mask"),
    (pcbnew.B_Mask, "B_Mask", "Back solder mask"),
    (pcbnew.F_SilkS, "F_Silkscreen", "Front silkscreen"),
    (pcbnew.B_SilkS, "B_Silkscreen", "Back silkscreen"),
    (pcbnew.Edge_Cuts, "Edge_Cuts", "Board outline"),
)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    board.BuildConnectivity()

    plotter = pcbnew.PLOT_CONTROLLER(board)
    options = plotter.GetPlotOptions()
    options.SetOutputDirectory(str(OUTPUT_DIR) + "/")
    options.SetPlotFrameRef(False)
    options.SetPlotValue(False)
    options.SetPlotReference(False)
    options.SetSubtractMaskFromSilk(True)
    options.SetUseGerberProtelExtensions(True)
    options.SetCreateGerberJobFile(True)
    options.SetUseGerberX2format(True)
    options.SetGerberPrecision(6)

    generated = []
    for layer, suffix, description in LAYERS:
        plotter.SetLayer(layer)
        if not plotter.OpenPlotfile(suffix, pcbnew.PLOT_FORMAT_GERBER,
                                    description):
            raise RuntimeError(f"Unable to open Gerber output for {suffix}")
        if not plotter.PlotLayer():
            raise RuntimeError(f"Unable to plot Gerber layer {suffix}")
        generated.append(plotter.GetPlotFileName())
    plotter.ClosePlot()

    missing = [path for path in generated if not Path(path).is_file()]
    if missing:
        raise RuntimeError("Missing generated files: " + ", ".join(missing))

    for path in generated:
        output = Path(path)
        print(f"{output.name}: {output.stat().st_size} bytes")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
