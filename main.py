import re
import glob
import logging
import utils
import argparse
from measurement import OPMeasurement
from circuit import OPCircuit


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        '-o',
        '--onionperf-path',
        help="""Path to OP analysis json files""",
        type=str,
        action="store",
        dest="op_path",
        default="")
    p.add_argument(
        '-c',
        '--consensus-path',
        help="""Path to consensus directories""",
        type=str,
        action="store",
        dest="c_path",
        default="")
    args = p.parse_args()
    circuits = []
    op_files = glob.glob(args.op_path)
    logging.basicConfig(level=logging.INFO)
    total_guard_first_hops = 0
    s = utils.StateObject()
    print(utils.count_path_lengths(op_files))

    for op_file in op_files:
        m = OPMeasurement(op_file)
        for hostname in m.hostnames:
            for circuit_id in m.get_circuit_ids(hostname):
                c = None
                try:
                    ts, path = m.get_circuit(hostname, circuit_id)
                    first_hop = path[0][0]
                    second_hop = path[1][0]
                    last_hop = path[2][0]
                    c = OPCircuit(ts, first_hop, second_hop, last_hop,
                                  args.c_path)
                except IndexError:
                    logging.debug("Circuit too short or missing details - {0}".
                                  format(circuit_id))
                except KeyError:
                    logging.debug(
                        "OnionPerf is missing details for circuit {0}".format(
                            circuit_id))
                except TypeError:
                    logging.debug(
                        "OnionPerf is missing details for circuit {0}".format(
                            circuit_id))
                if c:
                    fprint = c.first_hop[1:41]
                    flags = utils.find_flags(c.consensuses, fprint, s)
                    if flags and 'Guard' in flags:
                        total_guard_first_hops += 1
                    circuits.append(c)

    print("Total number of circuits analyzed: {0}".format(len(circuits)))
    print(
        "Total number of times a guard relay was chosen for the first hop {0}".
        format(total_guard_first_hops))
    print(
        "Total number of times a non-guard relay was chosen for the first hop {0}"
        .format(len(circuits) - total_guard_first_hops))


if __name__ == "__main__":
    main()
