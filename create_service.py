#!/usr/bin/env python
#

import requests
import json
import re
import argparse
import time
import os


def environ_or_required(key):
    return ({
        'default': os.environ.get(key)
    } if os.environ.get(key) else {
        'required': True
    })


parser = argparse.ArgumentParser(description='Create service in PagerDuty')
parser.add_argument(
    '--api_key', help='ApiKey PagerDuty', **environ_or_required('API_KEY'))
parser.add_argument(
    '--service_name',
    help='Service Name in PagerDuty',
    **environ_or_required('SERVICE_NAME'))
parser.add_argument(
    '--service_description',
    help='Short Description for service',
    **environ_or_required('SERVICE_DESCRIPTION'))
parser.add_argument(
    '--service_template',
    help='Template for service',
    **environ_or_required('SERVICE_TEMPLATE'))

parser.add_argument(
    '-d',
    '--debug',
    dest='debug',
    action='store_true',
    default=False,
    help='Run in debug mode')
parser.add_argument(
    '-a',
    '--show_api',
    dest='show_api',
    action='store_true',
    default=False,
    help='Show service api key')

args = parser.parse_args()

if not args.show_api:
    print("Input service_name: " + args.service_name)
    print("Input service_description: " + args.service_description)
    print("Input service_template: " + args.service_template)

# Update to match your API key
API_KEY = args.api_key

TEMPLATE_NAME = args.service_template
NAME = args.service_name
DESCRIPTION = args.service_description

# Update to match your chosen parameters
TEAM_IDS = []
TIME_ZONE = 'UTC'
SORT_BY = 'name'
QUERY = ''
INCLUDE = []


def pdebug(txt):
    if args.debug:
        print(txt)


def list_services():
    url = 'https://api.pagerduty.com/services'
    headers = {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': 'Token token={token}'.format(token=API_KEY)
    }
    payload = {
        'team_ids[]': TEAM_IDS,
        'time_zone': TIME_ZONE,
        'sort_by': SORT_BY,
        'query': QUERY,
        'include[]': INCLUDE
    }
    r = requests.get(url, headers=headers, params=payload)
    pdebug('Status Code: {code}'.format(code=r.status_code))
    if r.status_code not in range(200, 299):
        print("ERROR get services" + str(r))
        exit(2)

    pdebug(json.dumps(r.json(), indent=4, sort_keys=True))
    return r.json()


def get_service_byname(name, sysexit=False):
    l_services = list_services()
    s_names = ""
    for service in l_services['services']:
        s_names += service['name'] + ","
        if name.lower() == service['name'].lower():
            return service

    if sysexit:
        print("ERROR service not found: '" + name + "' possible options: [" +
              s_names + "]")
        exit(2)
    return None


def create_service(service_template, name, description):
    url = 'https://api.pagerduty.com/services'
    headers = {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': 'Token token={token}'.format(token=API_KEY),
        'Content-type': 'application/json'
    }
    payload = {
        'service': {
            'name':
            name,
            'description':
            description,
            'escalation_policy': {
                'id': service_template['escalation_policy']['id'],
                'type': 'escalation_policy'
            },
            'type':
            service_template['type'],
            'auto_resolve_timeout':
            service_template['auto_resolve_timeout'],
            'acknowledgement_timeout':
            service_template['acknowledgement_timeout'],
            'teams':
            service_template['teams'],
            'scheduled_actions':
            service_template['scheduled_actions'],
            'integrations':
            service_template['escalation_policy'],
            'addons':
            service_template['addons'],
            'support_hours':
            service_template['support_hours'],
            'incident_urgency_rule':
            service_template['incident_urgency_rule'],
            "alert_creation":
            "create_alerts_and_incidents"
        }
    }
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    pdebug('Status Code: {code}'.format(code=r.status_code))
    pdebug(r.json())


def create_integration(service_id, name, summary, itype, integration_email=''):
    # itype='events_api_v2_inbound_integration'
    # itype='generic_email_inbound_integration'
    url = 'https://api.pagerduty.com/services/{id}/integrations'.format(
        id=service_id)
    headers = {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': 'Token token={token}'.format(token=API_KEY),
        'Content-type': 'application/json'
    }
    payload = {
        'integration': {
            'type': itype,
            'summary': summary,
            'name': name,
            'vendor': None
        }
    }
    if itype == 'generic_email_inbound_integration':
        payload['integration']['integration_email'] = integration_email
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    pdebug('Status Code: {code}'.format(code=r.status_code))
    pdebug(r.json())


def get_service_integrations_byname(service, name):
    for integration in service['integrations']:
        if integration['summary'] == name:
            return integration
    return None


def get_api_key(self):
    headers = {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': 'Token token={token}'.format(token=API_KEY),
        'Content-type': 'application/json'
    }
    r = requests.get(self, headers=headers)
    pdebug('Status Code: {code}'.format(code=r.status_code))

    return r.json()


if __name__ == '__main__':
    service_template = get_service_byname(TEMPLATE_NAME, True)
    pdebug(json.dumps(service_template, indent=4, sort_keys=True))
    if get_service_byname(NAME) is None:
        create_service(service_template, NAME, DESCRIPTION)

    new_service = get_service_byname(NAME)
    pdebug(json.dumps(new_service, indent=4, sort_keys=True))
    if not args.show_api:
        print("Pager duty service name: " + new_service['name'])
    pg_domain = re.search("https?://(?P<url>[^\s/]+)",
                          new_service['html_url']).group("url")
    pdebug('id:' + new_service['id'] + ' html_url:' + new_service['html_url'] +
           ' pg_domain:' + pg_domain)

    # create email
    integration_name = "email_" + NAME
    integration_description = "Email integration for " + NAME
    integration_email = NAME + "@" + pg_domain
    if get_service_integrations_byname(new_service, integration_name) is None:
        create_integration(
            new_service['id'], integration_name, integration_description,
            'generic_email_inbound_integration', integration_email)

    # create api2
    integration_name = "api_" + NAME
    integration_description = "Api integration for " + NAME
    if get_service_integrations_byname(new_service, integration_name) is None:
        create_integration(new_service['id'], integration_name,
                           integration_description,
                           'events_api_v2_inbound_integration')

    if args.show_api:
        # get api2 key
        for x in range(0, 10):
            nservice = get_service_byname(
                NAME
            )  # get service again old one missing inntegrations (created before)
            api_self = get_service_integrations_byname(nservice,
                                                       integration_name)
            if api_self and 'self' in api_self:
                api_result = get_api_key(api_self['self'])

                print('api_integration_key: ' +
                      api_result['integration']['integration_key'])
                break
            else:
                pdebug("sleep")
                time.sleep(10)
