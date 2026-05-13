from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch


def test_configure_ca_bundle_copies_certifi_bundle_to_ascii_path(monkeypatch, tmp_path):
    source_bundle = tmp_path / "部署" / ".venv" / "Lib" / "site-packages" / "certifi" / "cacert.pem"
    source_bundle.parent.mkdir(parents=True)
    source_bundle.write_text("dummy-cert", encoding="utf-8")

    local_app_data = tmp_path / "LocalAppData"
    monkeypatch.setenv("LOCALAPPDATA", str(local_app_data))
    monkeypatch.delenv("SSL_CERT_FILE", raising=False)
    monkeypatch.delenv("REQUESTS_CA_BUNDLE", raising=False)
    monkeypatch.delenv("CURL_CA_BUNDLE", raising=False)

    from tradingagents.runtime_env import configure_ca_bundle

    expected = local_app_data / "TradingAgents" / "certs" / "cacert.pem"
    if expected.exists():
        expected.unlink()

    with patch("certifi.where", return_value=str(source_bundle)):
        bundle_path = configure_ca_bundle()

    assert bundle_path == str(expected)
    assert expected.read_text(encoding="utf-8") == "dummy-cert"
    assert Path(bundle_path).exists()
    assert "部署" not in bundle_path
    assert bundle_path == os.environ["SSL_CERT_FILE"]
    assert bundle_path == os.environ["REQUESTS_CA_BUNDLE"]
    assert bundle_path == os.environ["CURL_CA_BUNDLE"]


def test_configure_ca_bundle_preserves_existing_valid_bundle(monkeypatch, tmp_path):
    existing_bundle = tmp_path / "custom" / "bundle.pem"
    existing_bundle.parent.mkdir(parents=True)
    existing_bundle.write_text("custom-cert", encoding="utf-8")

    monkeypatch.setenv("REQUESTS_CA_BUNDLE", str(existing_bundle))
    monkeypatch.delenv("SSL_CERT_FILE", raising=False)
    monkeypatch.delenv("CURL_CA_BUNDLE", raising=False)

    from tradingagents.runtime_env import configure_ca_bundle

    bundle_path = configure_ca_bundle()

    assert bundle_path == str(existing_bundle)
    assert str(existing_bundle) == os.environ["SSL_CERT_FILE"]
    assert str(existing_bundle) == os.environ["REQUESTS_CA_BUNDLE"]
    assert str(existing_bundle) == os.environ["CURL_CA_BUNDLE"]