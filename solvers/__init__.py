"""Numerics for structure-preserving low-rank 2-D Navier--Stokes."""
from .dlra import DLRA, RankStats, SVDProjector
from .forcing import (
    FrozenVorticityForcing,
    KolmogorovForcing,
    SelfConsistentForcing,
    ZeroForcing,
)
from .ns_psi import EnergyTerms, StreamFunctionNS
from .pod import PODGalerkin, fit_pod
from .spectral import Grid2D

__all__ = [
    "DLRA",
    "EnergyTerms",
    "FrozenVorticityForcing",
    "Grid2D",
    "KolmogorovForcing",
    "PODGalerkin",
    "RankStats",
    "SVDProjector",
    "SelfConsistentForcing",
    "StreamFunctionNS",
    "ZeroForcing",
    "fit_pod",
]
