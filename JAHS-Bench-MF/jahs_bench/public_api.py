import logging
from functools import partial
from pathlib import Path
from typing import Optional, Union

import numpy as np
import pandas as pd
from jahs_bench.lib.surrogate import XGBSurrogate

_log = logging.getLogger(__name__)
_log.setLevel(logging.WARNING)


class Benchmark:
    def __init__(self, model_path: Optional[Union[str, Path]] = True):
        if isinstance(model_path, str):
            model_path = Path(model_path)

        assert model_path is not None, \
            "A path to a directory where a surrogate model was saved must be given."
        assert model_path.exists() and model_path.is_dir()
        self.surrogate = XGBSurrogate.load(model_path)
        self._call_fn = partial(self._benchmark_surrogate, surrogate=self.surrogate)

    def __call__(self, config: dict, nepochs: Optional[int] = 200):
        return self._call_fn(config=config, nepochs=nepochs)

    @staticmethod
    def _benchmark_surrogate(surrogate: XGBSurrogate, config: dict,
                             nepochs: Optional[int] = 200) -> dict:
        features = pd.Series(config).to_frame().transpose()
        features.loc[:, "epoch"] = nepochs

        outputs: np.ndarray = surrogate.predict(features)
        outputs = outputs.reshape(-1, surrogate.label_headers.size)

        return {k: outputs[0][i] for i, k in enumerate(surrogate.label_headers.values)}


if __name__ == "__main__":
    from jahs_bench.search_space.configspace import joint_config_space
    conf = joint_config_space.sample_configuration().get_dictionary()

    b = Benchmark(
        model_path=Path("/home/archit/thesis/experiments/test/surrogates/full_data")
    )
    res = b(config=conf, nepochs=200)
    print(res)
