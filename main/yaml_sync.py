#!/usr/bin/python
import copy
import sys
import re
import logging
from deepdiff import DeepDiff
from ordered_set import OrderedSet


class YamlSync:
    def __init__(self,
                 do_not_add_yaml: dict,
                 do_not_update_yaml: dict,
                 do_not_remove_yaml: dict,
                 verbose: bool):
        self.log = self.__get_logger('YamlSync', logging.DEBUG if verbose else logging.INFO)
        self.do_not_add_yaml = do_not_add_yaml
        self.do_not_update_yaml = do_not_update_yaml
        self.do_not_remove_yaml = do_not_remove_yaml

    def __get_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("[%(levelname)s| %(funcName)20s()] %(message)s"))
        return console_handler

    def __get_logger(self, logger_name, logging_level):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging_level)
        logger.addHandler(self.__get_console_handler())
        # with this pattern, it's rarely necessary to propagate the error up to parent
        logger.propagate = False
        return logger

    def is_yaml_field_exist(self, search_fields: list, yaml_data: dict):
        current_node = yaml_data
        for field in search_fields:
            self.log.debug('search field=%s, yaml_data=%s', field, yaml_data)
            found = current_node.get(field)
            if found is None:
                return False
            current_node = found
        return True

    def add_new_field(self, new_fields: list, target_yaml_data: dict, new_yaml_data: dict):
        if len(new_fields) == 0:
            return

        if self.is_yaml_field_exist(new_fields, self.do_not_add_yaml):
            return

        new_current_node = new_yaml_data
        target_current_node = target_yaml_data
        for field in new_fields:
            self.log.debug('search field=%s', field)
            self.log.debug('new_yaml_current_node=%s', new_current_node)
            self.log.debug('target_current_node=%s', target_current_node)
            found_new = new_current_node.get(field)
            found_target = target_current_node.get(field)
            self.log.debug('Found new field= %s and target field=%s', found_new, found_target)
            if found_new is None:
                self.log.error("Unable to find the new field with key=%s", field)
                return
            if found_target is None:
                target_current_node[field] = found_new
                return
            new_current_node = found_new
            target_current_node = found_target

    def process_added_fields(self, current_yaml_data: dict, added_fields: OrderedSet, new_yaml_data: dict):
        self.log.debug("added_fields=%s", added_fields)
        if added_fields is None:
            return
        for added_field in added_fields:
            self.log.debug("added_field=%s", added_field)
            tokens = re.findall(r"\['([^'\[\]]*)'\]", added_field)
            self.add_new_field(tokens, current_yaml_data, new_yaml_data)

    def update_existing_field(self, updated_fields: list, target_yaml_data: dict, new_yaml_data: dict):
        if len(updated_fields) == 0:
            return

        if self.is_yaml_field_exist(updated_fields, self.do_not_update_yaml):
            return

        new_current_node = new_yaml_data
        target_current_node = target_yaml_data
        for field in updated_fields[:-1]:
            self.log.debug('update field=%s', field)
            self.log.debug('new_yaml_current_node=%s', new_current_node)
            self.log.debug('target_current_node=%s', target_current_node)
            found_new = new_current_node.get(field)
            found_target = target_current_node.get(field)
            self.log.debug('Found update field= %s and target field=%s', found_new, found_target)
            if found_new is None:
                self.log.error("Unable to find the updated field with key=%s", field)
                return
            if found_target is None:
                self.log.error("Unable to find target update field with key=%s", field)
                return
            new_current_node = found_new
            target_current_node = found_target
        target_current_node[updated_fields[-1]] = new_current_node[updated_fields[-1]]

    def process_updated_fields(self, current_yaml_data: dict, updated_fields: OrderedSet, new_yaml_data: dict):
        if updated_fields is None:
            return
        for field in updated_fields:
            tokens = re.findall(r"\['([^'\[\]]*)'\]", field)
            self.update_existing_field(tokens, current_yaml_data, new_yaml_data)

    def remove_fields(self, removed_fields: list, target_yaml_data: dict):
        if len(removed_fields) == 0:
            return

        target_current_node = target_yaml_data
        for field in removed_fields[:-1]:
            self.log.debug('removal field=%s', field)
            self.log.debug('target_current_node=%s', target_current_node)
            found_target = target_current_node.get(field)
            self.log.debug('Found target field=%s', found_target)
            if found_target is None:
                print("Unable to find target removed field with key=%s", field)
                return
            target_current_node = found_target
        self.log.debug('target_current_node=%s', target_current_node)
        del target_current_node[removed_fields[-1]]

        add_back_current_node = self.do_not_remove_yaml
        target_current_node = target_yaml_data
        for field in removed_fields:
            self.log.debug('add back field=%s', field)
            self.log.debug('target_current_node=%s', target_current_node)
            found_add_back = add_back_current_node.get(field)
            found_target = target_current_node.get(field)
            self.log.debug('Found add back field=%s, target=%s', found_add_back, found_target)
            if found_add_back is None:
                self.log.debug('No addFound update field= %s and target field=%s', found_add_back, found_target)
                return
            if found_target is None:
                target_current_node[field] = found_add_back
                return
            add_back_current_node = found_add_back
            target_current_node = found_target

    def process_removed_fields(self, current_yaml_data: dict, removed_fields: OrderedSet):
        if removed_fields is None:
            return
        for field in removed_fields:
            tokens = re.findall(r"\['([^'\[\]]*)'\]", field)
            self.remove_fields(tokens, current_yaml_data)

    def sync(self, current_yaml: dict, new_yaml: dict):
        updated_yaml = copy.deepcopy(current_yaml)
        diff = DeepDiff(updated_yaml, new_yaml, ignore_order=True)
        self.process_added_fields(updated_yaml, diff.get('dictionary_item_added'), new_yaml)
        self.process_updated_fields(updated_yaml, diff.get('type_changes'), new_yaml)
        self.process_updated_fields(updated_yaml, diff.get('values_changed'), new_yaml)
        self.log.debug("Before process removed files=%s", updated_yaml)
        self.process_removed_fields(updated_yaml, diff.get('dictionary_item_removed'))
        return updated_yaml

