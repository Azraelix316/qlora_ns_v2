"""Numerics for structure-preserving low-rank 2-D Navier--Stokes."""
from .dlra import DLRA, RankStats, SVDProjector
from .forcing import (
    FrozenVorticityForcing,
    KolmogorovForcing,
    SelfConsistentForcing,
    ZeroForcing,
)
from .ns_psi import EnergyTerms, StreamFunctionNS
from .pod import PODDMD, PODGalerkin, fit_pod
from .spectral import Grid2D, fluctuations, zonal_mean

__all__ = [
    "DLRA",
    "EnergyTerms",
    "FrozenVorticityForcing",
    "Grid2D",
    "KolmogorovForcing",
    "PODDMD",
    "PODGalerkin",
    "RankStats",
    "SVDProjector",
    "SelfConsistentForcing",
    "StreamFunctionNS",
    "ZeroForcing",
    "fit_pod",
    "fluctuations",
    "zonal_mean",
]
