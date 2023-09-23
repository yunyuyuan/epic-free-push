import requests
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='restore or save gist')
    parser.add_argument('--restore', default=False, action="store_true", help='is restore?')
    parser.add_argument('--save', default=False, action="store_true", help='is save?')
    parser.add_argument('--token', type=str, required=True, help='github token')
    parser.add_argument('--id', type=str, required=True, help='gist id')
    parser.add_argument('--owner', type=str, required=True, help='gist owner')
    args = parser.parse_args()
    
    if args.save:
        with open("passed.json", "r", encoding="utf-8") as fp:
            passed = fp.read()
            resp = requests.get(f'https://gist.githubusercontent.com/{args.owner}/{args.id}/raw/passed.json')
            if passed == resp.text:
                print("no need to update")
                exit()
            resp = requests.patch(f'https://api.github.com/gists/{args.id}', json={
                "files": {
                    "passed.json": { "content": passed }
                }
            }
            , headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f'Bearer {args.token}',
                "X-GitHub-Api-Version": "2022-11-28"
            })
            if resp.ok:
                print("gist saved!")
            else:
                print("Error: ", resp.text)
    else:
        resp = requests.get(f'https://gist.githubusercontent.com/{args.owner}/{args.id}/raw/passed.json')
        with open("passed.json", "w", encoding="utf-8") as fp:
            fp.write(resp.text)
            print("passed.json restored!")
    