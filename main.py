from collections import namedtuple
import json

import pandas as pd
import requests


def main():
    """
    Load a pandas DataFrame with police incident data
    from Arlington's Open Data Portal
    """

    stream_name = 'police_log'

    with open('config.json') as config_file:
        config = json.load(config_file)

    stream_guid = ''
    for stream in config['data_streams']:
        if stream['name'] == stream_name:
            stream_guid = stream['guid']
            break

    url = (config['api_url_prefix']
           + stream_guid
           + config['api_url_suffix'])
    params = {'auth_key': config['api_key'], 'limit': 1000}

    data_json = requests.get(url, params=params).json()
    results = data_json['result']['fArray']

    # Extract headers
    headers, header_fields = extract_headers(results)
    print(f'Found {(len(results)/header_fields - header_fields)} results')

    Incident = namedtuple('incident', [field for field in headers])

    # Create list of Incidents
    incidents = []
    i = header_fields
    while i <= len(results) - header_fields:
        fields = []
        for incident in results[i:i+header_fields]:
            fields.append(incident['fStr'])
        incidents.append(Incident(*fields))
        i += header_fields

    frame = pd.DataFrame(incidents, columns=headers)
    print(frame)


def extract_headers(api_result):
    headers = []
    header_fields = 0
    for result in api_result:
        try:
            result['fHeader']
            headers.append(result['fStr'])
            header_fields += 1
        except KeyError:
            break
    return (headers, header_fields)


if __name__ == '__main__':
    main()
