# -*- coding: utf-8 -*-

# There is a name clash with a module in Ansible named "copy":
deepcopy = __import__('copy').deepcopy
import re
import sys
import os.path
import json

# To be able to include package wp_inventory in parent directory
sys.path.append(os.path.dirname(__file__))

from ansible.errors import AnsibleActionFail
from ansible.module_utils import six
from wordpress_action_module import WordPressActionModule

class ActionModule(WordPressActionModule):
    def run (self, tmp=None, task_vars=None):

        self.result = super(ActionModule, self).run(tmp, task_vars)
        
        # Handling --check execution mode
        if task_vars['ansible_check_mode']:
            self.result['skipped'] = True
            return self.result

        self._name = self._task.args.get('name')
        self._mandatory = self._task.args.get('is_mu', False)
        self._type = 'mu-plugin' if self._task.args.get('is_mu', False) else 'plugin'

        current_activation_state = self._get_activation_state()
        (desired_installation_state,
         desired_activation_state) = self._get_desired_state()

        if (
                bool(desired_activation_state) and
                'active' in set([current_activation_state]) - set([desired_activation_state])
        ):
            self._update_result(self._do_deactivate_plugin())
            if 'failed' in self.result: return self.result

        if desired_installation_state:
            # Setting desired installation state
            self._ensure_all_files_state(desired_installation_state)
            if 'failed' in self.result: return self.result

        if (
                not self._is_mandatory() and
                bool(desired_activation_state) and
                'active' in set([desired_activation_state]) - set([current_activation_state])
        ):
            
            
            self._do_activate_element()
            if 'failed' in self.result: return self.result

        return self.result


    def _do_deactivate_plugin (self):
        """
        Uses WP-CLI to deactivate plugin
        """
        return self._run_wp_cli_action('plugin deactivate {}'.format(self._get_name()))

