from utils import find_consensus_path


class OPCircuit():
    """
    Class to model OnionPerf Circuits.
    :attribute time: Unix timestamp
    :attribute first_hop: string
    :attribute second_hop: string
    :attribute last_hop: string
    :attribute consensuses: list
    """

    def __init__(self, time, f, s, l, path):

        self.time = time
        self.first_hop = f
        self.second_hop = s
        self.last_hop = l
        self.consensuses = [
            find_consensus_path(path, self.time),
            find_consensus_path(path, self.time - 3600),
            find_consensus_path(path, self.time - 7200)
        ]
