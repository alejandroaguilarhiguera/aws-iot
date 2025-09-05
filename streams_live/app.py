import json
import boto3
import os

def lambda_handler(event, context):
    stream_name = event.get("queryStringParameters", {}).get("streamName")

    if not stream_name:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Falta el parámetro streamName"})
        }

    try:
        kvs = boto3.client("kinesisvideo", region_name=os.environ.get("AWS_REGION", "us-east-1"))
        endpoint = kvs.get_data_endpoint(
            APIName="GET_HLS_STREAMING_SESSION_URL",
            StreamName=stream_name
        )["DataEndpoint"]

        kvs_media = boto3.client("kinesis-video-archived-media", endpoint_url=endpoint)

        response = kvs_media.get_hls_streaming_session_url(
            StreamName=stream_name,
            PlaybackMode="LIVE",
            HLSFragmentSelector={
                # "FragmentSelectorType": "PRODUCER_TIMESTAMP"
                "FragmentSelectorType": "SERVER_TIMESTAMP"
            }
        )

        url = response.get("HLSStreamingSessionURL")

        if not url:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "No se pudo obtener la URL HLS. Verifica que el stream tiene un productor enviando video."})
            }

        return {
            "statusCode": 200,
            "body": json.dumps({"url": url})
        }

    except Exception as e:
        print("Error en Lambda:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }