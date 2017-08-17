"""
requirements: python-jenkins
Communicate with Jenkins in an OOP-like way is more convenient than using
python-jenkins directly.
"""

import json
import logging
import xml.etree.ElementTree as ET
from urlparse import urljoin
from contextlib import contextmanager

import jenkins
import requests

logger = logging.getLogger(__name__)


class JenkinsHandler(jenkins.Jenkins):
    def __init__(self, host, username, password):
        try:
            if host.find('https') == 0:
                raise Exception('https protocol for jenkins not support.')
            elif host.find('http') < 0:
                host = 'http://' + host
            jenkins.Jenkins.__init__(self, host,
                                     username=username,
                                     password=password)
            self.git_plugin_info = self.get_plugin_info('git')
        except jenkins.JenkinsException as e:
            # log
            raise

    def get(self):
        return self

    def put(self, obj):
        pass

    def update_node(self, name, **kwargs):
        if not kwargs:
            return
        else:
            config_xml = self.get_node_config(name)
            root = ET.fromstring(config_xml)

        if kwargs['label']:
            e_label = root.find('label')
            e_label.text = kwargs['label']

        self.reconfig_node(name, ET.tostring(root))

    def create_credential(self, domain, name, password, scope, type):
        raise Exception('not support yet.')
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Authorization': self.auth,
                   # self.crumb['crumbRequestField']: self.crumb['crumb']
                   }
        json_data = {'': '0',
                     'credentials': {'username': name,
                                     'password': password,
                                     'description': 'create by api',
                                     '$class': 'com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl',
                                     'scope': 'GLOBAL',
                                     'id': ""
                                     }
                     }
        url = urljoin(self.server,
                      '/credential-store/domain/domain1/createCredentials')

        response = requests.post(url, data={'json': json.dumps(json_data)},
                                 headers=headers)

    def get_credentials(self):
        raise Exception('not support yet.')
        headers = {'Authorization': self.auth}
        url = urljoin(self.server,
                      '/credential-store/domain/domain1/api/json')
        res = requests.get(url, headers=headers)


XML_PARAMETER = '''<?xml version='1.0' encoding='UTF-8'?>
<hudson.model.StringParameterDefinition>
  <name></name>
  <description></description>
  <defaultValue></defaultValue>
</hudson.model.StringParameterDefinition>'''

XML_TRIGGERS_REVERSE = '''<?xml version='1.0' encoding='UTF-8'?>
<jenkins.triggers.ReverseBuildTrigger>
  <spec></spec>
  <upstreamProjects></upstreamProjects>
  <threshold>
    <name>SUCCESS</name>
    <ordinal>0</ordinal>
    <color>BLUE</color>
    <completeBuild>true</completeBuild>
  </threshold>
</jenkins.triggers.ReverseBuildTrigger>
'''

XML_SCM = '''<?xml version='1.0' encoding='UTF-8'?>
<scm class="hudson.plugins.git.GitSCM" plugin="git@2.3.5">
  <configVersion>2</configVersion>
  <userRemoteConfigs>
    <hudson.plugins.git.UserRemoteConfig>
      <url/>
      <credentialsId/>
    </hudson.plugins.git.UserRemoteConfig>
  </userRemoteConfigs>
  <branches>
    <hudson.plugins.git.BranchSpec>
      <name>*/master</name>
    </hudson.plugins.git.BranchSpec>
  </branches>
  <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
  <submoduleCfg class="list"/>
  <extensions/>
</scm>'''

SHELL_BUILDER = '''<?xml version='1.0' encoding='UTF-8'?>
<hudson.tasks.Shell>
  <command></command>
</hudson.tasks.Shell>'''


class BaseObject(object):
    # This is a queue-like object which should support get and put method. The
    # get method will return an instance of jenkins.Jenkins, and the put method
    # will retrieve the instance.
    handler_hub = None

    @contextmanager
    def get_handler(self):
        handler = self.handler_hub.get()
        try:
            yield handler
        finally:
            self.handler_hub.put(handler)


class JenkinsProject(BaseObject):
    def __init__(self, name, config_xml=None):
        """
        :param name: project name, ``str``
        :param config_xml: default config_xml if project not exist. If not set 
        and project not exists, use jenkins.EMPTY_CONFIG_XML as the default 
        configuration. Ignored if project already exist. ``str``
        """
        self.name = name
        self.config_xml = config_xml
        self.exist = None

    def create(self, force=False):
        """Create the project. Do nothing if project with the same name already
        exists. Set force True to re-create a project that exists.

        :param force: ``boolean``
        """
        if self.exist is None:
            self.check_remote_project()

        with self.get_handler() as handler:
            if self.exist:
                if force:
                    handler.delete_job(self.name)
                    handler.create_job(self.name, self.config_xml)
            else:
                handler.create_job(self.name, self.config_xml)

    def check_remote_project(self):
        """Check project exists or not. If exists, get the config_xml.
        """
        with self.get_handler() as handler:
            try:
                self.config_xml = handler.get_job_config(self.name)
                self.exist = True
            except jenkins.NotFoundException:
                if not self.config_xml:
                    self.config_xml = jenkins.EMPTY_CONFIG_XML
                self.exist = False

    def set_scm(self, scm_url=None, scm_branch=None):
        """Configure scm_url and scm_branch. If scm_url is none, nothing 
        changes, which is the same with the scm_branch. If scm_url is '', the 
        operation is not defined. If scm_branch is '', the default value 
        '*/master' will be set.

        :param scm_url: str
        :param scm_branch: str
        """
        if scm_url is None and scm_branch is None:
            logger.warn('no scm configured: all input is none.')
            return
        if self.exist is None:
            self.check_remote_project()
        root = ET.fromstring(self.config_xml)

        with self.get_handler() as handler:
            if scm_url is not None:
                if scm_url.strip() == '':
                    # this is an undefined operation
                    pass
                else:
                    element_scm = root.find('scm')
                    if element_scm.attrib['class'] == 'hudson.scm.NullSCM':
                        root.remove(element_scm)
                        element_scm = ET.fromstring(XML_SCM)
                        root.append(element_scm)
                        git_info = handler.git_plugin_info
                        element_scm.set('plugin',
                                        'git@' + str(git_info['version']))

                    if self.exist == False:
                        git_info = handler.git_plugin_info
                        element_scm.set('plugin',
                                        'git@' + str(git_info['version']))
                    element_url = element_scm.iter('url').next()
                    element_url.text = scm_url

            if scm_branch is not None:
                element_scm = root.find('scm')
                if element_scm.attrib['class'] == 'hudson.scm.NullSCM':
                    raise Exception('scm url not configured.')
                element_branch = element_scm.iter('name').next()
                if scm_branch.strip() == '':
                    element_branch.text = '*/master'
                else:
                    element_branch.text = scm_branch

        self.config_xml = ET.tostring(root)

    def set_trigger_project(self, project_name):
        """Configure trigger project. If project_name is '', all triggers will 
        be removed.

        :param project_name: ``str``
        """
        if project_name is None:
            raise ValueError('trigger project is None ')
        if self.exist is None:
            self.check_remote_project()
        root = ET.fromstring(self.config_xml)

        element_triggers = root.find('triggers')
        element_triggers.clear()

        if project_name.strip() != '':
            element_trigger = ET.fromstring(XML_TRIGGERS_REVERSE)
            element_upstream_projects = element_trigger.find('upstreamProjects')
            element_upstream_projects.text = project_name
            element_triggers.append(element_trigger)

        self.config_xml = ET.tostring(root)

    def set_assigned_node(self, assigned_node):
        """Configure assigned_node. if assigned_node is '', the node will be
        deleted.

        :param assigned_node: ``str``
        """
        if assigned_node is None:
            raise ValueError('assigned_node is None ')
        if self.exist is None:
            self.check_remote_project()
        root = ET.fromstring(self.config_xml)

        if assigned_node != '':
            # set label
            element_node = root.find('assignedNode')
            if element_node is None:
                element_node = ET.Element('assignedNode')
                root.append(element_node)
            element_node.text = assigned_node
            root.find('canRoam').text = 'false'
        else:
            # delete label
            element_node = root.find('assignedNode')
            if element_node is not None:
                root.remove(element_node)
            root.find('canRoam').text = 'true'

        self.config_xml = ET.tostring(root)

    def set_builder(self, index, script, type=SHELL_BUILDER):
        """Set the index-th builder. To set the first builder, set index=0.
        If index is no less than the number of builders that already exist, new
        builder will be appended. Only support shell builder.

        :param index: ``int``
        :param script: ``str``
        :return: index that the new builder sits.
        """
        if not script:
            raise ValueError('script is None or empty')
        if self.exist is None:
            self.check_remote_project()
        root = ET.fromstring(self.config_xml)
        builder_new = ET.fromstring(type)
        builder_new.find('command').text = script

        builder_root = root.find('builders')
        builders = builder_root.findall('./')
        if index >= len(builders):
            index = len(builders)
            builder_root.append(builder_new)
        else:
            builder_root.remove(builders[index])
            builder_root.insert(index, builder_new)

        self.config_xml = ET.tostring(root)
        return index

    def re_configure(self):
        """ refresh the configuration of the project with self.config_xml
        """
        if self.config_xml is None:
            raise Exception('config_xml is None')
        with self.get_handler() as handler:
            handler.reconfig_job(self.name, self.config_xml)

    def set_build_parameters(self, **kwargs):
        """Configure build parameters, only support string type parameter. Old 
        parameters will be cleaned.

        :param kwargs: parameters, ``dict``.
        """
        if not kwargs:
            return

        if self.exist is None:
            self.check_remote_project()
        root = ET.fromstring(self.config_xml)
        element_par_def = self.get_para_def_element(root)

        element_parameters = element_par_def.findall(
            'hudson.model.StringParameterDefinition')
        for e in element_parameters:
            element_par_def.remove(e)

        for key, value in kwargs.iteritems():
            element_parameter = ET.fromstring(XML_PARAMETER)
            element_parameter.find('name').text = key
            element_parameter.find('defaultValue').text = value
            element_par_def.append(element_parameter)

        self.config_xml = ET.tostring(root)

    def update_build_parameters(self, **kwargs):
        """Configure build parameters, only support string type parameter. Add
        a parameter if not existed, update a parameter if exist. Unable to 
        delete a parameter.

        :param kwargs: parameters, ``dict``.
        """
        if not kwargs:
            return

        if self.exist is None:
            self.check_remote_project()
        root = ET.fromstring(self.config_xml)
        element_par_def = self.get_para_def_element(root)

        element_parameters = element_par_def.findall(
            'hudson.model.StringParameterDefinition')
        for key, value in kwargs.iteritems():
            for e in element_parameters:
                if key == e.find('name').text:
                    e.find('defaultValue').text = value
                    break
            else:
                element_parameter = ET.fromstring(XML_PARAMETER)
                element_parameter.find('name').text = key
                element_parameter.find('defaultValue').text = value
                element_par_def.append(element_parameter)

        self.config_xml = ET.tostring(root)

    def get_para_def_element(self, root):
        element_properties = root.find('properties')
        element_par_def_pro = element_properties.find(
            'hudson.model.ParametersDefinitionProperty')
        if element_par_def_pro is None:
            element_par_def_pro = ET.Element(
                'hudson.model.ParametersDefinitionProperty')
            element_properties.append(element_par_def_pro)

        element_par_def = element_par_def_pro.find('parameterDefinitions')
        if element_par_def is None:
            element_par_def = ET.Element('parameterDefinitions')
            element_par_def_pro.append(element_par_def)

        return element_par_def

    def do_build(self):
        """build jenkins job, always with parameters
        """
        # In our business scenarios, job is always built with parameters.
        # According to jenkins API, to build with parameters, the second
        # parameter of build_job() is needed, or error will occur.
        with self.get_handler() as handler:
            handler.build_job(self.name,
                              parameters={'delay': '0sec'})

    def get_next_build_number(self):
        with self.get_handler() as handler:
            info = handler.get_job_info(self.name)
            num = info['nextBuildNumber']
            inQueue = info['inQueue']
        return num, inQueue

    def get_build_info(self, build_number, *args):
        """Get build information specified by args from jenkins. If args not 
        provided, return handler.get_build_info(job_name, build_number).

        :param build_number: jenkins build number. ``str``
        :param args: only support : commit_hash, build_result, scm_url. ``str``
        :returns: dictionary of information, ``dict``

        Example:
            get_build_detail(build_number, 'commit_hash', 'build_result')

            return: {'commit_hash': '12345678901234567890',
                     'build_result: 'SUCCEED'
                    }
        """

        with self.get_handler() as handler:
            build_info = handler.get_build_info(self.name, build_number)
        if not args:
            return build_info

        data = {}
        # get commit hash
        if 'commit_hash' in args:
            for dict_value in build_info['actions']:
                if dict_value.get('lastBuiltRevision'):
                    data['commit_hash'] = dict_value['lastBuiltRevision'][
                        'SHA1']
                    break
            else:
                data['commit_hash'] = ''

        # get scm url
        if 'scm_url' in args:
            for dict_value in build_info['actions']:
                if dict_value.get('remoteUrls'):
                    data['scm_url'] = dict_value['remoteUrls'][0].replace(
                        '.git', '')
                    break
            else:
                data['scm_url'] = ''

        # get build result
        if 'build_result' in args:
            data['build_result'] = build_info.get('result', '')

        return data

    def get_job_info(self):
        with self.get_handler() as handler:
            job_info = handler.get_job_info(self.name)
        return job_info

    def cancel_queue(self, id):
        with self.get_handler() as handler:
            handler.cancel_queue(id)

    def stop_build(self, build_number):
        with self.get_handler() as handler:
            handler.stop_build(self.name, build_number)


class JenkinsNode(BaseObject):
    def __init__(self, name, label, numExecutors):
        self.name = name
        self.label = label
        self.numExecutors = numExecutors

    def create(self):
        with self.get_handler() as handler:
            handler.create_node(self.name, labels=self.label, exclusive=True,
                                numExecutors=self.numExecutors,
                                launcher=jenkins.LAUNCHER_JNLP,
                                remoteFS='/var/jenkins_home')

    def delete(self):
        with self.get_handler() as handler:
            handler.delete_node(self.name)


def basic_init(host, port, username, password):
    handler = JenkinsHandler('%s:%s' % (host, port), username, password)
    BaseObject.handler_hub = handler



