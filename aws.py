import boto3

s3 = boto3.client('s3')

s3.upload_file('ski_resort_data_p1-7.csv', 'aicore-akirby')

# list_buckets returns a json file so there is a bit of digging in that's needed.
print(s3.list_buckets()["Buckets"][0]['Name'])