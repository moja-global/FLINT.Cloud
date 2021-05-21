import os
from enum import Enum
from argparse import ArgumentParser
from glob import glob
from osgeo import gdal
from contextlib import contextmanager


class SimulationSize(Enum):
    Small = 1
    Medium = 2
    Large = 3


@contextmanager
def open_raster(path):
    ds = None
    band = None
    try:
        ds = gdal.Open(path)
        band = ds.GetRasterBand(1)
        yield band
    finally:
        band = None
        ds = None


def estimate_simulation_size(input_data_dir):
    age_layer_path = glob(os.path.join(input_data_dir, "initial_age*.tiff"))
    if not age_layer_path:
        raise RuntimeError(f"Initial age layer not found in {input_data_dir}")

    age_layer_path = age_layer_path[0]
    with open_raster(age_layer_path) as layer:
        pixel_count = sum(layer.GetHistogram(approx_ok=0))
        return SimulationSize.Small if pixel_count < 1e5 \
            else SimulationSize.Medium if pixel_count < 1e6 \
            else SimulationSize.Large


if __name__ == "__main__":
    parser = ArgumentParser("Estimate GCBM simulation size.")
    parser.add_argument(
        "input_data_dir", help="Path to simulation's tiled layers", type=os.path.abspath)
    args = parser.parse_args()

    simulation_size = estimate_simulation_size(args.input_data_dir)
    print(simulation_size)
