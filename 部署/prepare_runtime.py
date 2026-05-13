import os
import shutil
from pathlib import Path

import certifi


def main() -> None:
    local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    target = local_app_data / "TradingAgents" / "certs" / "cacert.pem"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(certifi.where(), target)
    print(str(target))


if __name__ == "__main__":
    main()