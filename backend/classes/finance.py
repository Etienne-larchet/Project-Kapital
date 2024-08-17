from typing import Optional

import numpy as np
import pandas as pd


class Fmaths:
    @staticmethod
    def generate_randoms_proba(
        probas_req: dict, arraysize=1, seed: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Generate random probability distributions given specified minimum and maximum bounds for each ticker.

        **Example usage:**
        >>> probas_req = {
        >>> 'tickers': ['AAPL', 'AMZN', 'MSFT'],
        >>> 'min': [0.05, 0.1, 0.1],
        >>> 'max': [0.5, 0.6, 0.3]
        >>> }
        >>> result = generate_randoms_proba(probas_req, 300)
        >>> print(result)
        """

        def _weights_calc(min_probs, max_probs, n, seed: Optional[int] = None):
            random_values = np.random.default_rng(seed).random(
                size=(arraysize, n), dtype=np.float32
            )
            weights = min_probs + max_probs * random_values
            weights /= weights.sum(axis=1, keepdims=True)
            return weights

        n = len(probas_req["tickers"])
        min_probs = probas_req.get("min", None)
        max_probs = probas_req.get("max", None)
        if not min_probs:
            min_probs = np.zeros(n)
        if not max_probs:
            max_probs = np.ones(n)
        if sum(min_probs) > 1:
            raise ValueError("Sum of min probabilities must be inferior to 1")
        elif sum(max_probs) < 1:
            raise ValueError("Sum of max probabilities must be superior to 1")
        weights = _weights_calc(
            min_probs=min_probs, max_probs=max_probs, n=n, seed=seed
        )
        return pd.DataFrame(weights, columns=probas_req["tickers"])
