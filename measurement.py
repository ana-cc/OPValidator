import json


class OPMeasurement():
    def __init__(self, filename):
        self.filename = filename
        self.data = self.load()
        self.hostnames = self.get_hostnames()

    def load(self):
        with open(self.filename) as f:
            data = json.load(f)
        return data["data"]

    def get_hostnames(self):
        hostnames = []
        for hostname in self.data:
            hostnames.append(hostname)
        return hostnames

    def get_circuit_ids(self, hostname):
        circuit_ids = []
        for circuit_id in self.data[hostname]["tor"]["circuits"]:
            circuit_ids.append(circuit_id)
        return circuit_ids

    def get_circuit(self, hostname, circuit_id):
        path = None
        ts = None
        try:
            path = self.data[hostname]["tor"]["circuits"][circuit_id]["path"]
            ts = self.data[hostname]["tor"]["circuits"][circuit_id][
                "unix_ts_start"]
        except KeyError:
            pass
        return ts, path
