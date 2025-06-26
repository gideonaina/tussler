import garak
# from garak import config
from garak import core

def queue_probes():
    # Initialize Garak configuration
    # cfg = config.get_config()

    # Load all probes using the ProbeManager
    pm = core.ProbeManager()
    probes = pm.list_probes()

    # Print or return list of probes
    for probe in probes:
        print(probe)


if __name__ == "__main__":
    queue_probes()