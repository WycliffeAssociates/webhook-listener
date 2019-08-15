from flask import Flask, request, abort
from sh import git
import os
import shutil
import subprocess
import json_file_builder

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        payload = request.json
        repo_name = payload['repository']['name']
        repo_clone_url = payload['repository']['clone_url']
        return clone_and_check_repo(repo_name, repo_clone_url)
    else:
        abort(400)

def clone_and_check_repo(repo_name, repo_clone_url):
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

        has_manifest_json_file = json_file_builder.get_has_manifest(repo_name, has_manifest)
        num_invalid_usfm_json_file = json_file_builder.get_num_invalid_usfm(repo_name, num_invalid_usfm)
        
        try: 
            shutil.rmtree(f'./{repo_name}')
            
        except OSError as e:  ## if failed, report it back to the user ##
             print ("Error: %s - %s." % (e.filename, e.strerror))

        return str(has_manifest), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
