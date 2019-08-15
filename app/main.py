from flask import Flask, request, abort
from sh import git
import os , logging , shutil , json_file_builder
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST' and request.json is not None:
         
        s3 = boto3.client('s3')
        payload = request.json
        user_name = payload['repository']['owner']['username']
        repo_name = payload['repository']['name']
        repo_clone_url = payload['repository']['clone_url']
        valid = False
        
        git.clone(repo_clone_url)
       
        for fname in os.listdir(f'./{repo_name}'):
            if fname == 'manifest.json' or fname == 'manifest.yaml':
                valid = True
                break
            
        json_file_builder.get(repo_name=repo_name,is_valid=valid)
        
        localfilename = f'./{repo_name}.json'
        remotefilename = f'{user_name}/{repo_name}.json'
        bucket_name = 'test-repo-badges-bucket'
        
        try :
            response = s3.upload_file(localfilename, bucket_name, remotefilename, ExtraArgs={'ACL':'public-read'})
        
        except ClientError as e: 
            logging.error(e)
        
        try: 
            shutil.rmtree(f'./{repo_name}')
            os.remove(f'./{repo_name}.json')
            
        except OSError as e:  ## if failed, report it back to the user ##
             print ("Error: %s - %s." % (e.filename, e.strerror))


        return str(valid), 200
    else:
        abort(400)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=443)
