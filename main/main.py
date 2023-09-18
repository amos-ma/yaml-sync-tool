import argparse
import yaml
from yaml_sync import YamlSync


def load_yaml(filename):
    with open(filename) as f:
        yaml_data = yaml.load(f, Loader=yaml.FullLoader)
    return yaml_data


parser = argparse.ArgumentParser(description='Diff YAML for sync purpose')
parser.add_argument('--verbose', '-v', action='count', default=0)
parser.add_argument('--current_yaml_file', default='current.yaml', help='The current YAML file')
parser.add_argument('--new_yaml_file', default='new.yaml', help='The new YAML file', )
parser.add_argument('--do_not_add_file', default='do_not_add.yaml',
                    help='The YAML file contains do not add config fields and values')
parser.add_argument('--do_not_remove_file', default='do_not_remove.yaml',
                    help='The YAML file contains do not remove config fields and values')
parser.add_argument('--do_not_update_file', default='do_not_update.yaml',
                    help='The YAML file contains do not update config fields and values')
parser.add_argument('--generated_yaml_file', default='output.yaml',
                    help='The YAML file contains latest fields and values')

parser.add_argument('--data_location', default='data',
                    help='The YAML file contains latest fields and values')

args = parser.parse_args()

do_not_add_yaml = load_yaml(args.data_location + '/' + args.do_not_add_file)
do_not_update_yaml = load_yaml(args.data_location + '/' + args.do_not_update_file)
do_not_remove_yaml = load_yaml(args.data_location + '/' + args.do_not_remove_file)

current_yaml = load_yaml(args.data_location + '/' + args.current_yaml_file)
new_yaml = load_yaml(args.data_location + '/' + args.new_yaml_file)
yaml_sync = YamlSync(do_not_add_yaml, do_not_update_yaml, do_not_remove_yaml, True)
updated_yaml = yaml_sync.sync(current_yaml, new_yaml)
yaml_output_stream = open(args.data_location + '/' + args.generated_yaml_file, 'w')
yaml.dump(updated_yaml, yaml_output_stream)
