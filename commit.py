import dateutil.parser
import requests
import argparse
import datetime
import dateutil
import base64


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='create a dummy commit')
    parser.add_argument('--token', type=str, required=True, help='github token')
    parser.add_argument('--repo', type=str, required=True, help='repo name with owner (owner/repo)')
    parser.add_argument('--branch', type=str, required=True, help='branch name')
    args = parser.parse_args()

    [owner, repo] = args.repo.split("/")

    resp = requests.post(f'https://api.github.com/graphql', json={
        "query": '''query {
    viewer {
      login
    }
    repository(name: "'''+repo+'", owner: "'+owner+'''") {
      defaultBranchRef {
        target {
          ... on Commit {
            history(first: 1) {
              nodes {
                oid
                committedDate
              }
            }
          }
        }
      }
    }
  }'''
    }
    , headers={
        "Authorization": f'Bearer {args.token}',
    })
    data = resp.json()['data']['repository']['defaultBranchRef']["target"]['history']['nodes'][0]
    sha = data['oid']
    lastCommitTime = dateutil.parser.parse(data['committedDate'])
    nowTimestamp = datetime.datetime.now().timestamp()
    if (nowTimestamp - lastCommitTime.timestamp())/(3600*24) > 50:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        resp = requests.post(f'https://api.github.com/graphql', json={
            "query": '''mutation {
        createCommitOnBranch(
        input: {
            branch: {
            branchName: "'''+args.branch+'''",
            repositoryNameWithOwner: "'''+args.repo+'''"
            },
            message: {
            headline: "['''+now+'''] update CHANGELOG"
            },
            expectedHeadOid: "'''+sha+'''",
            fileChanges: {
            additions: [{path: "CHANGELOG.md",contents: "'''+base64.b64encode(now.encode('ascii')).decode('ascii')+'''"}]
            }
        }
        ) {
        clientMutationId
        }
    }'''
        }
        , headers={
            "Authorization": f'Bearer {args.token}',
        })
        if resp.ok:
            print("commit created!")
        else:
            print("Error: ", resp.text)
    else:
        print("no need to update")