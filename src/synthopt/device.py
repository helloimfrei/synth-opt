import live
import json
import pickle
from pathlib import Path
from skopt import Optimizer
from skopt.space import Real

"""
TODO:
Breaks when devices are inserted before the device of interest
For stock plugins without a configure button, need a way to filter what parameters are of interest 
(for now, grouping into Instrument Rack and assigning macros is OK. But need to filter out all default macros that aren't assigned)

"""

class DeviceOptimizer:
    """
    Locate and access parameters of a device in an active Live set.
    All parameters of interest must be configured within Live!
    """

    def __init__(self, device_name: str, track_name: str = None,
                 state_file: str = "saved_state/optimizer_state.pkl"):
        self.name = device_name
        self.device = self.locate_device(device_name, track_name=track_name)
        self.params = {param.name: param.value[-1] for param in self.device.parameters}
        self.params.pop("Device On", None)

        Path("saved_state").mkdir(parents=True, exist_ok=True)
        self.state_file = Path(state_file)

        # single JSON log file path
        self.params_log = self.state_file.parent / "saved_params.json"
        if not self.params_log.exists():
            with open(self.params_log, "w") as f:
                json.dump([], f)  # start with an empty list
            self.round_count = 0
        else:
            with open(self.params_log, "r") as f:
                history = json.load(f)
            self.round_count = len(history)  # resume from last count

        # Initialize or restore optimizer
        if self.state_file.exists():
            with open(self.state_file, "rb") as f:
                self.opt = pickle.load(f)
            self.pending_x = None
        else:
            dims = [Real(0, 1) for _ in range(len(self.params))]
            self.opt = Optimizer(dimensions=dims, base_estimator="GP", acq_func="EI", random_state=42)
            self.pending_x = None

    def locate_device(self, name: str, track_name: str = None):
        set = live.Set(scan=True)
        tracks = set.tracks if track_name is None else [t for t in set.tracks if t.name == track_name]
        devices = [device for t in tracks for device in t.devices]
        for device in devices:
            if name.lower() in device.name.lower():
                return device
        raise Exception(f"No matching device found in Live set for query: {name} on {'any track' if track_name is None else track_name}.")

    ## update param attributes
    def get_params(self):
        return self.params

    def set_params(self, params: dict[str, float]):
        self.params.update(params)

    ## push/pull param attributes from live
    def refresh_params(self):
        params = {param.name: param.value[-1] for param in self.device.parameters}
        params.pop("Device On", None)
        return params

    def push_params(self):
        for param in self.device.parameters:
            if param.name in self.params:
                param.value = self.params[param.name]

    ## save stuff
    def _log_params(self, score: float | None = None):
        """Append params, round number, and score to a single JSON file."""
        with open(self.params_log, "r") as f:
            history = json.load(f)

        entry = {
            "round": self.round_count,
            "params": self.params,
            "score": score,
        }
        history.append(entry)

        with open(self.params_log, "w") as f:
            json.dump(history, f, indent=2)

    def _save_optimizer(self):
        with open(self.state_file, "wb") as f:
            pickle.dump(self.opt, f)

    ## convert params between optimizer and live formats
    def _vector_to_params(self, x: list[float]) -> dict[str, list]:
        param_ids = [ids[0:3] for ids in self.params.values()]
        updated_params = {}
        for key, param_id, value in zip(self.params.keys(), param_ids, x):
            updated_params[key] = param_id + [value]
        return updated_params

    ## optimizer
    def ask(self) -> dict:
        x = self.opt.ask()
        self.pending_x = x
        return dict(zip(self.params.keys(), (round(v,2) for v in x)))

    def tell(self, score: float, log: bool = True):
        if self.pending_x is None:
            raise RuntimeError("No pending proposal. Call .ask() first.")
        self.opt.tell(self.pending_x, -float(score))
        self.pending_x = None
        if log:
            self._log_params(score=score)
            self.round_count += 1
        self._save_optimizer()
