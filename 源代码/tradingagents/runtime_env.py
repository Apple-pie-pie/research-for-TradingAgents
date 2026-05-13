from __future__ import annotations

import os
import shutil
from pathlib import Path


def _first_configured_ca_bundle() -> str | None:
    for var_name in ("CURL_CA_BUNDLE", "REQUESTS_CA_BUNDLE", "SSL_CERT_FILE"):
        value = os.environ.get(var_name)
        if value:
            return value
    return None


def _set_missing_ca_env_vars(bundle_path: str) -> None:
    for var_name in ("SSL_CERT_FILE", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE"):
        os.environ.setdefault(var_name, bundle_path)


def configure_ca_bundle() -> str | None:
    existing_bundle = _first_configured_ca_bundle()
    if existing_bundle and Path(existing_bundle).exists():
        _set_missing_ca_env_vars(existing_bundle)
        return existing_bundle

    try:
        import certifi
    except ImportError:
        return None

    source = Path(certifi.where())
    if not source.exists():
        return None

    local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    target = local_app_data / "TradingAgents" / "certs" / "cacert.pem"
    target.parent.mkdir(parents=True, exist_ok=True)

    if not target.exists() or source.stat().st_mtime_ns != target.stat().st_mtime_ns:
        shutil.copyfile(source, target)
        os.utime(target, ns=(source.stat().st_atime_ns, source.stat().st_mtime_ns))

    bundle_path = str(target)
    _set_missing_ca_env_vars(bundle_path)
    return bundle_path