import yaml

with open("states/front_to_back.yaml", "r") as file:
    try:
        content = yaml.safe_load(file)
        print(content['text'])
        print('\u2709')
    except yaml.YAMLError as exc:
        print(exc)

with open("states/front_to_back.yaml", "w") as file:
    try:
        content['text'] += 'abds\u2709'
        yaml.dump(content, file)
    except yaml.YAMLError as exc:
        print(exc)