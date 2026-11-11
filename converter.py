import os
import boto3
from urllib.parse import unquote_plus
from PIL import Image

s3_client = boto3.client('s3')

DEST_BUCKET = os.environ.get('DEST_BUCKET')

def lambda_handler(event, context):
    for record in event.get('Records', []):
        source_bucket = record['s3']['bucket']['name']
        object_key = unquote_plus(record['s3']['object']['key'])

        download_path = f"/tmp/{os.path.basename(object_key)}"
        base_name, _ = os.path.splitext(os.path.basename(object_key))
        converted_filename = f"{base_name}.webp"
        upload_path = f"/tmp/{converted_filename}"

        try:
            print(f"Downloading {object_key} from {source_bucket}...")
            s3_client.download_file(source_bucket, object_key, download_path)

            with Image.open(download_path) as img:
                img.save(upload_path, 'WEBP', quality=85)

            print(f"Uploading {converted_filename} to {DEST_BUCKET}...")
            s3_client.upload_file(upload_path, DEST_BUCKET, converted_filename)

            print(f"Successfully converted and uploaded {converted_filename}")

        except Exception as e:
            print(f"Error converting file {object_key}: {str(e)}")
            raise e
        finally:
            for path in [download_path, upload_path]:
                if os.path.exists(path):
                    os.remove(path)

    return {"statusCode": 200, "body": "Conversion completed"}