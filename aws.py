import boto3

s3 = boto3.client('s3')

#s3.download_file('aicore-akirby', '320-SUNPORT-SPP300-320M60C.pdf','320-SUNPORT-SPP300-320M60C.pdf')

# list_buckets returns a json file so there is a bit of digging in that's needed.
print(s3.list_buckets()["Buckets"][0]['Name'])