import pathlib
import time
import json

import bluepyopt as bpopt


def main():
    """Main"""
    optimizer = Optimizer()
    optimizer.start()


class DummyEvaluator(bpopt.evaluators.Evaluator):

    def init_simulator_and_evaluate_with_lists(
            self, param_list=None, target='scores'):
        return self.evaluate_with_lists(
            param_list=param_list, target=target)

    def evaluate_with_lists(self, param_list=None, target='scores'):
        """Run evaluation with lists as input and outputs"""

        print(f"Evaluating with lists: {param_list}")

        return [1.0, 1.0]


class FileMap:

    def __init__(self, input_file_path,
                 output_file_path):
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path

    def evaluate(self, params):

        if self.output_file_path.exists():
            self.output_file_path.unlink()

        with open(self.input_file_path, 'w') as input_file:
            json.dump(params, input_file, indent=4)

        while True:
            print(
                f'Waiting for output file: {self.output_file_path.resolve()}')
            if self.output_file_path.exists():
                with open(self.output_file_path) as output_file:
                    objs = json.load(output_file)
                self.output_file_path.unlink()
                self.input_file_path.unlink()
                print('Returning objectives')
                return objs
            else:
                time.sleep(10)

    def map_function(self, *map_input):
        _ = map_input[0]
        params = map_input[1]

        return self.evaluate(params)


class Optimizer:

    def __init__(self):
        self.params = [
            bpopt.parameters.Parameter(
                'gnabar_hh', bounds=[0.05, 0.125]),
            bpopt.parameters.Parameter(
                'gkbar_hh', bounds=[0.01, 0.075])]
        self.objectives = [
            bpopt.objectives.Objective(f'obj{i}') for i in range(2)]

        self.evaluator = DummyEvaluator(
            params=self.params, objectives=self.objectives)

    def start(self):
        print("Starting optimization")
        map = FileMap(pathlib.Path('params.json'), pathlib.Path('objs.json'))
        optimisation = bpopt.optimisations.DEAPOptimisation(
            evaluator=self.evaluator,
            offspring_size=3,
            map_function=map.map_function)

        final_pop, hall_of_fame, logs, hist = optimisation.run(max_ngen=10)
        print(f"Optimization done: {final_pop}")


if __name__ == '__main__':
    main()
