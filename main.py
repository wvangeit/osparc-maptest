import os
import pathlib
import json
import numpy as np


def main():
    """Main"""

    print("Starting parameter creator")

    n_engines = 4  # numbero of engines
    output_dirs = {}
    for engine_i in range(1, n_engines + 1):
        output_dirs[engine_i] = pathlib.Path(
            os.environ["DY_SIDECAR_PATH_OUTPUTS"]) \
            / pathlib.Path(f'output_{engine_i}')

    print(f'Output directories: {output_dirs}')

    # params = {"gnabar_hh": 0.1, "gkbar_hh": 0.03}

    for i in range(1, n_engines + 1):
        params = {
            "gnabar_hh": float(np.random.uniform(
                0.1, 0.01)), "gkbar_hh": float(np.random.uniform(
                    0.01, 0.001))}
        with open(output_dirs[engine_i] / 'params.json', 'w') as params_file:
            json.dump(params, params_file)


if __name__ == '__main__':
    main()
