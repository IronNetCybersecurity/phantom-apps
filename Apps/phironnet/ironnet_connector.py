# -----------------------------------------
# IronNet Phantom Connector
# -----------------------------------------

# Phantom App imports
import phantom.app as phantom
from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult

import json
import re
import swagger_client
from swagger_client.rest import ApiException

severity_mapping = {
    "undecided": "SEVERITY_UNDECIDED",
    "benign": "SEVERITY_BENIGN",
    "suspicious": "SEVERITY_SUSPICIOUS",
    "malicious": "SEVERITY_MALICIOUS"
}

expectation_mapping = {
    "expected": "EXP_EXPECTED",
    "unexpected": "EXP_UNEXPECTED",
    "unknown": "EXP_UNKNOWN"
}

status_mapping = {
    "awaiting review": "STATUS_AWAITING_REVIEW",
    "under review": "STATUS_UNDER_REVIEW",
    "closed": "STATUS_CLOSED"
}

# Phantom ts format
phantom_ts = re.compile('^(\\d+-\\d+-\\d+) (\\d+:\\d+\\d+:\\d+\\.\\d+\\+\\d+)$')


def fix_timestamp(timestamp):
    # Attempts to reformat the given timestamp as RFC3339
    match = phantom_ts.match(timestamp)
    if(match):
        return match.group(1) + "T" + match.group(2) + ":00"
    return timestamp


class RetVal(tuple):
    def __new__(cls, val1, val2=None):
        return tuple.__new__(RetVal, (val1, val2))


class IronnetConnector(BaseConnector):

    def __init__(self):

        # Call the BaseConnectors init first
        super(IronnetConnector, self).__init__()

        self._state = None

        self._base_url = None
        self._username = None
        self._password = None
        self._verify_server_cert = None
        self._enable_alert_notifications = None
        self._alert_notification_actions = None
        self._alert_categories = None
        self._alert_subcategories = None
        self._alert_severity_lower = None
        self._alert_severity_upper = None
        self._alert_limit = None
        self._enable_dome_notifications = None
        self._dome_categories = None
        self._dome_limit = None
        self._enable_event_notifications = None
        self._alert_event_actions = None
        self._event_categories = None
        self._event_subcategories = None
        self._event_severity_lower = None
        self._event_severity_upper = None
        self._event_limit = None
        self._store_event_notifs_in_alert_containers = None
        self._api_instance = None

    def _handle_test_connectivity(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress("Attempting to connect to IronAPI")

        call_status = None

        try:
            response = self._api_instance.login(swagger_client.IronapiTypesLoginRequest(), _preload_content=False)
            self.save_progress("Received response: Code:{}, Data:{}".format(response.status, response.data.encode('utf-8')))
            if response.status != 200:
                call_status = phantom.APP_ERROR
                action_result.set_status(call_status, "Fetch for Login failed. Status code was " + str(response.status))
            else:
                call_status = phantom.APP_SUCCESS
        except ApiException as e:
            call_status = phantom.APP_ERROR
            action_result.set_status(phantom.APP_ERROR, 'A server error has occurred: ' + str(e))

        if phantom.is_success(call_status):
            return action_result.set_status(phantom.APP_SUCCESS, "Test Connectivity to IronAPI Passed")
        else:
            self.save_progress("Error occurred in Test Connectivity: {}".format(action_result.get_message()))
            return action_result.set_status(phantom.APP_ERROR, "Test Connectivity to IronAPI Failed")

    def _handle_irondefense_rate_alert(self, param):
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress("Received param: {0}".format(param))

        # Access action parameters passed in the 'param' dictionary
        request = {
            'alert_id': param.get('alert_id'),
            'comment': param.get('comment'),
            'share_comment_with_irondome': param.get('share_comment_with_irondome'),
            'analyst_severity': severity_mapping[param.get('analyst_severity', '')],
            'analyst_expectation': expectation_mapping[param.get('analyst_expectation', '')]
        }

        call_status = None

        try:
            response = self._api_instance.rate_alert(swagger_client.AlertRateAlertRequest(request), _preload_content=False)
            self.save_progress("Received response: Code:{}, Data:{}".format(response.status, response.data.encode('utf-8')))
            if response.status != 200:
                call_status = phantom.APP_ERROR
                action_result.set_status(call_status, "Rate Alert failed. Status code was " + str(response.status))
            else:
                response_data = json.loads(response.data)
                call_status = phantom.APP_SUCCESS
        except ApiException as e:
            call_status = phantom.APP_ERROR
            action_result.set_status(phantom.APP_ERROR, 'A server error has occurred: ' + str(e))

        if phantom.is_success(call_status):
            self.debug_print("Alert rating was successful")
            # Add the response into the data section
            action_result.add_data(response_data)
            return action_result.set_status(phantom.APP_SUCCESS, "Alert rating was successful")
        else:
            self.debug_print("Alert rating failed. Error: {}".format(action_result.get_message()))
            return action_result.set_status(phantom.APP_ERROR, "Alert rating failed. Error: {}".format(action_result.get_message()))

    def _handle_irondefense_set_alert_status(self, param):
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress("Received param: {0}".format(param))

        # Access action parameters passed in the 'param' dictionary
        request = {
            'alert_id': param.get('alert_id'),
            'comment': param.get('comment'),
            'share_comment_with_irondome': param.get('share_comment_with_irondome'),
            'status': status_mapping[param.get('alert_status')]
        }

        call_status = None

        try:
            response = self._api_instance.set_alert_status(swagger_client.AlertSetAlertStatusRequest(request), _preload_content=False)
            self.save_progress("Received response: Code:{}, Data:{}".format(response.status, response.data.encode('utf-8')))
            if response.status != 200:
                call_status = phantom.APP_ERROR
                action_result.set_status(call_status, "Set Alert status failed. Status code was " + str(response.status))
            else:
                response_data = json.loads(response.data)
                call_status = phantom.APP_SUCCESS
        except ApiException as e:
            call_status = phantom.APP_ERROR
            action_result.set_status(phantom.APP_ERROR, 'A server error has occurred: ' + str(e))

        if phantom.is_success(call_status):
            self.debug_print("Setting alert staus was successful")
            # Add the response into the data section
            action_result.add_data(response_data)
            return action_result.set_status(phantom.APP_SUCCESS, "Setting alert status was successful")
        else:
            self.debug_print("Setting alert status failed. Error: {}".format(action_result.get_message()))
            return action_result.set_status(phantom.APP_ERROR, "Setting alert status failed. Error: {}".format(action_result.get_message()))

    def _handle_irondefense_comment_on_alert(self, param):
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress("Received param: {0}".format(param))

        # Access action parameters passed in the 'param' dictionary
        request = {
            'alert_id': param.get('alert_id'),
            'comment': param.get('comment'),
            'share_comment_with_irondome': param.get('share_comment_with_irondome')
        }

        call_status = None

        try:
            response = self._api_instance.comment_on_alert(swagger_client.AlertCommentOnAlertRequest(request), _preload_content=False)
            self.save_progress("Received response: Code:{}, Data:{}".format(response.status, response.data.encode('utf-8')))
            if response.status != 200:
                call_status = phantom.APP_ERROR
                action_result.set_status(call_status, "Comment on Alert failed. Status code was " + str(response.status))
            else:
                response_data = json.loads(response.data)
                call_status = phantom.APP_SUCCESS
        except ApiException as e:
            call_status = phantom.APP_ERROR
            action_result.set_status(phantom.APP_ERROR, 'A server error has occurred: ' + str(e))

        if phantom.is_success(call_status):
            self.debug_print("Adding comment to alert was successful")
            # Add the response into the data section
            action_result.add_data(response_data)
            return action_result.set_status(phantom.APP_SUCCESS, "Adding comment to alert was successful")
        else:
            self.debug_print("Adding comment to alert failed. Error: {}".format(action_result.get_message()))
            return action_result.set_status(phantom.APP_ERROR, "Adding comment failed. Error: {}".format(action_result.get_message()))

    def _handle_irondefense_report_observed_bad_activity(self, param):
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress("Received param: {0}".format(param))

        # Access action parameters passed in the 'param' dictionary
        request = {
            'name': param['name'],
            'description': param.get('description', ''),
            'domain': param.get('domain', ''),
            'ip': param.get('ip', ''),
            'activity_start_time': fix_timestamp(param['activity_start_time']),
            'activity_end_time': fix_timestamp(param.get('activity_end_time', param['activity_start_time'])),
        }

        self.save_progress("Request: {0}".format(request))

        call_status = None

        try:
            response = self._api_instance.report_observed_bad_activity(swagger_client.ThreatReportObservedBadActivityRequest(request), _preload_content=False)
            self.save_progress("Received response: Code:{}, Data:{}".format(response.status, response.data.encode('utf-8')))
            if response.status != 200:
                call_status = phantom.APP_ERROR
                action_result.set_status(call_status, "Report observed bad activity failed. Status code was " + str(response.status))
            else:
                response_data = json.loads(response.data)
                call_status = phantom.APP_SUCCESS
        except ApiException as e:
            call_status = phantom.APP_ERROR
            action_result.set_status(phantom.APP_ERROR, 'A server error has occurred: ' + str(e))

        if phantom.is_success(call_status):
            self.debug_print("Reporting bad activity to IronDefense was successful")
            # Add the response into the data section
            action_result.add_data(response_data)
            return action_result.set_status(phantom.APP_SUCCESS, "Reporting bad activity to IronDefense was successful")
        else:
            self.debug_print("Reporting bad activity to IronDefense failed. Error: {}".format(action_result.get_message()))
            return action_result.set_status(phantom.APP_ERROR, "Reporting bad activity to IronDefense failed. Error: {}".format(action_result.get_message()))

    def _handle_irondefense_get_alert_irondome_info(self, param):
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress("Received param: {0}".format(param))

        # Access action parameters passed in the 'param' dictionary
        request = {
            'alert_id': param['alert_id']
        }

        call_status = None

        try:
            response = self._api_instance.get_alert_iron_dome_information(swagger_client.DomeGetAlertIronDomeInformationRequest(request), _preload_content=False)
            self.save_progress("Received response: Code:{}, Data:{}".format(response.status, response.data.encode('utf-8')))
            if response.status != 200:
                call_status = phantom.APP_ERROR
                action_result.set_status(call_status, "Get alert IronDome info failed. Status code was " + str(response.status))
            else:
                response_data = json.loads(response.data)
                call_status = phantom.APP_SUCCESS
        except ApiException as e:
            call_status = phantom.APP_ERROR
            action_result.set_status(phantom.APP_ERROR, 'A server error has occurred: ' + str(e))

        if phantom.is_success(call_status):
            self.debug_print("Retrieving IronDome alert info was successful")
            # Add the response into the data section
            action_result.add_data(response_data)
            return action_result.set_status(phantom.APP_SUCCESS, "Retrieving IronDome alert info was successful")
        else:
            self.debug_print("Retrieving IronDome alert info failed. Error: {}".format(action_result.get_message()))
            return action_result.set_status(phantom.APP_ERROR, "Retrieving IronDome alert info failed. Error: {}".format(action_result.get_message()))

    def _handle_irondefense_get_alert_notifications(self):
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict()))

        call_status = None

        try:
            response = self._api_instance.get_alert_notifications(swagger_client.AlertGetAlertNotificationsRequest(limit=self._alert_limit), _preload_content=False)
            self.save_progress("Received response: Code:{}, Data:{}".format(response.status, response.data.encode('utf-8')))
            if response.status != 200:
                call_status = phantom.APP_ERROR
                action_result.set_status(call_status, "Fetch for AlertNotifications failed. Status code was " + str(response.status))
            else:
                response_data = json.loads(response.data)
                call_status = phantom.APP_SUCCESS
        except ApiException as e:
            call_status = phantom.APP_ERROR
            action_result.set_status(phantom.APP_ERROR, 'A server error has occurred: ' + str(e))

        if phantom.is_success(call_status):
            self.save_progress("Fetching alert notifications was successful")
            # Filter the response
            for alert_notification in response_data['alert_notifications']:
                if alert_notification['alert_action'] in self._alert_notification_actions and alert_notification['alert']:
                    alert = alert_notification['alert']
                    if alert['category'] not in self._alert_categories and alert['sub_category'] not in self._alert_subcategories:
                        if self._alert_severity_lower <= int(alert['severity']) <= self._alert_severity_upper:
                            # create container
                            container = {
                                'name': alert['id'],
                                'kill_chain': alert['category'],
                                'description': "IronDefense {}/{} alert".
                                format(alert['category'], alert['sub_category']),
                                'source_data_identifier': alert['id'],
                                'data': alert,
                            }
                            container_status, container_msg, container_id = self.save_container(container)
                            if container_status == phantom.APP_ERROR:
                                self.debug_print("Failed to store: {}".format(container_msg))
                                self.debug_print("Failed with status: {}".format(container_status))
                                action_result.set_status(phantom.APP_ERROR, 'Alert Notification container creation failed: {}'.format(container_msg))
                                return container_status

                            # add notification as artifact of container
                            artifact = {
                                'data': alert_notification,
                                'name': "{} ALERT NOTIFICATION".format(alert_notification['alert_action'][4:].replace("_", " ")),
                                'container_id': container_id,
                                'source_data_identifier': "{}-{}".format(alert['id'], alert["updated"]),
                                'start_time': alert['updated']
                            }
                            artifact_status, artifact_msg, artifact_id = self.save_artifact(artifact)
                            if artifact_status == phantom.APP_ERROR:
                                self.debug_print("Failed to store: {}".format(artifact_msg))
                                self.debug_print("Failed with status: {}".format(artifact_status))
                                action_result.set_status(phantom.APP_ERROR, 'Alert Notification artifact creation failed: {}'.format(artifact_msg))
                                return artifact_status

            self.save_progress("Filtering alert notifications was successful")
            return action_result.set_status(phantom.APP_SUCCESS)
        else:
            self.debug_print(action_result.get_message())
            self.save_progress("Fetching alert notifications failed")
            return action_result.set_status(phantom.APP_ERROR, action_result.get_message())

    def _handle_irondefense_get_dome_notifications(self):
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict()))

        call_status = None

        try:
            response = self._api_instance.get_dome_notifications(swagger_client.DomeGetDomeNotificationsRequest(limit=self._dome_limit), _preload_content=False)
            self.save_progress("Received response: Code:{}, Data:{}".format(response.status, response.data.encode('utf-8')))
            if response.status != 200:
                call_status = phantom.APP_ERROR
                action_result.set_status(call_status, "Fetch for DomeNotifications failed. Status code was " + str(response.status))
            else:
                response_data = json.loads(response.data)
                call_status = phantom.APP_SUCCESS
        except ApiException as e:
            call_status = phantom.APP_ERROR
            action_result.set_status(call_status, 'A server error has occurred: ' + str(e))

        if phantom.is_success(call_status):
            self.save_progress("Fetching dome notifications was successful")
            # Filter the response
            for dome_notification in response_data['dome_notifications']:
                if dome_notification['category'] not in self._dome_categories:
                    for alert_id in dome_notification['alert_ids']:
                        # create or find container
                        container = {
                            'name': alert_id,
                            'source_data_identifier': alert_id,
                        }
                        container_status, container_msg, container_id = self.save_container(container)
                        if container_status == phantom.APP_ERROR:
                            self.debug_print("Failed to store: {}".format(container_msg))
                            self.debug_print("Failed with status: {}".format(container_status))
                            action_result.set_status(phantom.APP_ERROR, 'Dome Notification container creation failed: {}'.format(container_msg))
                            return container_status

                        # add notification as artifact of container
                        artifact = {
                            'data': dome_notification,
                            'name': "{} DOME NOTIFICATION".format(dome_notification['category'][4:].replace("_", " ")),
                            'container_id': container_id,
                            'source_data_identifier': "{}".format(dome_notification["id"]),
                            'start_time': dome_notification['created']
                        }
                        artifact_status, artifact_msg, artifact_id = self.save_artifact(artifact)
                        if artifact_status == phantom.APP_ERROR:
                            self.debug_print("Failed to store: {}".format(artifact_msg))
                            self.debug_print("Failed with status: {}".format(artifact_status))
                            action_result.set_status(phantom.APP_ERROR, 'Dome Notification artifact creation failed: {}'.format(artifact_msg))
                            return artifact_status

            self.save_progress("Filtering dome notifications was successful")
            return action_result.set_status(phantom.APP_SUCCESS)
        else:
            self.debug_print(action_result.get_message())
            self.save_progress("Fetching dome notifications failed")
            return action_result.set_status(phantom.APP_ERROR, action_result.get_message())

    def _handle_irondefense_get_event_notifications(self):
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict()))

        call_status = None

        try:
            response = self._api_instance.get_event_notifications(swagger_client.EventGetEventNotificationsRequest(limit=self._event_limit), _preload_content=False)
            self.save_progress("Received response: Code:{}, Data:{}".format(response.status, response.data.encode('utf-8')))
            if response.status != 200:
                call_status = phantom.APP_ERROR
                action_result.set_status(call_status, "Fetch for EventNotifications failed. Status code was " + str(response.status))
            else:
                response_data = json.loads(response.data)
                call_status = phantom.APP_SUCCESS
        except ApiException as e:
            call_status = phantom.APP_ERROR
            action_result.set_status(call_status, 'A server error has occurred: ' + str(e))

        if response.status != 200:
            call_status = phantom.APP_ERROR
            action_result.set_status(call_status, "Fetch for EventNotifications failed. Status code was " + str(response.status))

        if phantom.is_success(call_status):
            self.save_progress("Fetching event notifications was successful")
            # Filter the response
            for event_notification in response_data['event_notifications']:
                if event_notification['event_action'] in self._event_notification_actions and event_notification['event']:
                    event = event_notification['event']
                    if event['category'] not in self._event_categories and event['sub_category'] not in self._event_subcategories:
                        if self._event_severity_lower <= int(event['severity']) <= self._event_severity_upper:
                            if self._store_event_notifs_in_alert_containers:
                                # store in alert container
                                container = {
                                    'name': event['alert_id'],
                                    'source_data_identifier': event['alert_id'],
                                }
                                container_status, container_msg, container_id = self.save_container(container)
                                if container_status == phantom.APP_ERROR:
                                    self.debug_print("Failed to store: {}".format(container_msg))
                                    self.debug_print("Failed with status: {}".format(container_status))
                                    action_result.set_status(phantom.APP_ERROR, 'Event Notification container creation failed: {}'.format(container_msg))
                                    return container_status

                                # add notification as artifact of container
                                artifact = {
                                    'data': event_notification,
                                    'name': "{} EVENT NOTIFICATION".format(event_notification['event_action'][4:].replace("_", " ")),
                                    'container_id': container_id,
                                    'source_data_identifier': "{}-{}".format(event['id'], event["updated"]),
                                    'start_time': event['updated']
                                }
                            else:
                                # store in event container
                                container = {
                                    'name': event['id'],
                                    'kill_chain': event['category'],
                                    'description': "IronDefense {}/{} event".
                                    format(event['category'], event['sub_category']),
                                    'source_data_identifier': event['id'],
                                    'data': event,
                                }
                                container_status, container_msg, container_id = self.save_container(container)
                                if container_status == phantom.APP_ERROR:
                                    self.debug_print("Failed to store: {}".format(container_msg))
                                    self.debug_print("Failed with status: {}".format(container_status))
                                    action_result.set_status(phantom.APP_ERROR, 'Event Notification container creation failed: {}'.format(container_msg))
                                    return container_status

                                # add notification as artifact of container
                                artifact = {
                                    'data': event_notification,
                                    'name': "{} EVENT NOTIFICATION".format(event_notification['event_action'][4:].replace("_", " ")),
                                    'container_id': container_id,
                                    'source_data_identifier': "{}-{}".format(event['id'], event["updated"]),
                                    'start_time': event['updated']
                                }
                            artifact_status, artifact_msg, artifact_id = self.save_artifact(artifact)
                            if artifact_status == phantom.APP_ERROR:
                                self.debug_print("Failed to store: {}".format(artifact_msg))
                                self.debug_print("Failed with status: {}".format(artifact_status))
                                action_result.set_status(phantom.APP_ERROR, 'Event Notification artifact creation failed: {}'.format(artifact_msg))
                                return artifact_status

            self.save_progress("Filtering event notifications was successful")
            return action_result.set_status(phantom.APP_SUCCESS)
        else:
            self.debug_print(action_result.get_message())
            self.save_progress("Fetching event notifications failed")
            return action_result.set_status(phantom.APP_ERROR, action_result.get_message())

    def _handle_irondefense_get_alerts(self, param):
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress("Received param: {0}".format(param))

        # Access action parameters passed in the 'param' dictionary
        request = {}
        if 'alert_id' in param and param['alert_id'].strip() != '':
            request['alert_id'] = param['alert_id'].strip().split(",")
        if 'category' in param and param['category'].strip() != '':
            request['category'] = [str(cat).strip().replace(" ", "_").upper() for cat in param['category'].split(',')]
        if 'sub_category' in param and param['sub_category'].strip() != '':
            request['sub_category'] = [str(cat).strip().replace(" ", "_").upper() for cat in param['sub_category'].split(',')]
        if 'status' in param and param['status'].strip() != '':
            request['status'] = [status_mapping[status.strip().lower()] for status in param['status'].split(',')]
        min_sev = 0 if 'min_severity' not in param else param['min_severity']
        max_sev = 1000 if 'max_severity' not in param else param['max_severity']
        request['severity'] = {
            "lower_bound": min_sev,
            "upper_bound": max_sev
        }

        call_status = None

        try:
            response = self._api_instance.get_alerts(swagger_client.AlertGetAlertsRequest(request), _preload_content=False)
            self.save_progress("Received response: Code:{}, Data:{}".format(response.status, response.data.encode('utf-8')))
            if response.status != 200:
                call_status = phantom.APP_ERROR
                action_result.set_status(call_status, "Get Alerts failed. Status code was " + str(response.status))
            else:
                response_data = json.loads(response.data)
                call_status = phantom.APP_SUCCESS
        except ApiException as e:
            call_status = phantom.APP_ERROR
            action_result.set_status(phantom.APP_ERROR, 'A server error has occurred: ' + str(e))

        if phantom.is_success(call_status):
            self.debug_print("Retrieving alerts was successful")
            # Add the response into the data section
            action_result.add_data(response_data)
            return action_result.set_status(phantom.APP_SUCCESS, "Retrieving alerts was successful")
        else:
            self.debug_print("Retrieving alerts failed. Error: {}".format(action_result.get_message()))
            return action_result.set_status(phantom.APP_ERROR, "Retrieving alerts failed. Error: {}".format(action_result.get_message()))

    def _handle_irondefense_get_events(self, param):
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict()))

        # Access action parameters passed in the 'param' dictionary
        request = {
            'alert_id': param['alert_id']
        }

        call_status = None

        try:
            response = self._api_instance.get_events(swagger_client.EventGetEventsRequest(request), _preload_content=False)
            self.save_progress("Received response: Code:{}, Data:{}".format(response.status, response.data.encode('utf-8')))
            if response.status != 200:
                call_status = phantom.APP_ERROR
                action_result.set_status(call_status, "Get Events failed. Status code was " + str(response.status))
            else:
                response_data = json.loads(response.data)
                call_status = phantom.APP_SUCCESS
        except ApiException as e:
            call_status = phantom.APP_ERROR
            action_result.set_status(phantom.APP_ERROR, 'A server error has occurred: ' + str(e))

        if phantom.is_success(call_status):
            self.debug_print("Retrieving events was successful")
            # Add the response into the data section
            action_result.add_data(response_data)
            return action_result.set_status(phantom.APP_SUCCESS, "Retrieving events was successful")
        else:
            self.debug_print("Retrieving events failed. Error: {}".format(action_result.get_message()))
            return action_result.set_status(phantom.APP_ERROR,
                                            "Retrieving events failed. Error: {}".format(
                                                action_result.get_message()))

    def _handle_irondefense_get_event(self, param):
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict()))

        # Access action parameters passed in the 'param' dictionary
        request = {
            'event_id': param['event_id']
        }

        call_status = None

        try:
            response = self._api_instance.get_event(swagger_client.EventGetEventRequest(request), _preload_content=False)
            self.save_progress("Received response: Code:{}, Data:{}".format(response.status, response.data.encode('utf-8')))
            if response.status != 200:
                call_status = phantom.APP_ERROR
                action_result.set_status(call_status, "Get Event failed. Status code was " + str(response.status))
            else:
                response_data = json.loads(response.data)
                call_status = phantom.APP_SUCCESS
        except ApiException as e:
            call_status = phantom.APP_ERROR
            action_result.set_status(phantom.APP_ERROR, 'A server error has occurred: ' + str(e))

        if phantom.is_success(call_status):
            self.debug_print("Retrieving event was successful")
            # Add the response into the data section
            action_result.add_data(response_data)
            return action_result.set_status(phantom.APP_SUCCESS, "Retrieving event was successful")
        else:
            self.debug_print("Retrieving event failed. Error: {}".format(action_result.get_message()))
            return action_result.set_status(phantom.APP_ERROR,
                                            "Retrieving event failed. Error: {}".format(
                                                action_result.get_message()))

    def handle_action(self, param):
        ret_val = phantom.APP_SUCCESS

        # Get the action that we are supposed to execute for this App Run
        action_id = self.get_action_identifier()

        self.debug_print("action_id", self.get_action_identifier())

        if action_id == 'test_connectivity':
            ret_val = self._handle_test_connectivity(param)
        elif action_id == 'irondefense_rate_alert':
            ret_val = self._handle_irondefense_rate_alert(param)
        elif action_id == 'irondefense_set_alert_status':
            ret_val = self._handle_irondefense_set_alert_status(param)
        elif action_id == 'irondefense_comment_on_alert':
            ret_val = self._handle_irondefense_comment_on_alert(param)
        elif action_id == 'irondefense_report_observed_bad_activity':
            ret_val = self._handle_irondefense_report_observed_bad_activity(param)
        elif action_id == 'irondefense_get_alert_irondome_info':
            ret_val = self._handle_irondefense_get_alert_irondome_info(param)
        elif action_id == 'irondefense_get_events':
            ret_val = self._handle_irondefense_get_events(param)
        elif action_id == 'on_poll':
            alert_ret_val = phantom.APP_SUCCESS
            dome_ret_val = phantom.APP_SUCCESS
            event_ret_val = phantom.APP_SUCCESS

            if self._enable_alert_notifications:
                alert_ret_val = self._handle_irondefense_get_alert_notifications()
            else:
                self.save_progress("Fetching alert notifications is disabled")
            if self._enable_dome_notifications:
                dome_ret_val = self._handle_irondefense_get_dome_notifications()
            else:
                self.save_progress("Fetching dome notifications is disabled")
            if self._enable_event_notifications:
                event_ret_val = self._handle_irondefense_get_event_notifications()
            else:
                self.save_progress("Fetching event notifications is disabled")
            ret_val = alert_ret_val and dome_ret_val and event_ret_val
        elif action_id == 'irondefense_get_alerts':
            ret_val = self._handle_irondefense_get_alerts(param)
        elif action_id == 'irondefense_get_event':
            ret_val = self._handle_irondefense_get_event(param)

        return ret_val

    def initialize(self):
        # Load the state in initialize, use it to store data
        # that needs to be accessed across actions
        self._state = self.load_state()

        # get the asset config
        config = self.get_config()

        self._base_url = config.get('base_url')
        self._username = config.get('username')
        self._password = config.get('password')
        self._verify_server_cert = config.get('verify_server_cert')

        configuration = swagger_client.Configuration()
        configuration.host = config.get('base_url')
        configuration.username = config.get('username')
        configuration.password = config.get('password')
        configuration.verify_ssl = config.get('verify_server_cert')
        self._api_instance = swagger_client.IronApiApi(swagger_client.ApiClient(configuration))

        # Alert Notification Configs
        self._enable_alert_notifications = config.get('enable_alert_notifications')
        if self._enable_alert_notifications:
            alert_acts = config.get('alert_notification_actions')
            if alert_acts:
                self._alert_notification_actions = ["ANA_" + str(act).strip().replace(" ", "_").upper() for act in
                                             alert_acts.split(',') if act.strip()]
            else:
                self._alert_notification_actions = ["ANA_ALERT_CREATED"]
            alert_cats = config.get('alert_categories')
            if alert_cats:
                self._alert_categories = [str(cat).strip().replace(" ", "_").upper() for cat in alert_cats.split(',')
                                          if cat.strip()]
            else:
                self._alert_categories = []
            alert_subcats = config.get('alert_subcategories')
            if alert_subcats:
                self._alert_subcategories = [str(subcat).strip().replace(" ", "_").upper() for subcat in
                                             alert_subcats.split(',') if subcat.strip()]
            else:
                self._alert_subcategories = []
            self._alert_severity_lower = int(config.get('alert_severity_lower'))
            self._alert_severity_upper = int(config.get('alert_severity_upper'))
            if self._alert_severity_lower >= self._alert_severity_upper:
                self.save_progress("Initialization Failed: Invalid Range for Alert Severity- {} is not lower than {}"
                        .format(self._alert_severity_lower, self._alert_severity_upper))
                return phantom.APP_ERROR
            self._alert_limit = int(config.get('alert_limit'))

        # Dome Notification Configs
        self._enable_dome_notifications = config.get('enable_dome_notifications')
        if self._enable_dome_notifications:
            dome_cats = config.get('dome_categories')
            if dome_cats:
                self._dome_categories = ["DNC_{}".format(str(cat).strip().replace(" ", "_").upper()) for cat in
                                         dome_cats.split(',') if cat.strip()]
            else:
                self._dome_categories = []
            self._dome_limit = int(config.get('dome_limit'))

        # Event Notification Configs
        self._enable_event_notifications = config.get('enable_event_notifications')
        if self._enable_event_notifications:
            event_acts = config.get('event_notification_actions')
            if event_acts:
                self._event_notification_actions = ["ENA_" + str(act).strip().replace(" ", "_").upper() for act in
                                             event_acts.split(',') if act.strip()]
            else:
                self._event_notification_actions = ["ENA_EVENT_CREATED"]
            event_cats = config.get('event_categories')
            if event_cats:
                self._event_categories = [str(cat).strip().replace(" ", "_").upper() for cat in event_cats.split(',')
                                          if cat.strip()]
            else:
                self._event_categories = []
            event_subcats = config.get('event_subcategories')
            if event_subcats:
                self._event_subcategories = [str(subcat).strip().replace(" ", "_").upper() for subcat in
                                             event_subcats.split(',') if subcat.strip()]
            else:
                self._event_subcategories = []
            self._event_severity_lower = int(config.get('event_severity_lower'))
            self._event_severity_upper = int(config.get('event_severity_upper'))
            if self._event_severity_lower >= self._event_severity_upper:
                self.save_progress("Initialization Failed: Invalid Range for Event Severity- {} is not lower than {}"
                        .format(self._event_severity_lower, self._event_severity_upper))
                return phantom.APP_ERROR
            self._event_limit = int(config.get('event_limit'))
            self._store_event_notifs_in_alert_containers = config.get('store_event_notifs_in_alert_containers')

        return phantom.APP_SUCCESS

    def finalize(self):

        # Save the state, this data is saved across actions and app upgrades
        self.save_state(self._state)
        return phantom.APP_SUCCESS


if __name__ == '__main__':
    import sys

    with open(sys.argv[1]) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = IronnetConnector()
        connector.print_progress_message = True

        ret_val = connector._handle_action(json.dumps(in_json), None)
        print(json.dumps(json.loads(ret_val), indent=4))

    exit(0)
