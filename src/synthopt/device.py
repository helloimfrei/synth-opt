import live
import json
import pickle
from pathlib import Path
from skopt import Optimizer
from skopt.space import Categorical, Integer, Real


class DeviceOptimizer:
    """
    Locate and access parameters of a device in an active Live set.
    All parameters of interest must be configured within Live!
    """

    def __init__(self,device_name:str,track_name:str=None,state_file:str="saved_params/optimizer_state.pkl"):
        self.name = device_name
        self.device = self.locate_device(device_name,track_name=track_name)
        self.params = {param.name: param.value[-1] for param in self.device.parameters}
        self.params.pop("Device On", None)
    
        Path("saved_params").mkdir(parents=True, exist_ok=True)
        self.state_file = Path(state_file)

        # Initialize or restore optimizer
        if self.state_file.exists():
            self.opt = pickle.load(open(self.state_file, "rb"))
            self.pending_x = None
        else:
            dims = [Real(0, 1) for _ in range(len(self.params))]
            self.opt = Optimizer(dimensions=dims, base_estimator="GP", acq_func="EI", random_state=42)
            self.pending_x = None
            self._log_params("init")

    def locate_device(self,name:str,track_name:str=None):
        """
        Locate device by name in an active Live set. Provide an optional track name to limit search to a specific track.
        """
        set = live.Set(scan=True)
        tracks = set.tracks if track_name is None else [track for track in set.tracks if track.name == track_name]
        devices = [device for track in tracks for device in track.devices]
        for device in devices:
            if name.lower() in device.name.lower():
                return device
        raise Exception(f"No matching device found in Live set for query: {name} on {'any track' if track_name is None else track_name}.") 

## update param attributes
    def get_params(self):
        return self.params

    def set_params(self, params:dict[str,float]):
        self.params.update(params)

## push/pull param attributes from live
    def refresh_params(self):
        """
        Refresh params from Live (does not set them as attributes).
        """
        params = {param.name: param.value[-1] for param in self.device.parameters}
        params.pop("Device On", None)
        return params


    def push_params(self):
        """
        Push params from attributes to Live.
        """
        for param in self.device.parameters:
            if param.name in self.params:
                param.value = self.params[param.name]


## save stuff
    def _log_params(self, tag: str):
        base_dir = self.state_file.parent 
        base_dir.mkdir(parents=True, exist_ok=True)
        with open(base_dir / f"params_{tag}.json", "w") as f:
            json.dump(self.params, f, indent=2)


    def _save_optimizer(self):
        """
        Save optimizer state to disk (pickle).
        """
        with open(self.state_file, "wb") as f:
            pickle.dump(self.opt, f)


## convert params between optimizer and live formats
    def _vector_to_params(self, x: list[float]) -> dict[str, list]:
        param_ids = [ids[0:3] for ids in self.params.values()]

        updated_params = {}
        for key,param_id, value in zip(self.params.keys(),param_ids, x):
            updated_params[key] = param_id + [value]

        return updated_params

## optimizer
    def ask(self) -> dict:
        """
        Propose the next parameter set to try (does not apply it).
        """
        x = self.opt.ask()
        self.pending_x = x
        return dict(zip(self.params.keys(), x))

    def tell(self, score: float, log: bool = True):
        """
        Report the observed 'score' for the most recent suggestion.
        Larger 'score' is assumed better (skopt minimizes by default so sign is flipped).
        """
        if self.pending_x is None:
            raise RuntimeError("No pending proposal. Call .ask() first.")
        self.opt.tell(self.pending_x, -float(score))
        self.pending_x = None
        if log:
            self._log_params(tag=f"score_{score}")
        self._save_optimizer()

