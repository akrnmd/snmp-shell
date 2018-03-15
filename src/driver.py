# from data_model import *  # run 'shellfoundry generate' to generate data model classes
from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext, AutoLoadCommandContext
from cloudshell.cli.cli import CLI
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.command_mode import CommandMode
from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.snmp.quali_snmp import QualiSnmp, QualiMibTable, SNMPParameters, SNMPV2ReadParameters
from data_model import *


class LinuxServerShellDriver (ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        self._logger = None
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    # <editor-fold desc="Discovery">

    def get_inventory(self, context):
        """
        Discovers the resource structure and attributes.
        :param AutoLoadCommandContext context: the context the command runs on
        :return Attribute and sub-resource information for the Shell resource you can return an AutoLoadDetails object
        :rtype: AutoLoadDetails
        """
        # See below some example code demonstrating how to return the resource structure and attributes
        # In real life, this code will be preceded by SNMP/other calls to the resource details and will not be static
        # run 'shellfoundry generate' in order to create classes that represent your data model

        '''
        resource = LinuxServerShell.create_from_context(context)
        resource.vendor = 'specify the shell vendor'
        resource.model = 'specify the shell model'

        port1 = ResourcePort('Port 1')
        port1.ipv4_address = '192.168.10.7'
        resource.add_sub_resource('1', port1)

        return resource.create_autoload_details()
        '''
        self._logger = self._get_logger(context)

        resource = LinuxServerShell.create_from_context(context)
        session = CloudShellAPISession(host=context.connectivity.server_address,
                                       token_id=context.connectivity.admin_auth_token,
                                       domain='Global')

        logger = get_qs_logger()
        address = context.resource.address
        snmp_read_community = session.DecryptPassword(context.resource.attributes['LinuxServerShell.SNMP Read Community']).Value
        snmp_v2_parameters = SNMPV2ReadParameters(ip=address, snmp_read_community=snmp_read_community)
        snmp_service = QualiSnmp(snmp_v2_parameters, logger)

        for if_table in snmp_service.get_table('IF-MIB', 'ifTable').values():
            port = ResourcePort(if_table['ifDescr'])
            port.model_name = if_table['ifType']
            port.mac_address = if_table['ifPhysAddress']
            port.port_speed = if_table['ifSpeed']
            for ip_table in snmp_service.get_table('IP-MIB', 'ipAddrTable').values():
                if ip_table['ipAdEntIfIndex'] == if_table['ifIndex']:
                    port.ipv4_address = ip_table['ipAdEntAddr']
            resource.add_sub_resource(if_table['ifIndex'], port)

        # port = ResourcePort('Port 1')
        # resource.add_sub_resource('1', port)
        # port = ResourcePort('Port 2')
        # resource.add_sub_resource('2', port)

        autoload_details = resource.create_autoload_details()
        self._logger.info('autoload attributes: ' + ','.join([str(vars(x)) for x in autoload_details.attributes]))
        self._logger.info('autoload resources: ' + ','.join([str(vars(x)) for x in autoload_details.resources]))
        return autoload_details

    # </editor-fold>

    # <editor-fold desc="Orchestration Save and Restore Standard">
    def orchestration_save(self, context, cancellation_context, mode, custom_params):
      """
      Saves the Shell state and returns a description of the saved artifacts and information
      This command is intended for API use only by sandbox orchestration scripts to implement
      a save and restore workflow
      :param ResourceCommandContext context: the context object containing resource and reservation info
      :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
      :param str mode: Snapshot save mode, can be one of two values 'shallow' (default) or 'deep'
      :param str custom_params: Set of custom parameters for the save operation
      :return: SavedResults serialized as JSON
      :rtype: OrchestrationSaveResult
      """

      # See below an example implementation, here we use jsonpickle for serialization,
      # to use this sample, you'll need to add jsonpickle to your requirements.txt file
      # The JSON schema is defined at:
      # https://github.com/QualiSystems/sandbox_orchestration_standard/blob/master/save%20%26%20restore/saved_artifact_info.schema.json
      # You can find more information and examples examples in the spec document at
      # https://github.com/QualiSystems/sandbox_orchestration_standard/blob/master/save%20%26%20restore/save%20%26%20restore%20standard.md
      '''
            # By convention, all dates should be UTC
            created_date = datetime.datetime.utcnow()

            # This can be any unique identifier which can later be used to retrieve the artifact
            # such as filepath etc.

            # By convention, all dates should be UTC
            created_date = datetime.datetime.utcnow()

            # This can be any unique identifier which can later be used to retrieve the artifact
            # such as filepath etc.
            identifier = created_date.strftime('%y_%m_%d %H_%M_%S_%f')

            orchestration_saved_artifact = OrchestrationSavedArtifact('REPLACE_WITH_ARTIFACT_TYPE', identifier)

            saved_artifacts_info = OrchestrationSavedArtifactInfo(
                resource_name="some_resource",
                created_date=created_date,
                restore_rules=OrchestrationRestoreRules(requires_same_resource=True),
                saved_artifact=orchestration_saved_artifact)

            return OrchestrationSaveResult(saved_artifacts_info)
      '''
      pass

    def orchestration_restore(self, context, cancellation_context, saved_artifact_info, custom_params):
        """
        Restores a saved artifact previously saved by this Shell driver using the orchestration_save function
        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
        :param str saved_artifact_info: A JSON string representing the state to restore including saved artifacts and info
        :param str custom_params: Set of custom parameters for the restore operation
        :return: None
        """
        '''
        # The saved_details JSON will be defined according to the JSON Schema and is the same object returned via the
        # orchestration save function.
        # Example input:
        # {
        #     "saved_artifact": {
        #      "artifact_type": "REPLACE_WITH_ARTIFACT_TYPE",
        #      "identifier": "16_08_09 11_21_35_657000"
        #     },
        #     "resource_name": "some_resource",
        #     "restore_rules": {
        #      "requires_same_resource": true
        #     },
        #     "created_date": "2016-08-09T11:21:35.657000"
        #    }

        # The example code below just parses and prints the saved artifact identifier
        saved_details_object = json.loads(saved_details)
        return saved_details_object[u'saved_artifact'][u'identifier']
        '''
        pass

    def say_hello(self, context, name):
        """
        :param ResourceCommandContext context: the context the command runs on
        :param str name: A user parameter
        """
        return "hello {name} from {resource_name}".format(name=name, resource_name=context.resource.name)

    def send_any_cmd(self, context, sendcmd):
        """
        :param InitCommandContext context : passed in by cloudshell
        :param str sendcmd: the command to send to the CLI
        """

        cli = CLI()
        mode = CommandMode(r'#')  # for example r'%\s*$'
        session = CloudShellAPISession(host=context.connectivity.server_address,
                                       token_id=context.connectivity.admin_auth_token,
                                       domain=context.reservation.domain)
        address = context.resource.address
        user = context.resource.attributes['LinuxServerShell.User']
        password = session.DecryptPassword(context.resource.attributes['LinuxServerShell.Password']).Value

        session_types = [SSHSession(host=address, username=user, password=password)]

        with cli.get_session(session_types, mode) as default_session:
            out = default_session.send_command(sendcmd)
            print(out)

        return out


    def get_snmp(self, context, snmp_module_name, miboid):
        """
        :param InitCommandContext context: this is the context passed by cloudshell automatically
        :param str snmp_module_name: MIB name
        :param str miboid: 'management information base object id' test two
        :return:
        """

        session = CloudShellAPISession(host=context.connectivity.server_address,
                                       token_id=context.connectivity.admin_auth_token,
                                       domain=context.reservation.domain)
        reservation_id = context.reservation.reservation_id
        logger = get_qs_logger()
        address = context.resource.address
        snmp_read_community = session.DecryptPassword(context.resource.attributes['LinuxServerShell.SNMP Read Community']).Value
        snmp_v2_parameters = SNMPV2ReadParameters(ip=address, snmp_read_community=snmp_read_community)
        snmp_service = QualiSnmp(snmp_v2_parameters, logger)

        for index, info in snmp_service.get_table(snmp_module_name, miboid).items():
            session.WriteMessageToReservationOutput(reservation_id, "[{0}]".format(index))
            for key, value in info.items():
                session.WriteMessageToReservationOutput(reservation_id, " {0}: {1}".format(key, value))

        return "\nEnd of execution"

    def get_attributes(self, context):
        return context.resource.attributes

    def get_context(self, context):
        return context

    # </editor-fold>

    # private functions

    def _get_logger(self, context):
        """
        returns a logger
        :param context:
        :return: the logger object
        :rtype: logging.Logger
        """
        try:
            try:
                res_id = context.reservation.reservation_id
            except:
                res_id = 'out-of-reservation'
            try:
                resource_name = context.resource.fullname
            except:
                resource_name = 'no-resource'
            logger = get_qs_logger(res_id, 'LinuxServerShellDriver', resource_name)
            return logger
        except Exception as e:
            return None
