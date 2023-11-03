import requests
import json
import subprocess
import os
import shutil
import time
from dateutil import parser
import zipfile

# https://api.github.com/repos/SagerNet/sing-box/commits

newest_commit = {}


def ReadNewestCommit():
    req = requests.get(
        "https://raw.githubusercontent.com/jimmyhuang454/sing-box-backup/HEAD/version.txt"
    )
    global newest_commit
    try:
        newest_commit = json.loads(req.content)
    except Exception as e:
        newest_commit = {}
    print(newest_commit)


def SaveNewestCommit():
    global newest_commit
    with open("./dist/version.txt", mode="w+") as f:
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


def ZipDir(dirpath, outFullName):
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dirpath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dirpath, '')

        for filename in filenames:
            zip.write(os.path.join(path, filename),
                      os.path.join(fpath, filename))
    zip.close()


def UpdateRepo(repo_name, commit_id):
    # clone new version
    cmd = "git clone git@github.com:%s.git" % repo_name
    name = "%s_%s" % (repo_name.replace("/", "_"), commit_id)
    new_dir = "./%s" % name
    os.makedirs(new_dir)
    subprocess.Popen(cmd, cwd=new_dir, shell=True).wait()
    newest_commit[repo_name] = commit_id
    ZipDir(new_dir, "./dist/" + name + ".zip")


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

SaveNewestCommit()
