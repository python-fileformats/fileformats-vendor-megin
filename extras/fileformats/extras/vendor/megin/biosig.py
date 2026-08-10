import os
import typing as ty
from pathlib import Path

import mne.io

from fileformats.biosig.base import Biosig
from fileformats.core import extra_implementation, FileSet
from fileformats.extras.biosig.utils import mne_deidentify
from fileformats.vendor.megin.biosig import Fif


@extra_implementation(FileSet.read_metadata)
def fif_read_metadata(fif: Fif, **kwargs: ty.Any) -> ty.Mapping[str, ty.Any]:
    return mne.io.read_raw_fif(fif, preload=False, verbose=False).info.to_json_dict()  # type: ignore[no-any-return]


@extra_implementation(Biosig.deidentify)
def fif_deidentify(
    fif: Fif,
    out_dir: os.PathLike[str],
    spec: ty.Any = None,
    **kwargs: ty.Any,
) -> Fif:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = mne.io.read_raw_fif(fif, preload=True, verbose=False)
    raw.info = mne_deidentify(raw, spec)
    deid_fspath = out_dir / "meg-signals.fif"
    raw.save(deid_fspath, overwrite=True)
    return Fif(deid_fspath)
