import os
import pathlib
import json
import numpy as np


def main():
    param_creator = ParamCreator()

    param_creator.start()


class ParamCreator:

    def __init__(self):
        """Constructor"""
        self.main_inputs_dir = pathlib.Path(
            os.environ["DY_SIDECAR_PATH_INPUTS"])
        self.input_dirs = [
            self.main_inputs_dir
            / f'input_{i}' for i in range(
                1,
                5)]
        self.engine_ids = []

    def start(self):
        print("Starting parameter creator")

        for input_dir in self.input_dirs:
            engine_fn = input_dir / 'engine.json'
            if engine_fn.exists():
                with open(engine_fn) as engine_file:
                    self.register_engine(json.load(engine_file))

        # print(f'Output directories: {output_dirs}')

        # params = {"gnabar_hh": 0.1, "gkbar_hh": 0.03}

        # for engine_i in range(1, n_engines + 1):
        #    print(f"Generated: {params} for engine {engine_i}")
        # with open(output_dirs[engine_i] / 'params.json', 'w') as params_file:
        #        print(f"{output_dirs[engine_i].resolve()}")
        #    json.dump(params, params_file)

    def register_engine(self, engine_info):
        """Register engines"""

        engine_id = engine_info['id']
        engine_status = engine_info['status']

        self.engine_ids.append(engine_id)
        print(f'Registered engine: {engine_id} with status {engine_status}')

    def create_run_task(self, engine_id):
        """Create dict with run info"""

        params = {
            "gnabar_hh": 0.1 + float(np.random.uniform(
                0.0011, 0.0015)), "gkbar_hh": 0.03 + float(np.random.uniform(
                    0.0011, 0.0015))}

        task = {'command': 'run', 'engine_id': engine_id, 'payload': params}

        return task


if __name__ == '__main__':
    main()
