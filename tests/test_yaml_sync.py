import unittest

import yaml

from main.yaml_sync import YamlSync
from ordered_set import OrderedSet


def load_yaml(filename):
    with open(filename) as f:
        yaml_data = yaml.load(f, Loader=yaml.FullLoader)
    return yaml_data


class TesIYamlSync(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('Setup')
        cls.do_not_add_yaml = load_yaml('data/do_not_add.yaml')
        cls.do_not_update_yaml = load_yaml('data/do_not_update.yaml')
        cls.do_not_remove_yaml = load_yaml('data/do_not_remove.yaml')
        cls.current_yaml = load_yaml('data/current.yaml')
        cls.new_yaml = load_yaml('data/new.yaml')

    @classmethod
    def tearDownClass(cls):
        print('Teardown')

    def test_is_yaml_field_exist(self):
        yaml_sync = YamlSync(self.do_not_add_yaml, self.do_not_update_yaml, self.do_not_remove_yaml, True)
        actual = yaml_sync.is_yaml_field_exist(['section6','level6'], self.do_not_add_yaml)
        self.assertTrue(actual)
        actual = yaml_sync.is_yaml_field_exist(['section6','level_not_exist'], self.do_not_add_yaml)
        self.assertFalse(actual)

    def test_add_new_field__added_at_root_node(self):
        yaml_sync = YamlSync(self.do_not_add_yaml, self.do_not_update_yaml, self.do_not_remove_yaml, True)
        new_yaml = {'section7': {'level8': 23}}
        target_yaml = {'section6': {'level9': 24}}
        expect = {'section6': {'level9': 24}, 'section7': {'level8': 23}}
        yaml_sync.add_new_field(['section7'], target_yaml, new_yaml)
        self.assertEqual(expect, target_yaml)

    def test_add_new_field__added_at_sub_node(self):
        yaml_sync = YamlSync(self.do_not_add_yaml, self.do_not_update_yaml, self.do_not_remove_yaml, True)
        new_yaml = {'section6': {'level8': 23}}
        target_yaml = {'section6': {'level9': 24}}
        expect = {'section6': {'level8': 23, 'level9': 24}}
        yaml_sync.add_new_field(['section6','level8'], target_yaml, new_yaml)
        self.assertEqual(expect, target_yaml)

    def test_add_new_field__skip_due_to_do_not_add(self):
        yaml_sync = YamlSync(self.do_not_add_yaml, self.do_not_update_yaml, self.do_not_remove_yaml, True)
        new_yaml = {'section6': {'level6': 23}}
        target_yaml = {'section6': {'level9': 24}}
        expect = {'section6': {'level9': 24}}
        yaml_sync.add_new_field(['section6','level6'], target_yaml, new_yaml)
        self.assertEqual(expect, target_yaml)

    def test_process_added_fields__added_at_root_node(self):
        yaml_sync = YamlSync(self.do_not_add_yaml, self.do_not_update_yaml, self.do_not_remove_yaml, True)
        new_yaml = {'section7': {'level8': 23}, 'section9': {'level9': 24}}
        target_yaml = {'section6': {'level9': 24}}
        expect = {'section6': {'level9': 24}, 'section7': {'level8': 23}, 'section9': {'level9': 24}}
        yaml_sync.process_added_fields(target_yaml, OrderedSet(["root['section7']", "root['section9']"]), new_yaml)
        self.assertEqual(expect, target_yaml)

    def test_process_added_fields__added_at_sub_node(self):
        yaml_sync = YamlSync(self.do_not_add_yaml, self.do_not_update_yaml, self.do_not_remove_yaml, True)
        new_yaml = {'section6': {'level8': 23, 'level8a': 23}}
        target_yaml = {'section6': {'level9': 24}}
        expect = {'section6': {'level8': 23, 'level8a': 23, 'level9': 24}}
        yaml_sync.process_added_fields(target_yaml, OrderedSet(["root['section6']['level8']", "root['section6']['level8a']"]), new_yaml)
        self.assertEqual(expect, target_yaml)

    def test_process_added_fields__skip_due_to_do_not_add(self):
        yaml_sync = YamlSync(self.do_not_add_yaml, self.do_not_update_yaml, self.do_not_remove_yaml, True)
        new_yaml = {'section6': {'level6': 23}}
        target_yaml = {'section6': {'level9': 24}}
        expect = {'section6': {'level9': 24}}
        yaml_sync.process_added_fields(target_yaml, OrderedSet(["root['section6']['level6']"]), new_yaml)
        self.assertEqual(expect, target_yaml)

    def test_update_existing_field__update_at_sub_node(self):
        yaml_sync = YamlSync(self.do_not_add_yaml, self.do_not_update_yaml, self.do_not_remove_yaml, True)
        new_yaml = {'section6': {'level9': 28}}
        target_yaml = {'section6': {'level9': 24}}
        expect = {'section6': {'level9': 28}}
        yaml_sync.update_existing_field(['section6','level9'], target_yaml, new_yaml)
        self.assertEqual(expect, target_yaml)

    def test_update_existing_field__skip_update_due_do_not_update_list(self):
        yaml_sync = YamlSync(self.do_not_add_yaml, self.do_not_update_yaml, self.do_not_remove_yaml, True)
        new_yaml = {'section8': {'level8a': 28}}
        target_yaml = {'section8': {'level8a': 24}}
        expect = {'section8': {'level8a': 24}}
        yaml_sync.update_existing_field(['section8','level8a'], target_yaml, new_yaml)
        self.assertEqual(expect, target_yaml)

    def test_process_updated_fields_skip_update_due_do_not_update_list(self):
        yaml_sync = YamlSync(self.do_not_add_yaml, self.do_not_update_yaml, self.do_not_remove_yaml, True)
        new_yaml = {'section8': {'level8a': 25}, 'section9': {'level9': 27}}
        target_yaml = {'section8': {'level8a': 24}, 'section9': {'level9': 26}}
        expect = {'section8': {'level8a': 24}, 'section9': {'level9': 27}}
        yaml_sync.process_updated_fields(target_yaml, OrderedSet(["root['section8']['level8a']", "root['section9']['level9']"]), new_yaml)
        self.assertEqual(expect, target_yaml)

    def test_remove_fields__remove_at_sub_node(self):
        yaml_sync = YamlSync(self.do_not_add_yaml, self.do_not_update_yaml, self.do_not_remove_yaml, True)
        target_yaml = {'section6': {'level9': 24, 'level9a': 25}}
        expect = {'section6': {'level9a': 25}}
        yaml_sync.remove_fields(['section6','level9'], target_yaml)
        self.assertEqual(expect, target_yaml)

    def test_remove_fields__remove_at_root_node(self):
        yaml_sync = YamlSync(self.do_not_add_yaml, self.do_not_update_yaml, self.do_not_remove_yaml, True)
        target_yaml = {'section6': {'level9': 24, 'level9a': 25}, 'section7': {'level7': 25, 'level7a': 26}}
        expect = {'section7': {'level7': 25, 'level7a': 26}}
        yaml_sync.remove_fields(['section6'], target_yaml)
        self.assertEqual(expect, target_yaml)

    def test_remove_fields__skip_due_to_do_not_remove_list(self):
        yaml_sync = YamlSync(self.do_not_add_yaml, self.do_not_update_yaml, self.do_not_remove_yaml, True)
        target_yaml = {'section9': {'level9': 24, 'level9a': 25}}
        expect = {'section9': {'level9': 24, 'level9a': '9a'}}
        yaml_sync.remove_fields(['section9','level9a'], target_yaml)
        self.assertEqual(expect, target_yaml)

    def test_process_removed_fields_at_sub_node(self):
        yaml_sync = YamlSync(self.do_not_add_yaml, self.do_not_update_yaml, self.do_not_remove_yaml, True)
        target_yaml = {'section6': {'level9': 24, 'level9a': 25}}
        expect = {'section6': {'level9a': 25}}
        yaml_sync.process_removed_fields(target_yaml, OrderedSet(["root['section6']['level9']"]))
        self.assertEqual(expect, target_yaml)

    def test_process_removed_fields__remove_at_root_node(self):
        yaml_sync = YamlSync(self.do_not_add_yaml, self.do_not_update_yaml, self.do_not_remove_yaml, True)
        target_yaml = {'section6': {'level9': 24, 'level9a': 25}, 'section7': {'level7': 25, 'level7a': 26}}
        expect = {'section7': {'level7': 25, 'level7a': 26}}
        yaml_sync.process_removed_fields(target_yaml, OrderedSet(["root['section6']"]))
        self.assertEqual(expect, target_yaml)
