"""Lance une vraie passerelle (sous-processus) pour toute la session de tests."""
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
PORT = int(os.environ.get("PORT_TEST", "8779"))


@pytest.fixture(scope="session")
def passerelle():
    p = subprocess.Popen([sys.executable, "-m", "passerelle.server", str(PORT)], cwd=RACINE,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{PORT}"
    for _ in range(120):
        try:
            urllib.request.urlopen(url + "/v1/sante", timeout=1)
            break
        except Exception:
            time.sleep(0.5)
    else:
        p.kill()
        pytest.fail("la passerelle n'a pas démarré")
    os.environ["PASSERELLE_URL"] = url
    import chat.client as C
    C.URL = url
    yield url
    p.terminate()
    p.wait(10)
