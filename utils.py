import json
from datetime import datetime
from collections import Counter
from stem.descriptor import parse_file
from measurement import OPMeasurement


def count_path_lengths(op_files):
    paths = []
    for op_file in op_files:
        m = OPMeasurement(op_file)
        for hostname in m.hostnames:
            for circuit_id in m.get_circuit_ids(hostname):
                path_length = None
                ts, path = m.get_circuit(hostname, circuit_id)
                if path:
                    path_length = len(path)
                if path_length:
                    paths.append(path_length)
    cnt = Counter(paths)
    return cnt.most_common()


def find_flags(consensus_paths, fingerprint, state_obj):
    """
    Finds flags of a given relay by fingerprint and consensus files.  Creates
    an empty flag list and looks in the current state object for cached
    consensuses. If the required consensus files are not cached, it parses the
    corresponding files.  It then looks for the relay in the loaded consensuses,
    populating the flags list upon finding it.

    :param fingerprint: string
    :param consensus_paths: list
    :param state_object: StateObject
    :returns: list
    """
    consensus = None
    flags = []
    if consensus_paths == state_obj.filenames:
        consensuses = state_obj.consensuses
    else:
        consensuses = [
            list(parse_file(consensus_path))
            for consensus_path in consensus_paths
        ]
        state_obj.update(consensus_paths, consensuses)
    for consensus in consensuses:
        for desc in consensus:
            if desc.fingerprint == fingerprint:
                flags.extend(desc.flags)
    return flags

def find_consensus_path(path_prefix, ts):
    """
    Finds the path to a consensus based on a given timestamp.
    Path is relative to the current directory.

    :param ts: Unix timestamp
    :returns: string
    """
    d = datetime.fromtimestamp(int(ts))
    # 2019-01-01-05-00-00-consensus
    prefix = "{0}-{1}-{2}-{3}-00-00-consensus".format(d.year, f"{d.month:02d}", f"{d.day:02d}", f"{d.hour:02d}")
    consensus_path = "consensuses-{0}-{1}/{2}/{3}".format(d.year, f"{d.month:02d}", f"{d.day:02d}", prefix)
    return path_prefix + consensus_path

class StateObject():
    """
    Class to hold filenames and corresponding contents. Used for consensus files.
    """

    filenames = None
    consensuses = None

    def update(self, filenames, consensuses):
        """
        Updates contents of the state object

        :param filenames: list
        :param consensuses: list
        """
        self.filenames = filenames
        self.consensuses = consensuses
