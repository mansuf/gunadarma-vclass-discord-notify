import subprocess
import argparse
import secrets

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--daemon', action='store_true')
args = parser.parse_args()

random_char = secrets.token_hex(5)
name = 'ia24-assigments-bot'
container_name = f'{name}-{random_char}'

docker_args = [
    'docker',
    'run',
    '--name',
    container_name
]

if args.daemon:
    docker_args.append('-d')

# image name
docker_args.append(name)

app_args = [
    'python3',
    'start.py',
]

subprocess.run(docker_args + app_args)