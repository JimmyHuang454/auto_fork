import requests
import json
import subprocess
import os
import shutil
import time
from dateutil import parser

# https://api.github.com/repos/SagerNet/sing-box/commits

newest_commit = {}


def ReadNewestCommit():
    path = "./version.txt"
    if not os.path.exists(path):
        content = "{}"
    else:
        with open("./version.txt", mode="r+") as f:
            content = f.read()
            if content == "":
                content = "{}"
        f.close()
    global newest_commit
    newest_commit = json.loads(content)
    print(newest_commit)


def SaveNewestCommit():
    global newest_commit
    with open("./version.txt", mode="w+") as f:
        f.write(json.dumps(newest_commit))


def GetRepoNewestCommit(repo_name):
    req = requests.get("https://api.github.com/repos/%s/commits" % repo_name)
    try:
        res = json.loads(req.content)
        str_time = res[0]["commit"]["author"]['date']
        return int(parser.parse(str_time).timestamp())
    except Exception as e:
        print(e)
        return


def GetRepoCurrentCommit(repo_name):
    if repo_name not in newest_commit:
        return 0
    return newest_commit[repo_name]


def UpdateRepo(repo_name, commit_id):
    # clone new version
    cmd = "git clone git@github.com:%s.git" % repo_name
    new_dir = "./%s_%s" % (repo_name.replace("/", "_"), commit_id)
    os.makedirs(new_dir)
    subprocess.Popen(cmd, cwd=new_dir, shell=True).wait()
    newest_commit[repo_name] = commit_id

    # delete old version
    if repo_name in newest_commit:
        old_dir = "./%s_%s" % (repo_name.replace(
            "/", "_"), newest_commit[repo_name])
        if os.path.exists(old_dir) and os.path.getsize(
                old_dir) < os.path.getsize(new_dir):
            print("deleted " + old_dir)
            shutil.rmtree(old_dir)


def GetProjectRepoList(project_name):
    req = requests.get("https://api.github.com/orgs/%s/repos" % project_name)
    try:
        res = json.loads(req.content)
        return res
    except Exception as e:
        print(e)
        return


ReadNewestCommit()

sing_box_list = GetProjectRepoList("SagerNet")

save_repo_list = []
for item in sing_box_list:
    save_repo_list.append(item['full_name'])

i = 0
for item in save_repo_list:
    n = GetRepoNewestCommit(item)
    if n > GetRepoCurrentCommit(item):
        print("updating %s." % item)
        UpdateRepo(item, n)
    else:
        print("%s not need to update." % item)
    i += 1
    if i > 10:
        break

SaveNewestCommit()
