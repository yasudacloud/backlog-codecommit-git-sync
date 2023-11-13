import base64
import json
import os
import shutil
import urllib
import boto3
from pygit2 import clone_repository, RemoteCallbacks, UserPass, Signature
from validate import env_validate

secrets_manager = boto3.client('secretsmanager', region_name='ap-northeast-1')
resp = secrets_manager.get_secret_value(SecretId="git_credentials_secret")
secrets_info = json.loads(resp['SecretString'])

git_user = "automatic user"
git_email = "test@test.com"


def webhook(event, context):
    print(secrets_info)
    env_validate()

    body = base64.b64decode(event['body'])
    param = urllib.parse.parse_qs(body.decode("utf-8"))
    payload = json.loads(param['payload'][0])
    print("@backlog payload")
    print(payload)

    # Backlog
    from_repo_url = os.environ.get("GIT_FROM_REPO")
    from_branch = os.environ.get("GIT_FROM_BRANCH")

    # CodeCommit
    to_repo_url = os.environ.get("GIT_TO_REPO")
    to_clone_path = os.environ.get("GIT_TO_CLONE_PATH")
    to_branch = os.environ.get("GIT_TO_BRANCH")

    # webhookのパラメータのリポジトリURLとマージ予定のリポジトリURLが一致するか
    git_url = f"{payload['repository']['url']}.git"
    if git_url != from_repo_url:
        print(event)
        raise AttributeError("Bad Access")

    # 認証情報
    from_user_pass = UserPass(secrets_info["BACKLOG_USER"], secrets_info["BACKLOG_PASSWORD"])
    to_user_pass = UserPass(secrets_info["CODECOMMIT_USER"], secrets_info["CODECOMMIT_PASSWORD"])

    # git clone $url $path -b $branch
    to_repo = clone(to_repo_url, to_clone_path, to_branch, to_user_pass)

    # git remote add backlog $from_repo_url
    to_repo.remotes.create('backlog', from_repo_url)

    # Commit Message
    message = "auto merge"

    is_file_changed = merge_repositories(to_repo, from_user_pass, message)

    if is_file_changed:
        print("file changed")
        # push
        remote = to_repo.remotes["origin"]
        refspec = f'refs/heads/{from_branch}:refs/heads/{to_branch}'
        remote.push([refspec], callbacks=RemoteCallbacks(to_user_pass))
    else:
        print("file not changed")
    return {'hello': 'world'}


def merge_repositories(to_repo, from_user_pass, message):
    to_repo.remotes["backlog"].fetch(callbacks=RemoteCallbacks(from_user_pass))
    to_repo.merge(to_repo.branches["backlog/master"].target)

    # マージ後のツリーオブジェクトを取得
    merge_commit = to_repo.revparse_single("HEAD")
    merge_tree = merge_commit.tree

    # ツリーの差分を取得
    diff = to_repo.index.diff_to_tree(merge_tree)
    if diff.stats.files_changed == 0:
        return False

    tree = to_repo.index.write_tree()
    author = Signature(git_user, git_email)
    to_repo.create_commit(
        "HEAD",
        author,
        author,
        message,
        tree,
        [
            to_repo.head.target,
        ]
    )
    return True


# $GIT_TO_CLONE_PATH上に既にプロジェクトあれば削除する
# ストレージを永続化する場合はrmtreeを削除
def clone(url, path, branch, user_pass):
    if os.path.isdir(path):
        shutil.rmtree(path)
    repo = clone_repository(url, path, callbacks=RemoteCallbacks(user_pass),
                            checkout_branch=branch)
    return repo
