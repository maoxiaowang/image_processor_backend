import json
from typing import Any

import numpy


class NumJsonEncoder(json.JSONEncoder):

    def default(self, o: Any) -> Any:
        if isinstance(o, numpy.uint8):
            return int(o)

        return super().default(o)
