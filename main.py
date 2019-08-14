from flask import Flask, request, abort
from sh import git
import os
import shutil
import json_file_builder

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        payload = request.json
        repo_name = payload['repository']['name']
        repo_clone_url = payload['repository']['clone_url']
        valid = False
        
        git.clone(repo_clone_url)
       
        for fname in os.listdir(f'./{repo_name}'):
            if fname == 'manifest.json' or fname == 'manifest.yaml':
                valid = True
                break

        json_file = json_file_builder.get(repo_name, valid)
        print(json_file)
        
        try: 
            shutil.rmtree(f'./{repo_name}')
            
        except OSError as e:  ## if failed, report it back to the user ##
             print ("Error: %s - %s." % (e.filename, e.strerror))


        return str(valid), 200
    else:
        abort(400)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
