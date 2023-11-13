# backlog-codecommit-git-sync
## What is this repository?
Sample source code for synchronizing Backlog and CodeCommit Git repositories.
Specifically, when a Backlog file is changed, a Lambda is called and the diff file is pushed to CodeCommit.

This is simply implemented using Lambda, but it would be even better if combined with EFS and ChatBot.

This repository uses pygit2 and Serverless Framework. Sorry if it doesn't work properly.