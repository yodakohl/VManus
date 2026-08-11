#!/usr/bin/env python3
"""Source-free boundary tests for ``dani001_panel``.

The fixtures are synthetic.  They do not open a network endpoint, repository
transcription, atlas, deposited body, or real panel.
"""

from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import dani001_panel as panel


class _FakeResponse:
    def __init__(self, url: str, body: bytes) -> None:
        self._url = url
        self._body = body
        self._offset = 0

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def geturl(self) -> str:
        return self._url

    def read(self, size: int) -> bytes:
        block = self._body[self._offset:self._offset + size]
        self._offset += len(block)
        return block


class _FakeOpener:
    def __init__(self, bodies: dict[str, bytes]) -> None:
        self._bodies = bodies

    def open(self, request: object, *, timeout: float) -> _FakeResponse:
        del timeout
        url = request.full_url  # type: ignore[attr-defined]
        return _FakeResponse(url, self._bodies[url])


def _external_fixture() -> tuple[dict[str, bytes], bytes, bytes, bytes, bytes]:
    metadata = {
        "id": 22,
        "conceptrecid": "11",
        "revision": 4,
        "doi": "10.0000/synthetic",
        "created": "2026-01-01T00:00:00Z",
        "updated": "2026-01-02T00:00:00Z",
        "metadata": {
            "title": "Synthetic",
            "publication_date": "2026-01-01",
            "description": "Synthetic metadata fixture",
        },
        "files": [{
            "key": "synthetic.txt",
            "size": 3,
            "checksum": "md5:00000000000000000000000000000000",
            "links": {"self": "https://invalid.example/synthetic.txt"},
        }],
    }
    concept_body = panel.canonical_json(metadata)
    projection = panel.canonical_json(panel.stable_metadata_projection(metadata))
    pipeline_body = b"# inert synthetic pipeline fixture\n"
    lexicon_body = b'{"k":[{"domain":"general"}]}\n'
    return (
        {
            panel.CONCEPT_URL: concept_body,
            panel.PIPELINE_URL: pipeline_body,
            panel.LEXICON_URL: lexicon_body,
        },
        concept_body,
        projection,
        pipeline_body,
        lexicon_body,
    )


class DANI001PanelSourceFreeTests(unittest.TestCase):
    def test_atlas_validation_is_hash_only_provenance(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dani001-panel-files-") as outer:
            root = Path(outer)
            source_relatives = {
                edition: Path("transcription") / f"{edition}.txt"
                for edition in panel.EDITION_ORDER
            }
            source_hashes: dict[str, str] = {}
            for edition, relative in source_relatives.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                body = f"synthetic-{edition}\n".encode()
                path.write_bytes(body)
                source_hashes[edition] = hashlib.sha256(body).hexdigest()
            module = root / "experiments" / "semantic_assumptions"
            results = module / "results"
            results.mkdir(parents=True)
            spec_body = b"synthetic specification\n"
            atlas_body = b"synthetic atlas\n"
            validation_body = b"not JSON by design\n"
            (module / panel.SPEC_PATH.name).write_bytes(spec_body)
            (results / panel.ATLAS_PATH.name).write_bytes(atlas_body)
            (results / panel.ATLAS_VALIDATION_PATH.name).write_bytes(
                validation_body
            )
            with (
                mock.patch.object(
                    panel, "SOURCE_RELATIVE_PATHS", source_relatives
                ),
                mock.patch.object(panel, "SOURCE_SHA256", source_hashes),
                mock.patch.object(
                    panel,
                    "REGISTERED_SPEC_SHA256",
                    hashlib.sha256(spec_body).hexdigest(),
                ),
                mock.patch.object(
                    panel,
                    "ATLAS_SHA256",
                    hashlib.sha256(atlas_body).hexdigest(),
                ),
                mock.patch.object(
                    panel,
                    "ATLAS_VALIDATION_SHA256",
                    hashlib.sha256(validation_body).hexdigest(),
                ),
            ):
                paths, observed, atlas, validation = (
                    panel._validate_registered_files(root)
                )
            self.assertEqual(set(paths), set(panel.EDITION_ORDER))
            self.assertEqual(dict(observed), source_hashes)
            self.assertEqual(atlas.read_bytes(), atlas_body)
            self.assertEqual(validation.read_bytes(), validation_body)

    def test_core_code_collections_are_sorted_unique_tuples(self) -> None:
        body = panel.canonical_json({
            "k": [{"domain": "general", "source": "synthetic"}],
            "d": [{"domain": "function", "source": ""}],
            "zz": [{"domain": "medical", "source": None}],
        })
        bundle = panel.project_lexicon_bytes(body, enforce_registered=False)
        for view in bundle.views:
            self.assertIsInstance(view.direct_codes, tuple)
            self.assertIsInstance(view.deposited_affix_codes, tuple)
            self.assertEqual(view.direct_codes, tuple(sorted(set(view.direct_codes))))
            self.assertEqual(
                view.deposited_affix_codes,
                tuple(sorted(set(view.deposited_affix_codes))),
            )
        self.assertEqual(
            bundle.restored().direct_codes,
            bundle.view("FULL").direct_codes,
        )
        self.assertEqual(
            bundle.restored().deposited_affix_codes,
            bundle.view("FULL").deposited_affix_codes,
        )
        self.assertNotIn("zz", bundle.restored().reachable_keys)

    def test_private_dataclass_repr_does_not_expose_fields(self) -> None:
        token = panel.PanelToken(987_654, "syntheticsurface", (-1, 14))
        scanned = panel._ScanResult("privateeva", (-2, 13), True, True)
        self.assertEqual(repr(token), "PanelToken()")
        self.assertEqual(repr(scanned), "_ScanResult()")

    def test_split_acquisition_gate_inventory_and_cleanup(self) -> None:
        bodies, concept_body, projection, pipeline_body, lexicon_body = (
            _external_fixture()
        )
        fake_lexicon = object()
        lease: panel.RegisteredExternalAcquisition | None = None
        with tempfile.TemporaryDirectory(prefix="dani001-panel-test-") as outer:
            with (
                mock.patch.object(
                    panel.urllib.request,
                    "build_opener",
                    return_value=_FakeOpener(bodies),
                ),
                mock.patch.object(
                    panel,
                    "PIPELINE_SHA256",
                    hashlib.sha256(pipeline_body).hexdigest(),
                ),
                mock.patch.object(
                    panel,
                    "LEXICON_SHA256",
                    hashlib.sha256(lexicon_body).hexdigest(),
                ),
                mock.patch.object(
                    panel,
                    "STABLE_PROJECTION_SHA256",
                    hashlib.sha256(projection).hexdigest(),
                ),
                mock.patch.object(
                    panel,
                    "project_lexicon_bytes",
                    return_value=fake_lexicon,
                ) as project_mock,
            ):
                with panel.acquire_registered_external_files(
                    timeout=1.0,
                    temp_base=Path(outer),
                ) as lease:
                    inventory = {
                        item.name: item.read_bytes()
                        for item in sorted(lease.temporary_root.iterdir())
                    }
                    self.assertEqual(
                        inventory,
                        {
                            "lexicon.json": lexicon_body,
                            "pipeline.py.txt": pipeline_body,
                            "stable_metadata_projection.json": projection,
                        },
                    )
                    self.assertNotIn(concept_body, inventory.values())
                    representation = repr(lease)
                    self.assertNotIn(str(lease.temporary_root), representation)
                    self.assertNotIn("pipeline.py.txt", representation)
                    self.assertNotIn("lexicon.json", representation)
                    with self.assertRaises(panel.DANI001InputError):
                        panel.project_acquired_lexicon(
                            lease,
                            synthetic_gate_passed=False,
                        )
                    project_mock.assert_not_called()
                    result = panel.project_acquired_lexicon(
                        lease,
                        synthetic_gate_passed=True,
                    )
                    self.assertIs(result, fake_lexicon)
                    with self.assertRaises(panel.DANI001InputError):
                        panel.project_acquired_lexicon(
                            lease,
                            synthetic_gate_passed=True,
                        )
                    project_mock.assert_called_once_with(
                        lexicon_body,
                        enforce_registered=True,
                    )
                    lease_root = lease.temporary_root
                self.assertFalse(lease_root.exists())
                with self.assertRaises(panel.DANI001InputError):
                    panel.project_acquired_lexicon(
                        lease,
                        synthetic_gate_passed=True,
                    )
                project_mock.assert_called_once()

    def test_split_acquisition_cleans_up_after_caller_exception(self) -> None:
        bodies, _concept, projection, pipeline_body, lexicon_body = (
            _external_fixture()
        )
        lease_root: Path | None = None
        with tempfile.TemporaryDirectory(prefix="dani001-panel-test-") as outer:
            with (
                mock.patch.object(
                    panel.urllib.request,
                    "build_opener",
                    return_value=_FakeOpener(bodies),
                ),
                mock.patch.object(
                    panel,
                    "PIPELINE_SHA256",
                    hashlib.sha256(pipeline_body).hexdigest(),
                ),
                mock.patch.object(
                    panel,
                    "LEXICON_SHA256",
                    hashlib.sha256(lexicon_body).hexdigest(),
                ),
                mock.patch.object(
                    panel,
                    "STABLE_PROJECTION_SHA256",
                    hashlib.sha256(projection).hexdigest(),
                ),
            ):
                with self.assertRaisesRegex(RuntimeError, "synthetic caller stop"):
                    with panel.acquire_registered_external_files(
                        timeout=1.0,
                        temp_base=Path(outer),
                    ) as lease:
                        lease_root = lease.temporary_root
                        raise RuntimeError("synthetic caller stop")
                assert lease_root is not None
                self.assertFalse(lease_root.exists())


if __name__ == "__main__":
    unittest.main()
