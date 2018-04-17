from collections import namedtuple
import json

import pandas as pd
import requests


class Arlington:
    def __init__(self):
        self.limit = None

    def police_incidents(self, limit=None):
        """
        Retrieve jsonify'd police incident data from Open Data Portal
        """
        police_log = self.get_json('police_log', limit)
        frame = self.load_frame(police_log)
        return frame

    def get_json(self, stream_name, limit):
        """
        Retrieve jsonify'd police incident data from Open Data Portal
        """
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

        params = {'auth_key': config['api_key']}
        if limit is not None:
            params['limit'] = limit + 1  # limit plus header row

        data_json = requests.get(url, params=params).json()
        results = data_json['result']['fArray']

        return results

    def load_frame(self, api_result):
        """
        Load json result from Arlington Open Data Portal into pandas dataframe
        """

        headers, header_fields = self._extract_headers(api_result)
        result_count = int(len(api_result)/header_fields - 1)

        print(f'Found {result_count} results')

        incidents = self._extract_incidents(api_result, headers, header_fields)
        frame = pd.DataFrame(incidents, columns=headers)

        return frame

    def _extract_headers(self, api_result):
        """
        Extract header fields from Arlington Open Data json response
        """

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

    def _extract_incidents(self, api_result, headers, header_fields):
        Incident = namedtuple('incident', [field for field in headers])

        incidents = []
        i = header_fields
        while i <= len(api_result) - header_fields:
            fields = []
            for incident in api_result[i:i+header_fields]:
                fields.append(incident['fStr'])
            incidents.append(Incident(*fields))
            i += header_fields

        return incidents
