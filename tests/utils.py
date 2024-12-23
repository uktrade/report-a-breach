import boto3


def delete_all_bucket_files(bucket_name: str):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.all():
        obj.delete()

    yield

    for obj in bucket.objects.all():
        obj.delete()
