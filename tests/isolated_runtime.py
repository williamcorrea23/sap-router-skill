"""Shared subprocess boundary for tests: no personal config or persistent state."""
import atexit
import os
import subprocess
import tempfile

_state = tempfile.TemporaryDirectory(prefix='sap-router-tests-')
atexit.register(_state.cleanup)
os.environ['SAP_ROUTER_OFFLINE'] = '1'
os.environ['SAP_ROUTER_STATE_DIR'] = _state.name
_run = subprocess.run


def run(*args, **kwargs):
    env = {k: v for k, v in os.environ.items()
           if not any(k.startswith(p) for p in ('ARC_', 'SAP_', 'SAPGUI_', 'CPI_', 'APIM_', 'API_', 'BROWSER_', 'CHROME_'))}
    env.update(SAP_ROUTER_OFFLINE='1', SAP_ROUTER_STATE_DIR=_state.name,
               SAP_ROUTER_ROOT=os.path.dirname(os.path.dirname(__file__)))
    env.update(kwargs.pop('env', {}))
    kwargs.setdefault('timeout', 30)
    kwargs['env'] = env
    return _run(*args, **kwargs)
