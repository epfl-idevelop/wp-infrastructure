# -*- coding: utf-8 -*-

# There is a name clash with a module in Ansible named "copy":
deepcopy = __import__('copy').deepcopy
import re
import sys
import os.path
import json

# To be able to import wordpress_action_module
sys.path.append(os.path.dirname(__file__))

from wordpress_action_module import WordPressPluginOrThemeActionModule

class ActionModule(WordPressPluginOrThemeActionModule):
    def run (self, tmp=None, task_vars=None):

        self.result = super(ActionModule, self).run(tmp, task_vars)

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
            self._do_deactivate_plugin()

        if desired_installation_state:
            # Setting desired installation state
            self._ensure_all_files_state(desired_installation_state)

        if (
                not self._is_mandatory() and
                bool(desired_activation_state) and
                'active' in set([desired_activation_state]) - set([current_activation_state])
        ):
            self._do_activate_element()

        return self.result

    def _ensure_all_files_state (self, desired_state):
        """Overridden to try with `wp plugin delete` first."""
        # First try to use wp-cli to uninstall:
        if desired_state == 'absent' and not self._is_check_mode():
            orig_changed = self.result.get('changed', False)
            self._run_wp_cli_change('plugin delete {}'.format(self._task.args.get('name')))
            if ("Plugin already deleted" in self.result["stdout"]
                or "could not be found" in self.result["stdout"]):
                self.result['changed'] = orig_changed

        super(ActionModule, self)._ensure_all_files_state(desired_state)


    def _do_deactivate_plugin (self):
        """
        Uses WP-CLI to deactivate plugin
        """
        return self._run_wp_cli_change('plugin deactivate {}'.format(self._get_name()))


