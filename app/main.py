from flask import Flask, request, abort, send_from_directory, render_template
from sh import git
import os , logging , subprocess , shutil , json_file_builder
import boto3
from botocore.exceptions import ClientError

application = Flask(__name__, static_folder='md/static', template_folder='md')

@application.route('/') 
def index():
    return render_template('index.html')

@application.route('/static/<path:path>') 
def static_stuff(path):
    return send_from_directory('static', path)

@application.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST' and request.json is not None:
         
        s3 = boto3.client('s3')
        payload = request.json
        user_name = payload['repository']['owner']['username']
        repo_name = payload['repository']['name']
        repo_clone_url = payload['repository']['clone_url']
        return clone_and_check_repo(user_name,repo_name, repo_clone_url, s3)
    else:
        abort(400)

def upload_file(user_name, repo_name, suffix, s3):      
    localfilename = f'./{repo_name}{suffix}.json'
    remotefilename = f'{user_name}/{repo_name}{suffix}.json'
    bucket_name = 'test-repo-badges-bucket'
    
    try :
        response = s3.upload_file(localfilename, bucket_name, remotefilename, ExtraArgs={'ACL':'public-read'})
    
    except ClientError as e: 
        logging.error(e)

def clone_and_check_repo(user_name, repo_name, repo_clone_url, s3):
        has_manifest = False
        
        git.clone(repo_clone_url)
       
        processes = []
        outfiles = []
        for fname in os.listdir(f'./{repo_name}'):
            if fname.endswith('.usfm'):
                infile = repo_name + '/' + fname
                outfile = infile + "_out.json"
                proc = subprocess.Popen(["./usfmlinter/USFMLinter", "--input", infile, "--output", outfile])
                processes.append(proc)
                outfiles.append(outfile)

            if fname == 'manifest.json' or fname == 'manifest.yaml':
                has_manifest = True

        num_invalid_usfm = 0
        for proc, outfile in zip(processes, outfiles):
            proc.wait()
            with open(outfile, 'r') as f:
                result = f.read()
                if result != "[]":
                    num_invalid_usfm += 1

        print("# invalid USFM files = " + str(num_invalid_usfm))

        manifest_suffix = ""
        usfm_suffix = "_errors"

        json_file_builder.get_has_manifest(repo_name=repo_name,suffix=manifest_suffix,is_valid=has_manifest)
        json_file_builder.get_num_invalid_usfm(repo_name=repo_name,suffix=usfm_suffix,num_invalid=num_invalid_usfm)
        
        upload_file(user_name, repo_name, manifest_suffix, s3)
        upload_file(user_name, repo_name, usfm_suffix, s3)

        try: 
            shutil.rmtree(f'./{repo_name}')
            os.remove(f'./{repo_name}.json')
            os.remove(f'./{repo_name}_errors.json')
            
        except OSError as e:  ## if failed, report it back to the user ##
             print ("Error: %s - %s." % (e.filename, e.strerror))

        return str(has_manifest), 200


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=80)