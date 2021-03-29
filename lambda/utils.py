import logging
import os
import boto3
import json
from botocore.exceptions import ClientError
from typing import Dict, Any


def create_presigned_url(object_name):
    """Generate a presigned URL to share an S3 object with a capped expiration of 60 seconds

    :param object_name: string
    :return: Presigned URL as string. If error, returns None.
    """
    s3_client = boto3.client('s3',
                             region_name=os.environ.get('S3_PERSISTENCE_REGION'),
                             config=boto3.session.Config(signature_version='s3v4',s3={'addressing_style': 'path'}))
    try:
        bucket_name = os.environ.get('S3_PERSISTENCE_BUCKET')
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=60*1)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


def _load_apl_document(file_path):
    """Load the apl json document at the path into a dict object."""
    # type: (str) -> Dict[str, Any]
    with open(file_path) as f:
        return json.load(f)


def test_data_existence(server, data):
    """Function to generate the url to check the existence of the data."""
    # type: (str, str) -> str
    return server + "/data/" + data


def generate_url_plot(server, session_attr):
    """Function to generate the final url for the plot."""
    # type: (str, Dict[str, str]) -> str
    server += "genPlot/"
    for key, value in session_attr.items():
        server += ( key + "=" + value + "/" )
    return server


def eliminate_encodings(session_attr):
    """Function to eliminate all the encodings at once."""
    new_session_attr = {}
    for key, value in session_attr.items():
        if ((key == "data") | (key == "xvar") | (key == "yvar")):
            new_session_attr[key] = value
    return new_session_attr