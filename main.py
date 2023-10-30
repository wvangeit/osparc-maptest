import os
import pathlib
import json


def main():
    """Main"""

    print("Starting parameter creator")

    output1_dir = pathlib.Path(
        os.environ["DY_SIDECAR_PATH_OUTPUTS"]) / pathlib.Path('output_1')

    print(f'Output 1 directory: {output1_dir}')

    params = {"gnabar_hh": 0.1, "gkbar_hh": 0.03}
    with open(output1_dir / 'params.json', 'w') as params_file:
        json.dump(params, params_file)


if __name__ == '__main__':
    main()
