import os
import pathlib
import json
import time
import uuid
import logging
import threading

import opt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("paramstest main")


def main():

    optimizer = opt.Optimizer()

    opt_thread = threading.Thread(target=optimizer.start)
    opt_thread.start()

    param_creator = ParamCreator()

    param_creator.start()


class ParamCreator:

    def __init__(self):
        """Constructor"""
        self.id = str(uuid.uuid4())
        self.main_inputs_dir = pathlib.Path(
            os.environ["DY_SIDECAR_PATH_INPUTS"])
        self.main_outputs_dir = pathlib.Path(
            os.environ["DY_SIDECAR_PATH_OUTPUTS"])

        self.input_dirs = [
            self.main_inputs_dir
            / f'input_{i}' for i in range(
                2,
                5)]

        self.map_input_path = pathlib.Path('./params.json')
        self.output_dir = self.main_outputs_dir / 'output_1'
        self.master_file_path = self.output_dir / 'master.json'
        self.engine_ids = []
        self.engine_submitted = {}
        self.status = 'ready'
        self.torun_tasks = []
        self.running_tasks = []
        self.finished_tasks = []

    def start(self):
        print("Starting parameter creator")

        self.init_master_file()
        for input_dir in self.input_dirs:
            engine_fn = input_dir / 'engine.json'
            if engine_fn.exists():
                with open(engine_fn) as engine_file:
                    self.register_engine(json.load(engine_file))

        while True:
            self.check_map_files()
            self.check_engine_files()
            time.sleep(20)

    def populate_tasklist(self):

        with open(self.map_input_path) as map_input_file:
            map_input = json.load(map_input_file)

        for task_id, param_values in enumerate(map_input):
            params = {
                "gnabar_hh": param_values[0],
                "gkbar_hh": param_values[1]}
            task = {'command': 'run', 'task_id': task_id, 'payload': params}
            self.torun_tasks.append(task)

        logging.info(f"Created tasks: {self.torun_tasks}")

    def write_map_output(self):

        objs = []
        self.finished_tasks.sort(key=lambda task: task['id'])
        for task in self.finished_tasks:
            obj = task['payload']
            objs.append(obj)

        with open(self.map_output_path) as map_output_file:
            json.dump(objs, map_output_file, indent=4)

        self.finished_tasks = []

    def check_map_files(self):

        logging.info("Checking map files ...")

        if self.status == 'ready':
            if self.map_input_path.exists():
                self.populate_tasklist()
                self.status = 'computing'
        elif self.status == 'computing' and \
                len(self.torun_tasks) == 0 and \
                len(self.running_task) == 0:
            self.write_map_output()
            self.status = 'ready'

    def check_engine_files(self):

        logging.info("Checking engine files ...")

        for input_dir in self.input_dirs:
            engine_fn = input_dir / 'engine.json'
            if engine_fn.exists():
                engine_info = self.get_engine_info(engine_fn)
                if engine_info['id'] not in self.engine_ids:
                    self.register_engine(engine_info)

                if engine_info['status'] == 'ready' and \
                        not self.engine_submitted[engine_info['id']]:
                    if len(self.torun_tasks) != 0:
                        self.submit_task(engine_info)
                elif engine_info['status'] == 'submitted':
                    self.process_engine_payload(engine_info)
                    payload = self.process_engin_payload(engine_info)
                    print(
                        f'Received result {payload} '
                        f'from [engine_info["id"]')

                    self.set_engine_ready(engine_info['id'])

    def process_engine_payload(self, engine_info):
        """Get payload from engine"""

        task_id = engine_info['task_id']

        for i, task in enumerate(self.running_tasks):
            if task['task_id'] == task_id:
                self.finished_tasks.append(task)
                self.running_tasks.remove(i)

    def set_engine_ready(self, engine_id):
        master_dict = self.read_master_dict()

        master_dict['engines'][engine_id] = {'task':
                                             {'command': 'get ready'}}

        self.write_master_dict(master_dict)

        self.engine_submitted[engine_id] = False

    def get_engine_info(self, engine_fn):
        with open(engine_fn) as engine_file:
            engine_info = json.load(engine_file)

        print(f"Master received engine info: {engine_info}", flush=True)
        return engine_info

    def register_engine(self, engine_info):
        """Register engines"""

        engine_id = engine_info['id']
        engine_status = engine_info['status']

        if engine_status == 'ready':
            self.engine_ids.append(engine_id)
            self.engine_submitted[engine_id] = False
        elif engine_status == 'submitted':
            self.engine_ids.append(engine_id)
            self.set_engine_ready(engine_info['id'])
        else:
            raise ValueError(
                "Trying to register an engine that is not ready, "
                f"status: {engine_status}")

        master_dict = self.read_master_dict()
        master_dict['engines'][engine_id] = {}
        self.write_master_dict(master_dict)

        print(f"Registered engine: {engine_id}")

    def init_master_file(self):

        master_dict = {'engines': {}, 'id': self.id}
        self.write_master_dict(master_dict)

    def read_master_dict(self):
        with open(self.master_file_path) as master_file:
            master_dict = json.load(master_file)

        return master_dict

    def write_master_dict(self, master_dict):
        with open(self.master_file_path, 'w') as master_file:
            json.dump(master_dict, master_file, indent=4)

        print("Created new master.json: {master_dict}")

    def submit_task(self, engine_dict):
        """Create dict with run info"""

        engine_id = engine_dict['id']

        task = self.torun_tasks.pop()
        self.running_tasks.append(task)

        master_dict = self.read_master_dict()

        engine_command_dict = master_dict['engines'][engine_id]

        if engine_dict['status'] != 'ready':
            raise ValueError("Trying to run on engine that is not ready")

        engine_command_dict['task'] = task

        self.write_master_dict(master_dict)

        self.engine_submitted[engine_id] = True


if __name__ == '__main__':
    main()
