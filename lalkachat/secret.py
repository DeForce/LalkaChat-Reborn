import yaml

with open('secrets.yaml', 'r') as secret_file:
    data = yaml.safe_load(secret_file.read())

    TWITCH_CLIENT_ID = data['twitch']['clientid']
