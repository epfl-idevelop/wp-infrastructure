# Ensure that every languages has a menu located in "Top" location.
#  - if yes, do not touch anything (e.g. ic)
#  - if not, spread the jam in order that the site has a menu — it's most likely happening when creating a new site
#
# Quick test: ./wpsible -t wp.menus.polylang -l test_migration_wp__labs__bbb -e '{ "wp_destructive": { "test_migration_wp__labs__bbb" : ["config", "code"] }}'

import sys
import os
import json
from ansible.errors import AnsibleActionFail

# To be able to import wordpress_action_module
sys.path.append(os.path.dirname(__file__))
from wordpress_action_module import WordPressActionModule

class ActionModule(WordPressActionModule):

    MAIN_MENU = "Main"

    def run(self, tmp=None, task_vars=None):
        self.result = super(ActionModule, self).run(tmp, task_vars)
        desired_state = self._task.args.get('state', 'absent')
        if desired_state == "present":
            self.ensure_polylang_main_menu()
        return self.result

    def _menu_exists(self, menu_name):
        """
        Tells if a menu exists

        Keyword arguments
        menu_name -- menu name to check if exists
        """
        menu_list = self._get_wp_json("menu list --fields=name --format=json")
        # if no existing menus
        if not menu_list:
            return False
        # Looping through existing menus
        for existing_menu in menu_list:
            if existing_menu['name'] == menu_name:
                return True
        return False

    def ensure_polylang_main_menu(self):
        """
        Ensure that main menu exists
        """
        if not self._menu_exists(self.MAIN_MENU):
            self._run_wp_cli_action("pll menu create {} top".format(self.MAIN_MENU))
