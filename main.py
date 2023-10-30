import os
import pathlib
import json


def main():
    """Main"""

    print("Starting parameter creator")

    output1_dir = pathlib.Path(
        os.environ["OUTPUT_FOLDER"]) / pathlib.Path('output_1')

    for i in range(6):
        dir = pathlib.Path(
            os.environ["OUTPUT_FOLDER"]) / pathlib.Path(f'output_{i}')
        dir.mkdir()

    print(f'Output 1 directory: {output1_dir}')

    output1_dir.mkdir()

    params = {"gnabar_hh": 0.1, "gkbar_hh": 0.03}
    with open(output1_dir / 'params.json', 'w') as params_file:
        json.dump(params, params_file)


if __name__ == '__main__':
    main()
