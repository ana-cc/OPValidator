import glob
import json
import argparse
import pandas as pd
import sys


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


def get_last(ob):
    states = [
        "socket_create", "socket_connect", "proxy_init", "proxy_choice",
        "proxy_request", "proxy_response", "command", "response",
        "payload_progress", "checksum"
    ]
    for state in states:
        if state not in ob:
            return previous_state
        previous_state = state

    return "All states seen"


def main():
    parser = argparse.ArgumentParser(description='Process OPfiles')
    parser.add_argument(
        '--path',
        type=str,
        required=True,
        dest="path",
        help='Path(s) to files')
    args = parser.parse_args()

    #op_files = glob.glob("/home/ana/Measurements/*/*/*json")
    op_files = glob.glob(args.path + "/*json")
    if not op_files:
        sys.exit(
            "No suitable files found for analysis, please ensure your files are in json format and end with *json"
        )

    all_csv_data = pd.DataFrame()
    all_errors = 0
    for f in op_files:
        m = OPMeasurement(f)
        hostnames = m.get_hostnames()
        if len(hostnames) == 1:
            hostname = hostnames[0]

            tgen_data = m.data[hostname]["tgen"]["transfers"]
            tor_circuit_data = m.data[hostname]["tor"]["circuits"]
            tor_stream_data = m.data[hostname]["tor"]["streams"]

            tgen_dfObj = pd.DataFrame.from_dict(
                tgen_data,
                orient="index",
            )
            tgen_dfObj["endpoint_local"] = tgen_dfObj["endpoint_local"].apply(
                lambda x: x[20:])
            tgen_dfObj["total_seconds"] = tgen_dfObj[
                "unix_ts_end"] - tgen_dfObj["unix_ts_start"]
            tgen_dfObj["elapsed_seconds"] = pd.DataFrame.from_dict(
                tgen_dfObj["elapsed_seconds"])
            tgen_dfObj["state_failed"] = tgen_dfObj["elapsed_seconds"].apply(
                lambda x: get_last(x))

            new_df = tgen_dfObj[(tgen_dfObj.error_code != 'NONE')]
            all_errors +=len(new_df)

            tor_stream_dfObj = pd.DataFrame.from_dict(
                tor_stream_data, orient="index")
            tor_stream_dfObj["source"] = tor_stream_dfObj["source"].astype(str)
            tor_stream_dfObj["source"] = tor_stream_dfObj["source"].apply(
                lambda x: x[10:])

            tor_circuit_dfObj = pd.DataFrame.from_dict(
                tor_circuit_data, orient="index")

            try:
                tor_circuit_dfObj["circuit_id"] = tor_circuit_dfObj[
                    "circuit_id"].astype(str)
            except:
                print(f)

            unified_circuit_stream_data = pd.merge(
                tor_circuit_dfObj,
                tor_stream_dfObj,
                how="outer",
                on="circuit_id")

            unified_circuit_stream_data = pd.merge(
                tgen_dfObj,
                unified_circuit_stream_data,
                how="left",
                right_on="source",
                left_on="endpoint_local")

            unified_circuit_stream_data = unified_circuit_stream_data[(
                unified_circuit_stream_data.error_code != 'NONE')]

            all_csv_data = all_csv_data.append(unified_circuit_stream_data)
        else:
            sys.exit("Don't know how to deal with multiple hostnames yet")

    if not all_csv_data.empty:
        try:
            all_csv_data["failure_reason_local"] = all_csv_data[
                "failure_reason_local_y"]
        except:
            #if there are no failures at all in the circuit data then the csv column will simply be left empty
            pass
        try:
            all_csv_data["failure_reason_remote"] = all_csv_data[
                "failure_reason_remote_y"]
        except:
            #if there are no failures at all in the circuit data then the csv column will simply be left empty
            pass
        header = [
            'transfer_id', 'is_error', 'error_code', 'state_failed',
            'total_seconds', 'endpoint_remote', 'total_bytes_read',
            'circuit_id', 'stream_id','buildtime_seconds', 'failure_reason_local',
            'failure_reason_remote', 'path',  'source', 'target'
        ]
        if not all_csv_data.failure_reason_local_x.empty:
           header.extend(['failure_reason_local_x'])

        if not all_csv_data.failure_reason_remote_x.empty:
           header.extend(['failure_reason_remote_x'])
        print("all errors: {0}".format(all_errors))
        all_csv_data.to_csv("errors.csv", index=False, columns=header)
    else:
        sys.exit("Could not find any error data in the json files")


if __name__ == "__main__":
    main()
