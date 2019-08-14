from flask import Flask, request, abort
import json
import boto3 

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST' and request.json is not None:
        s3 = boto3.client('s3')
        localfilename = '/webhooks/testfile.json'
        remotefilename = 'webhooks/testfile.json'
        bucket_name = 'test-repo-badges-bucket'
        s3.upload_file(localfilename, bucket_name, remotefilename)
        return 'I did the thing', 200
    else:
        abort(400)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

