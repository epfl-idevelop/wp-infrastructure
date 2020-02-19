
# There is a name clash with a module in Ansible named "copy":
deepcopy = __import__('copy').deepcopy

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleActionFail
from ansible.module_utils import six

import re

class WordPressActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):

        self._tmp = tmp
        self._task_vars = task_vars
        # Has to be set in child classes with one of the following value:
        # plugin
        # mu-plugin
        # theme
        self._type = None
        # Has to be set with element name in child class
        self._name = None


        return super(WordPressActionModule, self).run(tmp, task_vars)

    @property
    def type(self):
        """
        Return element type or raise an exception if not initialized
        """
        if not self._type:
            raise ValueError("Please initiliaze 'self._type' in children class {}".format(type(self).__name__))
            
        return self._type

    @property
    def name(self):
        """
        Return element name or raise an exception if not initialized
        """
        if not self._name:
            raise ValueError("Please initiliaze 'self._name' in children class {}".format(type(self).__name__))
            
        return self._name
    

    def _get_desired_state(self):
        """
        Returns array with installation state and activation state for a (mu-)plugin.
        We look into YAML given args (plugins.yml)
        """
        desired_state = self._task.args.get('state', 'absent')
        if isinstance(desired_state, six.string_types):
             desired_state = set([desired_state.strip()])
        elif isinstance(desired_state, list):
            desired_state = set(desired_state)
        else:
            raise TypeError("Unexpected value for `state`: %s" % desired_state)

        if 'symlinked' in desired_state and 'installed' in desired_state:
            raise ValueError('% %s cannot be both `symlinked` and `installed`' % self.type, self.name)

        installation_state = self._installation_state(desired_state)
        activation_state = self._activation_state(desired_state)

        if installation_state == 'absent' and (activation_state == 'active' or self._is_mu):
            raise ValueError('%s %s cannot be simultaneously absent and %s' %
                             self.type, self.name, activation_state)

        if activation_state == 'active' or self._is_mu:
            # Cannot activate (or make a mu-plugin) if not installed
            if not installation_state:
                installation_state = 'symlinked'
        if installation_state == 'absent':
            # Must (attempt to) deactivate prior to uninstalling
            if not activation_state:
                activation_state = "inactive"

        return (installation_state, activation_state)
    


    def _activation_state(self, desired_state):
        """
        Returns plugin activation state based on desired state (active, inactive)

        :param desired_state: Plugin desired activation state
        """

        # Active by default
        if self._is_mu:
            return 'active'

        activation_state = desired_state.intersection(['active', 'inactive'])
        if len(activation_state) == 0:
            return None
        elif len(activation_state) == 1:
            return list(activation_state)[0]
        else:
            raise ValueError('%s %s cannot be simultaneously %s' % self.type, self.name, str(list(activation_state)))


    def _installation_state(self, desired_state):
        """
        Returns plugin installation state based on desired state (present, absent, symlinked)

        :param desired_state: Plugin desired installation state
        """
        installation_state = desired_state.intersection(['present', 'absent', 'symlinked'])
        if len(installation_state) == 0:
            return None
        elif len(installation_state) == 1:
            return list(installation_state)[0]
        else:
            raise ValueError('%s %s cannot be simultaneously %s' % self.type, self.name, str(list(installation_state)))


    def _do_symlink_file (self, basename):
        """
        Creates a symlink for a given plugin file/folder

        :param basename: given plugin file/folder for which we have to create a symlink
        """
        return self._run_action('file', {
            'state': 'link',
            # Beware src / path inversion, as is customary with everything symlink:
            'src': self._get_symlink_target(basename),
            'path': self._get_symlink_path(basename),
            })

    
    def _do_rimraf_file (self, basename):
        """
        Remove a file/folder belonging to a plugin

        :param basename: given plugin file/folder
        """
        self._run_action('file',
                         {'state': 'absent',
                          'path': self._get_symlink_path(basename)})
        return self.result

    
    def _get_symlink_path (self, basename):
        """
        Returns symlink source path

        :param basename: given plugin file/folder for which we want the symlink source path
        """
        return self._make_element_path(self._get_wp_dir(), basename)


    def _get_symlink_target (self, basename):
        """
        Returns a path to symlink target (mu-)plugin or theme file/folder

        :param basename: given plugin file/folder for which we want the symlink target path
        """
        return self._make_element_path('../../wp', basename)


    def _make_element_path (self, prefix, basename):
        """
        Generates an absolute (mu-)plugin or theme path.

        :param prefix: string to add at the beginning of the path to have an absolute one
        :param basename: given plugin file/folder for which we want the symlink source path
        """
        return '%s/wp-content/%ss/%s' % (
            prefix,
            self.type,
            basename)        

    def _run_wp_cli_action (self, args):
        """
        Executes a given WP-CLI command

        :param args: WP-CLI command to execute
        """
        return self._run_shell_action(
            '%s %s' % (self._get_ansible_var('wp_cli_command'), args))


    def _run_php_code(self, code):
        """
        Execute PHP code and returns result

        :param code: Code to execute
        """
        result = self._run_shell_action("php -r '%s'" % (code))

        return result['stdout_lines']


    def _run_shell_action (self, cmd):
        """
        Executes a Shell command

        :param cmd: Command to execute.
        """
        
        return self._run_action('command', { '_raw_params': cmd, '_uses_shell': True })


    def _run_action (self, action_name, args):
        """
        Executes an action, using an Ansible module.

        :param action_name: Ansible module name to use
        :param args: dict with arguments to give to module
        """
        # https://www.ansible.com/blog/how-to-extend-ansible-through-plugins at "Action Plugins"
        result = self._execute_module(module_name=action_name,
                                      module_args=args, tmp=self._tmp,
                                      task_vars=self._task_vars)
        
        # If command was to update an option using WP CLI
        if '_raw_params' in args and re.match(r'^wp\s--path=(.+)\soption\supdate', args['_raw_params']):
            # We update 'changed' key depending on what was done by WPCLI
            # NOTE: For an unknown reason, for some options, even if we set 'changed' to False 
            # when nothing is changed, somewhere, the value is changed to True... !?!
            result['changed'] = not result['stdout'].endswith('option is unchanged.')
        
        self._update_result(result)

        return self.result


    def _get_wp_dir (self):
        """
        Returns directory in which WordPress is installed
        """
        return self._get_ansible_var('wp_dir')


    def _get_ansible_var (self, name):
        """
        Returns Ansible var value

        :param name: Var name
        """
        unexpanded = self._task_vars.get(name, None)
        if unexpanded is None:
            return None
        else:
            return self._templar.template(unexpanded)


    def _is_filename (self, from_piece):
        """
        Tells if a path is a filename/folder name or not.

        :param from_piece: string describing plugin source.
        """
        return (from_piece != "wordpress.org/plugins"
                # check if match a github repo
                and not re.match(r'^https:\/\/github\.com\/[\w-]+\/[\w-]+(\/)?$', from_piece)
                and not from_piece.endswith(".zip"))


    def _log(self, str):
        with open('/tmp/ansible.log', 'a') as f:
            f.write("{}\n".format(str))


    def _update_result (self, result):
        """
        Updates result dict

        :param result: dict to update with
        """
        oldresult = deepcopy(self.result)
        self.result.update(result)

        def _keep_flag(flag_name):
            if (flag_name in oldresult and
                oldresult[flag_name] and
                flag_name in self.result and
                not result[flag_name]
            ):
                self.result[flag_name] = oldresult[flag_name]

        _keep_flag('changed')

        return self.result
