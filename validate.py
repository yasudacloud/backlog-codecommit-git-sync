import os


def env_validate():
    required_env = [
        "GIT_FROM_REPO",
        "GIT_TO_REPO",
        "GIT_FROM_BRANCH",
        "GIT_TO_BRANCH",
        "GIT_TO_CLONE_PATH",
    ]
    for key in required_env:
        if os.environ.get(key) is None:
            print("@not found")
            print(key)
            raise EnvironmentError(f"Environment variables are not set: {key}")
    return
