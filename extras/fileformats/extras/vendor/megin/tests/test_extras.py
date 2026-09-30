"""
Pytest tests for EEG/MEG file format validation and metadata reading.

Test data is downloaded via MNE's dataset utilities and cached for the session.

Authors:
- Miao Cao

Email:
- miaocao@swin.edu.au
"""

from fileformats.vendor.megin.biosig import Fif

# ------------------------------
# MEG: FIF
# ------------------------------


def test_fif_read_metadata(fif_path):
    metadata = Fif(fif_path).metadata
    assert metadata["sfreq"] is not None


def test_fif_deidentify(fif_path, tmp_path):
    fif = Fif(fif_path)
    orig_metadata = fif.metadata

    deid_fif = fif.deidentify(tmp_path)

    assert isinstance(deid_fif, Fif)

    deid_metadata = deid_fif.metadata
    assert orig_metadata != deid_metadata, "expected at least one field to change"

    # Subject identifying fields should be absent or cleared in the deidentified file
    deid_subject_info = deid_metadata.get("subject_info") or {}
    for pii_field in ("last_name", "first_name", "birthday"):
        assert not deid_subject_info.get(
            pii_field
        ), f"subject_info.{pii_field} was not cleared by deidentification"


def test_fif_deidentify_recipe_type():
    """The recipe format can be found from the deidentify implementation signature"""
    import typing as ty

    from fileformats.biosig import Biosig, MneAnonymizeRecipe
    from fileformats.core import LoadedMarker, find_extra_implementation

    impl = find_extra_implementation(Biosig.deidentify, Fif)
    hint = ty.get_type_hints(impl, include_extras=True)["recipe"]
    marker = LoadedMarker.from_hint(hint)
    assert marker is not None and marker.format is MneAnonymizeRecipe
