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
    carte = subprocess.Popen([sys.executable, str(RACINE / "tests" / "faux_carte.py"), str(PORT + 1)],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)      # API de couverture (contrat du plan)
    env = {**os.environ, "CARTE_URL": f"http://127.0.0.1:{PORT + 1}"}
    p = subprocess.Popen([sys.executable, "-m", "passerelle.server", str(PORT)], cwd=RACINE, env=env,
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
        carte.kill()
        pytest.fail("la passerelle n'a pas démarré")
    os.environ["PASSERELLE_URL"] = url
    import chat.client as C
    C.URL = url
    yield url
    p.terminate()
    p.wait(10)
    carte.terminate()
