import base64
import json
import os
import urllib
from handler import webhook

# TODO: ローカル環境でこのファイルを実行する場合はwebhook()を呼び出す前に環境変数をセットする
# 必要な環境変数はvalidate.pyに記載
# Backlogのwebhook仕様に合わせて加工して引数で渡す
json = json.dumps({
    "repository": {
        "url": os.environ.get("GIT_FROM_REPO").replace(".git", "")
    }})
encoded = urllib.parse.urlencode({
    "payload": json
})

# Calling a Lambda function
webhook({
    "body": base64.b64encode(
        str.encode(encoded)
    )
}, {})
