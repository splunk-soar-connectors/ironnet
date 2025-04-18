# Copyright (c) 2025 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# File: ironnet_connector.py
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.

import json
import re

import phantom.app as phantom
import requests
from bs4 import BeautifulSoup, UnicodeDammit
from phantom.action_result import ActionResult
from phantom.base_connector import BaseConnector


severity_mapping = {
    "undecided": "SEVERITY_UNDECIDED",
    "benign": "SEVERITY_BENIGN",
    "suspicious": "SEVERITY_SUSPICIOUS",
    "malicious": "SEVERITY_MALICIOUS",
}

expectation_mapping = {"expected": "EXP_EXPECTED", "unexpected": "EXP_UNEXPECTED", "unknown": "EXP_UNKNOWN"}

status_mapping = {"awaiting review": "STATUS_AWAITING_REVIEW", "under review": "STATUS_UNDER_REVIEW", "closed": "STATUS_CLOSED"}

# Phantom ts format
phantom_ts = re.compile("^(\\d+-\\d+-\\d+) (\\d+:\\d+\\d+:\\d+\\.\\d+\\+\\d+)$")


def fix_timestamp(timestamp):
    # Attempts to reformat the given timestamp as RFC3339
    match = phantom_ts.match(timestamp)
    if match:
        return match.group(1) + "T" + match.group(2) + ":00"
    return timestamp


class RetVal(tuple):
    def __new__(cls, val1, val2=None):
        return tuple.__new__(RetVal, (val1, val2))


class IronnetConnector(BaseConnector):
    def __init__(self):
        # Call the BaseConnectors init first
        super().__init__()

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

    def _process_empty_response(self, response, action_result):
        if response.status_code == 200:
            return RetVal(phantom.APP_SUCCESS, {})

        return RetVal(action_result.set_status(phantom.APP_ERROR, "Empty response and no information in the header"), None)

    def _process_html_response(self, response, action_result):
        # An html response, treat it like an error
        status_code = response.status_code

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            error_text = soup.text
            split_lines = error_text.split("\n")
            split_lines = [x.strip() for x in split_lines if x.strip()]
            error_text = "\n".join(split_lines)
        except:
            error_text = "Cannot parse error details"

        message = f"Status Code: {status_code}. Data from server:\n{error_text}\n"

        message = message.replace("{", "{{").replace("}", "}}")

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_json_response(self, r, action_result):
        # Try a json parse
        try:
            resp_json = r.json()
        except Exception as e:
            return RetVal(action_result.set_status(phantom.APP_ERROR, f"Unable to parse JSON response. Error: {e}"), None)

        # Please specify the status codes here
        if 200 <= r.status_code < 399:
            return RetVal(phantom.APP_SUCCESS, resp_json)

        # You should process the error returned in the json
        message = f"Error from server. Status Code: {r.status_code} Data from server: {r.text.replace('{', '{{').replace('}', '}}')}"

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_response(self, r, action_result):
        self.save_progress(f"Received response: Code:{r.status_code}, Data:{r.text}")

        # store the r_text in debug data, it will get dumped in the logs if the action fails
        if hasattr(action_result, "add_debug_data"):
            action_result.add_debug_data({"r_status_code": r.status_code})
            action_result.add_debug_data({"r_text": r.text})
            action_result.add_debug_data({"r_headers": r.headers})

        # Process each 'Content-Type' of response separately

        # Process a json response
        if "json" in r.headers.get("Content-Type", ""):
            return self._process_json_response(r, action_result)

        # Process an HTML response, Do this no matter what the api talks.
        # There is a high chance of a PROXY in between phantom and the rest of
        # world, in case of errors, PROXY's return HTML, this function parses
        # the error and adds it to the action_result.
        if "html" in r.headers.get("Content-Type", ""):
            return self._process_html_response(r, action_result)

        # it's not content-type that is to be parsed, handle an empty response
        if not r.text:
            return self._process_empty_response(r, action_result)

        # everything else is actually an error at this point
        message = (
            f"Can't process response from server. Status Code: {r.status_code} "
            + f"Data from server: {r.text.replace('{', '{{').replace('}', '}}')}"
        )

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _make_post(self, endpoint, action_result, method="post", data={}, **kwargs):
        # **kwargs can be any additional parameters that requests.request accepts
        if kwargs["headers"] is None:
            kwargs["headers"] = {"Content-Type": "application/json"}

        try:
            request_func = getattr(requests, method)
        except AttributeError:
            return RetVal(action_result.set_status(phantom.APP_ERROR, f"Invalid method: {method}"), None)

        # Create a URL to connect to
        url = UnicodeDammit(self._base_url).unicode_markup.encode("utf-8") + endpoint.encode("utf-8")

        self.save_progress(f"Issuing {method} request on {url} w/ content: {data}")
        try:
            r = request_func(
                url,
                auth=(self._username, self._password),  # basic authentication
                verify=self._verify_server_cert,
                data=json.dumps(data),
                **kwargs,
            )
        except Exception as e:
            if e.message:
                if isinstance(e.message, str):
                    error_msg = UnicodeDammit(e.message).unicode_markup.encode("UTF-8")
                else:
                    try:
                        error_msg = str(e.message)
                    except:
                        error_msg = "Unknown error occurred. Please check the asset configuration parameters."
            else:
                error_msg = "Unknown error occurred. Please check the asset configuration parameters."
            self.save_progress(f"Error while issuing REST call - {error_msg}")
            return RetVal(action_result.set_status(phantom.APP_ERROR, f"Error Connecting to server. Details: {error_msg}"), None)

        return self._process_response(r, action_result)

    def _handle_test_connectivity(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress("Attempting to connect to IronAPI")

        # make rest call
        ret_val, response = self._make_post("/Login", action_result, data=None, headers=None)

        if phantom.is_success(ret_val):
            return action_result.set_status(phantom.APP_SUCCESS, "Test Connectivity to IronAPI Passed")
        else:
            self.save_progress(f"Error occurred in Test Connectivity: {action_result.get_message()}")
            return action_result.set_status(phantom.APP_ERROR, "Test Connectivity to IronAPI Failed")

    def _handle_irondefense_rate_alert(self, param):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress(f"Received param: {param}")

        # Access action parameters passed in the 'param' dictionary
        request = {
            "alert_id": param.get("alert_id"),
            "comment": param.get("comment"),
            "share_comment_with_irondome": param.get("share_comment_with_irondome"),
            "analyst_severity": severity_mapping[param.get("analyst_severity", "")],
            "analyst_expectation": expectation_mapping[param.get("analyst_expectation", "")],
        }

        # make rest call
        ret_val, response = self._make_post("/RateAlert", action_result, data=request, headers=None)

        # Add the response into the data section
        action_result.add_data(response)

        if phantom.is_success(ret_val):
            self.debug_print("Alert rating was successful")
            return action_result.set_status(phantom.APP_SUCCESS, "Alert rating was successful")
        else:
            self.debug_print(f"Alert rating failed. Error: {action_result.get_message()}")
            return action_result.set_status(phantom.APP_ERROR, f"Alert rating failed. Error: {action_result.get_message()}")

    def _handle_irondefense_set_alert_status(self, param):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress(f"Received param: {param}")

        # Access action parameters passed in the 'param' dictionary
        request = {
            "alert_id": param.get("alert_id"),
            "comment": param.get("comment"),
            "share_comment_with_irondome": param.get("share_comment_with_irondome"),
            "status": status_mapping[param.get("alert_status")],
        }

        # make rest call
        ret_val, response = self._make_post("/SetAlertStatus", action_result, data=request, headers=None)

        # Add the response into the data section
        action_result.add_data(response)

        if phantom.is_success(ret_val):
            self.debug_print("Setting alert staus was successful")
            return action_result.set_status(phantom.APP_SUCCESS, "Setting alert status was successful")
        else:
            self.debug_print(f"Setting alert status failed. Error: {action_result.get_message()}")
            return action_result.set_status(phantom.APP_ERROR, f"Setting alert status failed. Error: {action_result.get_message()}")

    def _handle_irondefense_comment_on_alert(self, param):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress(f"Received param: {param}")

        # Access action parameters passed in the 'param' dictionary
        request = {
            "alert_id": param.get("alert_id"),
            "comment": param.get("comment"),
            "share_comment_with_irondome": param.get("share_comment_with_irondome"),
        }

        # make rest call
        ret_val, response = self._make_post("/CommentOnAlert", action_result, data=request, headers=None)

        # Add the response into the data section
        action_result.add_data(response)

        if phantom.is_success(ret_val):
            self.debug_print("Adding comment to alert was successful")
            return action_result.set_status(phantom.APP_SUCCESS, "Adding comment to alert was successful")
        else:
            self.debug_print(f"Adding comment failed. Error: {action_result.get_message()}")
            return action_result.set_status(phantom.APP_ERROR, f"Adding comment failed. Error: {action_result.get_message()}")

    def _handle_irondefense_report_observed_bad_activity(self, param):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress(f"Received param: {param}")

        # Access action parameters passed in the 'param' dictionary
        request = {
            "name": param["name"],
            "description": param.get("description", ""),
            "domain": param.get("domain", ""),
            "ip": param.get("ip", ""),
            "activity_start_time": fix_timestamp(param["activity_start_time"]),
            "activity_end_time": fix_timestamp(param.get("activity_end_time", param["activity_start_time"])),
        }

        self.save_progress(f"Request: {request}")

        # make rest call
        ret_val, response = self._make_post("/ReportObservedBadActivity", action_result, data=request, headers=None)

        # Add the response into the data section
        action_result.add_data(response)

        if phantom.is_success(ret_val):
            self.debug_print("Reporting bad activity to IronDefense was successful")
            return action_result.set_status(phantom.APP_SUCCESS, "Reporting bad activity to IronDefense was successful")
        else:
            self.debug_print(f"Reporting bad activity to IronDefense failed. Error: {action_result.get_message()}")
            return action_result.set_status(
                phantom.APP_ERROR, f"Reporting bad activity to IronDefense failed. Error: {action_result.get_message()}"
            )

    def _handle_irondefense_get_alert_irondome_info(self, param):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress(f"Received param: {param}")

        # Access action parameters passed in the 'param' dictionary
        request = {"alert_id": param["alert_id"]}

        # make rest call
        ret_val, response = self._make_post("/GetAlertIronDomeInformation", action_result, data=request, headers=None)

        # Add the response into the data section
        action_result.add_data(response)

        if phantom.is_success(ret_val):
            self.debug_print("Retrieving IronDome alert info was successful")
            return action_result.set_status(phantom.APP_SUCCESS, "Retrieving IronDome alert info was successful")
        else:
            self.debug_print(f"Retrieving IronDome alert info failed. Error: {action_result.get_message()}")
            return action_result.set_status(phantom.APP_ERROR, f"Retrieving IronDome alert info failed. Error: {action_result.get_message()}")

    def _handle_irondefense_get_alert_notifications(self):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict()))

        request = {"limit": self._alert_limit}

        # make rest call
        ret_val, response = self._make_post("/GetAlertNotifications", action_result, data=request, headers=None)
        if phantom.is_success(ret_val):
            self.save_progress(f"Fetching alert notifications was successful, , got {len(response['alert_notifications'])} notifications")
            # Filter the response
            for alert_notification in response["alert_notifications"]:
                if alert_notification["alert_action"] in self._alert_notification_actions and alert_notification["alert"]:
                    alert = alert_notification["alert"]
                    if alert["category"] not in self._alert_categories and alert["sub_category"] not in self._alert_subcategories:
                        if self._alert_severity_lower <= int(alert["severity"]) <= self._alert_severity_upper:
                            # create container
                            container = {
                                "name": f"{alert['category']}/{alert['sub_category']}",
                                "kill_chain": alert["category"],
                                "description": f"IronDefense {alert['category']}/{alert['sub_category']} alert",
                                "source_data_identifier": alert["id"],
                                "data": alert,
                            }
                            container_status, container_msg, container_id = self.save_container(container)
                            if container_status == phantom.APP_ERROR:
                                self.debug_print(f"Failed to store: {container_msg}")
                                self.debug_print(f"Failed to status: {container_status}")
                                action_result.set_status(phantom.APP_ERROR, f"Alert Notification container creation failed: {container_msg}")
                                return container_status

                            # add notification as artifact of container
                            artifact = {
                                "data": alert_notification,
                                "name": f"{alert_notification['alert_action'][4:].replace('_', ' ')} ALERT NOTIFICATION",
                                "container_id": container_id,
                                "source_data_identifier": f"{alert['id']}-{alert['updated']}",
                                "start_time": alert["updated"],
                            }
                            artifact_status, artifact_msg, artifact_id = self.save_artifact(artifact)
                            if artifact_status == phantom.APP_ERROR:
                                self.debug_print(f"Failed to store: {artifact_msg}")
                                self.debug_print(f"Failed with status: {artifact_status}")
                                action_result.set_status(phantom.APP_ERROR, f"Alert Notification artifact creation failed: {artifact_msg}")
                                return artifact_status

            self.save_progress("Filtering alert notifications was successful")
            return action_result.set_status(phantom.APP_SUCCESS)
        else:
            self.debug_print(action_result.get_message())
            self.save_progress("Fetching alert notifications failed")
            return action_result.set_status(phantom.APP_ERROR, action_result.get_message())

    def _handle_irondefense_get_dome_notifications(self):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict()))

        request = {"limit": self._dome_limit}

        # make rest call
        ret_val, response = self._make_post("/GetDomeNotifications", action_result, data=request, headers=None)
        if phantom.is_success(ret_val):
            self.save_progress(f"Fetching dome notifications was successful, got {len(response['dome_notifications'])} notifications")
            # Filter the response
            for dome_notification in response["dome_notifications"]:
                if dome_notification["category"] not in self._dome_categories:
                    for alert_id in dome_notification["alert_ids"]:
                        # create or find container
                        container = {
                            "name": dome_notification["category"][4:].replace("_", " "),
                            "source_data_identifier": alert_id,
                            "description": "Alert container with Dome notifications",
                        }
                        container_status, container_msg, container_id = self.save_container(container)
                        if container_status == phantom.APP_ERROR:
                            self.debug_print(f"Failed to store: {container_msg}")
                            self.debug_print(f"Failed to status: {container_status}")
                            action_result.set_status(phantom.APP_ERROR, f"Dome Notification container creation failed: {container_msg}")
                            return container_status

                        # add notification as artifact of container
                        artifact = {
                            "data": dome_notification,
                            "name": f"{dome_notification['category'][4:].replace('_', ' ')} DOME NOTIFICATION",
                            "container_id": container_id,
                            "source_data_identifier": str(dome_notification["id"]),
                            "start_time": dome_notification["created"],
                        }
                        artifact_status, artifact_msg, artifact_id = self.save_artifact(artifact)
                        if artifact_status == phantom.APP_ERROR:
                            self.debug_print(f"Failed to store: {artifact_msg}")
                            self.debug_print(f"Failed with status: {artifact_status}")
                            action_result.set_status(phantom.APP_ERROR, f"Dome Notification artifact creation failed: {artifact_msg}")
                            return artifact_status

            self.save_progress("Filtering dome notifications was successful")
            return action_result.set_status(phantom.APP_SUCCESS)
        else:
            self.debug_print(action_result.get_message())
            self.save_progress("Fetching dome notifications failed")
            return action_result.set_status(phantom.APP_ERROR, action_result.get_message())

    def _handle_irondefense_get_event_notifications(self):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict()))

        request = {"limit": self._event_limit}

        # make rest call
        ret_val, response = self._make_post("/GetEventNotifications", action_result, data=request, headers=None)
        if phantom.is_success(ret_val):
            self.save_progress(f"Fetching event notifications was successful, got {len(response['event_notifications'])} notifications")
            # Filter the response
            for event_notification in response["event_notifications"]:
                if event_notification["event_action"] in self._event_notification_actions and event_notification["event"]:
                    event = event_notification["event"]
                    if event["category"] not in self._event_categories and event["sub_category"] not in self._event_subcategories:
                        if self._event_severity_lower <= int(event["severity"]) <= self._event_severity_upper:
                            if self._store_event_notifs_in_alert_containers:
                                # store in alert container
                                container = {
                                    "name": f"{event['category']}/{event['sub_category']}",
                                    "source_data_identifier": event["alert_id"],
                                }
                                container_status, container_msg, container_id = self.save_container(container)
                                if container_status == phantom.APP_ERROR:
                                    self.debug_print(f"Failed to store: {container_msg}")
                                    self.debug_print(f"Failed with status: {container_status}")
                                    action_result.set_status(phantom.APP_ERROR, f"Event Notification container creation failed: {container_msg}")
                                    return container_status

                                # add notification as artifact of container
                                artifact = {
                                    "data": event_notification,
                                    "name": f"{event_notification['event_action'][4:].replace('_', ' ')} EVENT NOTIFICATION",
                                    "container_id": container_id,
                                    "source_data_identifier": f"{event['id']}-{event['updated']}",
                                    "start_time": event["updated"],
                                }
                            else:
                                # store in event container
                                container = {
                                    "name": f"{event['category']}/{event['sub_category']}",
                                    "kill_chain": event["category"],
                                    "description": f"IronDefense {event['category']}/{event['sub_category']} event",
                                    "source_data_identifier": event["id"],
                                    "data": event,
                                }
                                container_status, container_msg, container_id = self.save_container(container)
                                if container_status == phantom.APP_ERROR:
                                    self.debug_print(f"Failed to store: {container_msg}")
                                    self.debug_print(f"Failed with status: {container_status}")
                                    action_result.set_status(phantom.APP_ERROR, f"Event Notification container creation failed: {container_msg}")
                                    return container_status

                                # add notification as artifact of container
                                artifact = {
                                    "data": event_notification,
                                    "name": f"{event_notification['event_action'][4:].replace('_', ' ')} EVENT NOTIFICATION",
                                    "container_id": container_id,
                                    "source_data_identifier": f"{event['id']}-{event['updated']}",
                                    "start_time": event["updated"],
                                }
                            artifact_status, artifact_msg, artifact_id = self.save_artifact(artifact)
                            if artifact_status == phantom.APP_ERROR:
                                self.debug_print(f"Failed to store: {artifact_msg}")
                                self.debug_print(f"Failed with status: {artifact_status}")
                                action_result.set_status(phantom.APP_ERROR, f"Event Notification artifact creation failed: {artifact_msg}")
                                return artifact_status

            self.save_progress("Filtering event notifications was successful")
            return action_result.set_status(phantom.APP_SUCCESS)
        else:
            self.debug_print(action_result.get_message())
            self.save_progress("Fetching event notifications failed")
            return action_result.set_status(phantom.APP_ERROR, action_result.get_message())

    def _handle_irondefense_get_alerts(self, param):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress(f"Received param: {param}")

        # Access action parameters passed in the 'param' dictionary
        request = {}
        if "alert_id" in param and param["alert_id"].strip() != "":
            request["alert_id"] = param["alert_id"].strip().split(",")
        if "category" in param and param["category"].strip() != "":
            request["category"] = [str(cat).strip().replace(" ", "_").upper() for cat in param["category"].split(",")]
        if "sub_category" in param and param["sub_category"].strip() != "":
            request["sub_category"] = [str(cat).strip().replace(" ", "_").upper() for cat in param["sub_category"].split(",")]
        if "status" in param and param["status"].strip() != "":
            request["status"] = [status_mapping[status.strip().lower()] for status in param["status"].split(",")]
        min_sev = param.get("min_severity", 0)
        max_sev = param.get("max_severity", 1000)
        request["severity"] = {"lower_bound": min_sev, "upper_bound": max_sev}

        # make rest call
        ret_val, response = self._make_post("/GetAlerts", action_result, data=request, headers=None)

        # Add the response into the data section
        action_result.add_data(response)

        if phantom.is_success(ret_val):
            self.debug_print("Retrieving alerts was successful")
            return action_result.set_status(phantom.APP_SUCCESS, "Retrieving alerts was successful")
        else:
            self.debug_print(f"Retrieving alerts failed. Error: {action_result.get_message()}")
            return action_result.set_status(phantom.APP_ERROR, f"Retrieving alerts failed. Error: {action_result.get_message()}")

    def _handle_irondefense_get_events(self, param):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict()))

        # Access action parameters passed in the 'param' dictionary
        request = {"alert_id": param["alert_id"]}
        # make rest call
        ret_val, response = self._make_post("/GetEvents", action_result, data=request, headers=None)

        # Add the response into the data section
        action_result.add_data(response)

        if phantom.is_success(ret_val):
            self.debug_print("Retrieving events was successful")
            return action_result.set_status(phantom.APP_SUCCESS, "Retrieving events was successful")
        else:
            self.debug_print(f"Retrieving events failed. Error: {action_result.get_message()}")
            return action_result.set_status(phantom.APP_ERROR, f"Retrieving events failed. Error: {action_result.get_message()}")

    def _handle_irondefense_get_event(self, param):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict()))

        # Access action parameters passed in the 'param' dictionary
        request = {"event_id": param["event_id"]}
        # make rest call
        ret_val, response = self._make_post("/GetEvent", action_result, data=request, headers=None)

        # Add the response into the data section
        action_result.add_data(response)

        if phantom.is_success(ret_val):
            self.debug_print("Retrieving event was successful")
            return action_result.set_status(phantom.APP_SUCCESS, "Retrieving event was successful")
        else:
            self.debug_print(f"Retrieving event failed. Error: {action_result.get_message()}")
            return action_result.set_status(phantom.APP_ERROR, f"Retrieving event failed. Error: {action_result.get_message()}")

    def _handle_on_poll(self, param):
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

        return alert_ret_val and dome_ret_val and event_ret_val

    def handle_action(self, param):
        ret_val = phantom.APP_SUCCESS

        # Get the action that we are supposed to execute for this App Run
        action_id = self.get_action_identifier()

        self.debug_print("action_id", self.get_action_identifier())

        if action_id == "test_connectivity":
            ret_val = self._handle_test_connectivity(param)
        elif action_id == "irondefense_rate_alert":
            ret_val = self._handle_irondefense_rate_alert(param)
        elif action_id == "irondefense_set_alert_status":
            ret_val = self._handle_irondefense_set_alert_status(param)
        elif action_id == "irondefense_comment_on_alert":
            ret_val = self._handle_irondefense_comment_on_alert(param)
        elif action_id == "irondefense_report_observed_bad_activity":
            ret_val = self._handle_irondefense_report_observed_bad_activity(param)
        elif action_id == "irondefense_get_alert_irondome_info":
            ret_val = self._handle_irondefense_get_alert_irondome_info(param)
        elif action_id == "irondefense_get_events":
            ret_val = self._handle_irondefense_get_events(param)
        elif action_id == "on_poll":
            ret_val = self._handle_on_poll(param)
        elif action_id == "irondefense_get_alerts":
            ret_val = self._handle_irondefense_get_alerts(param)
        elif action_id == "irondefense_get_event":
            ret_val = self._handle_irondefense_get_event(param)

        return ret_val

    def initialize(self):
        # Load the state in initialize, use it to store data
        # that needs to be accessed across actions
        self._state = self.load_state()

        # get the asset config
        config = self.get_config()

        self._base_url = config.get("base_url") + "/IronApi"
        self._username = config.get("username")
        self._password = config.get("password")
        self._verify_server_cert = config.get("verify_server_cert")

        # Alert Notification Configs
        self._enable_alert_notifications = config.get("enable_alert_notifications")
        if self._enable_alert_notifications:
            alert_acts = config.get("alert_notification_actions")
            if alert_acts:
                self._alert_notification_actions = [
                    "ANA_" + str(act).strip().replace(" ", "_").upper() for act in alert_acts.split(",") if act.strip()
                ]
            else:
                self._alert_notification_actions = ["ANA_ALERT_CREATED"]
            alert_cats = config.get("alert_categories")
            if alert_cats:
                self._alert_categories = [str(cat).strip().replace(" ", "_").upper() for cat in alert_cats.split(",") if cat.strip()]
            else:
                self._alert_categories = []
            alert_subcats = config.get("alert_subcategories")
            if alert_subcats:
                self._alert_subcategories = [
                    str(subcat).strip().replace(" ", "_").upper() for subcat in alert_subcats.split(",") if subcat.strip()
                ]
            else:
                self._alert_subcategories = []
            self._alert_severity_lower = int(config.get("alert_severity_lower"))
            self._alert_severity_upper = int(config.get("alert_severity_upper"))
            if self._alert_severity_lower >= self._alert_severity_upper:
                self.save_progress(
                    f"Initialization Failed: Invalid Range for Alert Severity- {self._alert_severity_lower} "
                    f"is not lower than {self._alert_severity_upper}"
                )
                return phantom.APP_ERROR
            self._alert_limit = int(config.get("alert_limit"))

        # Dome Notification Configs
        self._enable_dome_notifications = config.get("enable_dome_notifications")
        if self._enable_dome_notifications:
            dome_cats = config.get("dome_categories")
            if dome_cats:
                self._dome_categories = [f"DNC_{str(cat).strip().replace(' ', '_').upper()}" for cat in dome_cats.split(",") if cat.strip()]
            else:
                self._dome_categories = []
            self._dome_limit = int(config.get("dome_limit"))

        # Event Notification Configs
        self._enable_event_notifications = config.get("enable_event_notifications")
        if self._enable_event_notifications:
            event_acts = config.get("event_notification_actions")
            if event_acts:
                self._event_notification_actions = [
                    "ENA_" + str(act).strip().replace(" ", "_").upper() for act in event_acts.split(",") if act.strip()
                ]
            else:
                self._event_notification_actions = ["ENA_EVENT_CREATED"]
            event_cats = config.get("event_categories")
            if event_cats:
                self._event_categories = [str(cat).strip().replace(" ", "_").upper() for cat in event_cats.split(",") if cat.strip()]
            else:
                self._event_categories = []
            event_subcats = config.get("event_subcategories")
            if event_subcats:
                self._event_subcategories = [
                    str(subcat).strip().replace(" ", "_").upper() for subcat in event_subcats.split(",") if subcat.strip()
                ]
            else:
                self._event_subcategories = []
            self._event_severity_lower = int(config.get("event_severity_lower"))
            self._event_severity_upper = int(config.get("event_severity_upper"))
            if self._event_severity_lower >= self._event_severity_upper:
                self.save_progress(
                    f"Initialization Failed: Invalid Range for Event Severity- {self._event_severity_lower} "
                    f"is not lower than {self._event_severity_upper}"
                )
                return phantom.APP_ERROR
            self._event_limit = int(config.get("event_limit"))
            self._store_event_notifs_in_alert_containers = config.get("store_event_notifs_in_alert_containers")

        return phantom.APP_SUCCESS

    def finalize(self):
        # Save the state, this data is saved across actions and app upgrades
        self.save_state(self._state)
        return phantom.APP_SUCCESS


if __name__ == "__main__":
    import sys

    with open(sys.argv[1]) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = IronnetConnector()
        connector.print_progress_message = True

        ret_val = connector._handle_action(json.dumps(in_json), None)
        print(json.dumps(json.loads(ret_val), indent=4))

    sys.exit(0)
