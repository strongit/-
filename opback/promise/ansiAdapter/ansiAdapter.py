# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# this is the ansible driver module, called by promise.walker

import os
from tempfile import NamedTemporaryFile
from ansible.inventory import Inventory
from ansible.vars import VariableManager
from ansible.parsing.dataloader import DataLoader
# from ansible.executor import playbook_executor
from ansible.utils.display import Display
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.playbook.play import Play


class Options(object):
    """
    Options class to replace Ansible OptParser
    """
    def __init__(self, verbosity=None, inventory=None, listhosts=None,
                 subset=None, module_paths=None, extra_vars=None,
                 forks=None, ask_vault_pass=None, vault_password_files=None,
                 new_vault_password_file=None,
                 output_file=None, tags=None, skip_tags=None, one_line=None,
                 tree=None, ask_sudo_pass=None, ask_su_pass=None,
                 sudo=None, sudo_user=None, become=None, become_method=None,
                 become_user=None, become_ask_pass=None,
                 ask_pass=None, private_key_file=None, remote_user=None,
                 connection=None, timeout=None, ssh_common_args=None,
                 sftp_extra_args=None, scp_extra_args=None,
                 ssh_extra_args=None, poll_interval=None, seconds=None,
                 check=None, syntax=None, diff=None, force_handlers=None,
                 flush_cache=None, listtasks=None, listtags=None,
                 module_path=None):
        self.verbosity = verbosity
        self.inventory = inventory
        self.listhosts = listhosts
        self.subset = subset
        self.module_paths = module_paths
        self.extra_vars = extra_vars
        self.forks = forks
        self.ask_vault_pass = ask_vault_pass
        self.vault_password_files = vault_password_files
        self.new_vault_password_file = new_vault_password_file
        self.output_file = output_file
        self.tags = tags
        self.skip_tags = skip_tags
        self.one_line = one_line
        self.tree = tree
        self.ask_sudo_pass = ask_sudo_pass
        self.ask_su_pass = ask_su_pass
        self.sudo = sudo
        self.sudo_user = sudo_user
        self.become = become
        self.become_method = become_method
        self.become_user = become_user
        self.become_ask_pass = become_ask_pass
        self.ask_pass = ask_pass
        self.private_key_file = private_key_file
        self.remote_user = remote_user
        self.connection = connection
        self.timeout = timeout
        self.ssh_common_args = ssh_common_args
        self.sftp_extra_args = sftp_extra_args
        self.scp_extra_args = scp_extra_args
        self.ssh_extra_args = ssh_extra_args
        self.poll_interval = poll_interval
        self.seconds = seconds
        self.check = check
        self.syntax = syntax
        self.diff = diff
        self.force_handlers = force_handlers
        self.flush_cache = flush_cache
        self.listtasks = listtasks
        self.listtags = listtags
        self.module_path = module_path


class ShellExecAdapter(object):

    def __init__(self, hostnames, remote_user, private_key_file,
                 run_data, become_pass, shell, verbosity=0):

        self.run_data = run_data

        self.options = Options()
        self.options.private_key_file = private_key_file
        self.options.verbosity = verbosity
        self.options.connection = 'ssh'
        # Need a connection type "smart" or "ssh"
        self.options.become = True
        self.options.become_method = 'sudo'
        self.options.become_user = 'root'

        # Set global verbosity
        self.display = Display()
        self.display.verbosity = self.options.verbosity

        # Become Pass Needed if not logging in as user root
        passwords = {'become_pass': become_pass}

        # Gets data from YAML/JSON files
        self.loader = DataLoader()
        # self.loader.set_vault_password(os.environ['VAULT_PASS'])

        # All the variables from all the various places
        self.variable_manager = VariableManager()
        self.variable_manager.extra_vars = self.run_data

        # Parse hosts, I haven't found a good way to
        # pass hosts in without using a parsed template
        self.hosts = NamedTemporaryFile(delete=False)
        hostsString = '\n'.join(hostnames)
        self.hosts.write("""[run_hosts]\n%s""" % hostsString)
        self.hosts.close()
        # This was my attempt to pass in hosts directly.
        #
        # Also Note: In py2.7, "isinstance(foo, str)" is valid for
        #            latin chars only. Luckily, hostnames are
        #            ascii-only, which overlaps latin charset
        # if isinstance(hostnames, str):
        #     hostnames = {"customers": {"hosts": [hostnames]}}

        # Set inventory, using most of above objects
        self.inventory = Inventory(
            loader=self.loader,
            variable_manager=self.variable_manager,
            host_list=self.hosts.name)
        self.variable_manager.set_inventory(self.inventory)
        play_source = dict(
            name="shell task",
            remote_user=remote_user,
            hosts='all',
            gather_facts='no',
            tasks=[
                dict(shell=shell, args=dict(chdir='/tmp/'),
                     register='shell_out', no_log=True)])
#            tasks=[
#                dict(shell=shell, args=dict(chdir='/tmp/'),
#                     register='shell_out'),
#                dict(action=dict(module='debug',
#                     args=dict(msg='{{shell_out.stdout}}')))])
        self.play = Play().load(
            play_source, variable_manager=self.variable_manager,
            loader=self.loader)
        self.tqm = TaskQueueManager(
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords=passwords,
            stdout_callback='default')

    def run(self):
        # Results of PlaybookExecutor
        state = self.tqm.run(self.play)

        hostvars = self.tqm.hostvars
        stats = self.tqm._stats
        hosts = sorted(stats.processed.keys())
        # run_success = True
        stats_sum = dict()
        results = dict()
        for host in hosts:
            t = stats.summarize(host)
            stats_sum[host] = t
            hostvar = hostvars.__getitem__(host)
            results[host] = hostvar['shell_out']

#        self.tqm.send_callback(
#            'walker2ansibleLog',
#            walker_id=self.run_data['walker_id'],
#            user_id=self.run_data['user_id'],
#            run_success=run_success
#        )
        if self.tqm is not None:
            self.tqm.cleanup()
            os.remove(self.hosts.name)
            self.inventory.clear_pattern_cache()
        return [state, stats_sum, results]


class ScriptExecAdapter(object):

    def __init__(self, hostnames, remote_user, private_key_file,
                 run_data, become_pass, script_text, params, verbosity=0):

        self.run_data = run_data

        self.options = Options()
        self.options.private_key_file = private_key_file
        self.options.verbosity = verbosity
        self.options.connection = 'ssh'
        # Need a connection type "smart" or "ssh"
        self.options.become = True
        self.options.become_method = 'sudo'
        self.options.become_user = 'root'

        # Set global verbosity
        self.display = Display()
        self.display.verbosity = self.options.verbosity

        # Become Pass Needed if not logging in as user root
        passwords = {'become_pass': become_pass}

        # Gets data from YAML/JSON files
        self.loader = DataLoader()
        # self.loader.set_vault_password(os.environ['VAULT_PASS'])

        # All the variables from all the various places
        self.variable_manager = VariableManager()
        self.variable_manager.extra_vars = self.run_data

        # Parse hosts, I haven't found a good way to
        # pass hosts in without using a parsed template
        self.hosts_file = NamedTemporaryFile(delete=False)
        hostsString = '\n'.join(hostnames)
        self.hosts_file.write("""[run_hosts]\n%s""" % hostsString)
        self.hosts_file.close()
        self.script_file = NamedTemporaryFile(delete=False)
        self.script_file.write("""%s""" % script_text.encode('utf-8'))
        self.script_file.close()

        # This was my attempt to pass in hosts directly.
        #
        # Also Note: In py2.7, "isinstance(foo, str)" is valid for
        #            latin chars only. Luckily, hostnames are
        #            ascii-only, which overlaps latin charset
        # if isinstance(hostnames, str):
        #     hostnames = {"customers": {"hosts": [hostnames]}}

        # Set inventory, using most of above objects
        self.inventory = Inventory(
            loader=self.loader,
            variable_manager=self.variable_manager,
            host_list=self.hosts_file.name)
        self.variable_manager.set_inventory(self.inventory)
        # file = open(self.script_file.name)
        # read=file.read()
        # print read
        play_source = dict(
            name="script task",
            remote_user=remote_user,
            hosts='all',
            gather_facts='no',
            tasks=[
                dict(
                    script=self.script_file.name + ' ' +
                    params.encode('utf-8'),
                    register='script_out', no_log=True)])
#            tasks=[
#                dict(script=self.script_file.name + ' ' + str(params),
#                     register='script_out', no_log=True),
#                dict(action=dict(module='debug',
#                     args=dict(msg='{{script_out.stdout}}')))])
        self.play = Play().load(
            play_source, variable_manager=self.variable_manager,
            loader=self.loader)
        self.tqm = TaskQueueManager(
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords=passwords,
            stdout_callback='default')
        print play_source

    def run(self):
        # Results of PlaybookExecutor
        state = self.tqm.run(self.play)

        hostvars = self.tqm.hostvars
        stats = self.tqm._stats
        hosts = sorted(stats.processed.keys())
        # run_success = True
        stats_sum = dict()
        results = dict()
        for host in hosts:
            t = stats.summarize(host)
            stats_sum[host] = t
            hostvar = hostvars.__getitem__(host)
            results[host] = hostvar['script_out']

#        self.tqm.send_callback(
#            'walker2ansibleLog',
#            walker_id=self.run_data['walker_id'],
#            user_id=self.run_data['user_id'],
#            run_success=run_success
#        )

        if self.tqm is not None:
            self.tqm.cleanup()
            os.remove(self.hosts_file.name)
            self.inventory.clear_pattern_cache()
        return [state, stats_sum, results]
