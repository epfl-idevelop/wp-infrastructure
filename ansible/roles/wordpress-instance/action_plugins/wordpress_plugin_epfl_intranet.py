import sys
import os.path

# There is a name clash with a module in Ansible named "copy":
deepcopy = __import__('copy').deepcopy

# To be able to include package wp_inventory in parent directory
sys.path.append(os.path.dirname(__file__))

from wordpress_action_module import WordPressActionModule


class ActionModule(WordPressActionModule):
    def run(self, tmp=None, task_vars=None):
        
        self.result = super(ActionModule, self).run(tmp, task_vars)

        # We only can do the job if plugin is installed
        if self._plugin_is_installed():

            self._set_protection_state()

        return self.result
    

    def _plugin_is_installed(self):
        """
        Tells if the plugin is installed
        """

        result = self._run_wp_cli_action("plugin list --format=csv", update_result=False)

        for line in result['stdout_lines'][1:]:
            fields = line.split(',')
            if len(fields) < 2: continue

            if fields[0] == 'epfl-intranet': 
                return True

        return False

    def _set_protection_state(self):
        """
        Set correct protection state for plugin
        """

        result = self._run_wp_cli_action("epfl intranet status", update_result=False)

        if 'failed' in self.result: return

        # Getting parameters
        protection_enabled = self._task.args.get('protection_enabled').strip().lower() == 'yes'
        restrict_to_groups = str(self._task.args.get('restrict_to_groups')).strip()

        # If protection needs to be enabled
        if protection_enabled:

            # If protection is disabled or group restriction is not correct
            if 'is disabled' in result['stdout'] or (restrict_to_groups != "" and not result["stdout"].endswith(restrict_to_groups)):

                # Creating restriction option
                restrict_to_groups_opt = "--restrict-to-groups={}".format(restrict_to_groups) if restrict_to_groups != "" else ""

                wpcli_command = "epfl intranet enable-protection {}".format(restrict_to_groups_opt)
                #self._update_result(self._run_wp_cli_action(wpcli_command))
                self._run_wp_cli_action(wpcli_command)
        
        # Protection needs to be disabled
        else:
            
            if 'is enabled' in result['stdout']:
                
                wpcli_command = "epfl intranet disable-protection"
                self._run_wp_cli_action(wpcli_command)