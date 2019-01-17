#!/usr/bin/env python3
"""
Copyright 2018 Akamai Technologies, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This script assumes you have python3 installed on your machine.  If
you don't have it installed on your Mac, it is easily available by
installing it with Brew.  https://brew.sh
"""

import inspect
import csv
import json
import os
from urllib.parse import urljoin
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import configparser
from akamai.edgegrid import EdgeGridAuth, EdgeRc
import jsonpatch
import requests

VERSION = '1.0.0'

def papi_groups(account_key, verbose):
    """ Getting a list of groups """

    gssapi = ''
    if account_key:
        gssapi = '?accountSwitchKey=' + account_key
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result = session.get(urljoin(BASEURL, '/papi/v1/groups' + gssapi))

    # Get result of dictionaries and put them into a list
    list_dict = result.json()

    verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name, [account_key])
    success_check(result.status_code, "200", list_dict, verbose)

    print('accountId:', list_dict["accountId"])
    print('accountName:', list_dict["accountName"])
    print('Groups:')
    sorted_groups = sorted(list_dict["groups"]["items"], key=lambda x: x['groupName'])
    print('\t', 'groupName;', 'groupId;', 'parentGroupId;')
    for items in sorted_groups:
        parent_id = items["parentGroupId"] if "parentGroupId" in items else "n/a"
        print('\t', items['groupName'] + ';', items['groupId'] + ';', parent_id + ';')
    print('\n')


def papi_contracts(account_key, verbose):
    """ Getting a list of contracts """

    gssapi = ''
    if account_key:
        gssapi = '?accountSwitchKey=' + account_key
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result = session.get(urljoin(BASEURL, '/papi/v1/contracts' + gssapi))

    # Get result of dictionaries and put them into a list
    list_dict = result.json()

    verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name, [account_key])
    success_check(result.status_code, "200", list_dict, verbose)

    print('accountId:', list_dict["accountId"])
    print('Contracts:')
    list_parse(list_dict["contracts"]["items"], verbose)
    print('\n')


def papi_products(account_key, cid, verbose):
    """ Getting a list of products """

    if not cid:
        print('Contract ID is required to get a list of Products.  '
              'To get a list of contracts, use "./' +
              os.path.basename(__file__) + ' contracts"', '\n')
        raise SystemExit

    gssapi = ''
    if account_key:
        gssapi = '&accountSwitchKey=' + account_key
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result = session.get(urljoin(BASEURL, '/papi/v1/products?contractId=' + cid + gssapi))

    # Get result of dictionaries and put them into a list
    list_dict = result.json()

    verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name, [account_key, cid])
    success_check(result.status_code, "200", list_dict, verbose)

    print('accountId:', list_dict["accountId"])
    print('contractId:', list_dict["contractId"])
    print('Products:')
    sorted_groups = sorted(list_dict["products"]["items"], key=lambda x: x['productName'])
    print('\t', 'productName;', 'productId;')
    for items in sorted_groups:
        print('\t', items['productName']+';', items['productId']+';')
    print('\n')


def papi_cpcodes(account_key, cid, gid, verbose):
    """ Getting a list of all CPCodes within a group """

    if not cid:
        print('Contract ID is required to get a list of CPCodes.  '
              'To get a list of contracts, use "./' +
              os.path.basename(__file__) + ' contracts"', '\n')
        raise SystemExit
    if not gid:
        print('Group ID is required to get a list of CPCodes.  '
              'To get a list of groups, use "./' +
              os.path.basename(__file__) + ' groups"', '\n')
        raise SystemExit

    gssapi = ''
    if account_key:
        gssapi = '&accountSwitchKey=' + account_key
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result = session.get(urljoin(BASEURL, '/papi/v1/cpcodes?contractId=' + cid +
                                 '&groupId=' + gid + gssapi))

    # Get result of dictionaries and put them into a list
    list_dict = result.json()

    verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name,
                  [account_key, cid, gid])
    success_check(result.status_code, "200", list_dict, verbose)

    print('accountId:', list_dict["accountId"])
    print('contractId:', list_dict["contractId"])
    print('groupId:', list_dict["groupId"])
    print('CPCodes:')
    sorted_groups = sorted(list_dict["cpcodes"]["items"], key=lambda x: x['cpcodeName'])
    print('\t', 'cpcodeName;', 'cpcodeId;', 'productIds;', 'createdDate;')
    for items in sorted_groups:
        print('\t', items['cpcodeName']+';', items['cpcodeId']+';',
              str(items['productIds'])+';', items['createdDate']+';')
    print('\n')


def papi_newcpcode(account_key, cid, gid, prd, cpname, verbose):
    """ Requesting a new CPCode """

    if not cid:
        print('Contract ID is required to make a new CPCode.  '
              'To get a list of contracts, use "./' +
              os.path.basename(__file__) + ' contracts"', '\n')
        raise SystemExit
    if not gid:
        print('Group ID is required to make a new CPCode.  '
              'To get a list of groups, use "./' +
              os.path.basename(__file__) + ' groups"', '\n')
        raise SystemExit
    if not prd:
        print('Product ID is required to make a new CPCode.  '
              'To get a list of products, use "./' +
              os.path.basename(__file__) + ' products"', '\n')
        raise SystemExit
    if not cpname:
        print('A CPCode Name is required to make a new CPCode', '\n')
        raise SystemExit

    data = '{"productId": "' + prd + '","cpcodeName": "' + cpname + '"}'
    headers = {'Content-Type': 'application/json'}

    gssapi = ''
    if account_key:
        gssapi = '&accountSwitchKey=' + account_key
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result = session.post(urljoin(BASEURL, '/papi/v1/cpcodes?contractId=' + cid +
                                  '&groupId=' + gid + gssapi), data=(data), headers=headers)

    # Get result of dictionaries and put them into a list
    list_dict = result.json()

    verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name,
                  [account_key, cid, gid, prd, cpname])
    success_check(result.status_code, "201", list_dict, verbose)

    if list_dict["cpcodeLink"]:
        string = list_dict["cpcodeLink"]
        paths = string.split('?')
        subpaths = paths[0].split('/')
        print("Your new CPCode is: " + subpaths[4].replace("cpc_", ""))
        papi_status(string, inspect.currentframe().f_code.co_name, verbose)


def papi_properties(account_key, cid, gid, verbose):
    """ Getting a list of properties """

    if not cid:
        print('Contract ID is required to get a list of properties.  '
              'To get a list of contracts, use "./' +
              os.path.basename(__file__) + ' contracts"', '\n')
        raise SystemExit
    if not gid:
        print('Group ID is required to get a list of properties.  '
              'To get a list of groups, use "./' +
              os.path.basename(__file__) + ' groups"', '\n')
        raise SystemExit

    gssapi = ''
    if account_key:
        gssapi = '&accountSwitchKey=' + account_key
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result = session.get(urljoin(BASEURL, '/papi/v1/properties?contractId=' + cid +
                                 '&groupId=' + gid + gssapi))

    # Get result of dictionaries and put them into a list
    list_dict = result.json()

    verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name,
                  [account_key, cid, gid])
    success_check(result.status_code, "200", list_dict, verbose)

    print('Properties:')
    sorted_groups = sorted(list_dict["properties"]["items"], key=lambda x: x['propertyName'])
    print('\t', 'propertyName;', 'propertyId;', 'Latest;', 'Staging;', 'Production;')
    for items in sorted_groups:
        print('\t', items['propertyName'] + ';', items['propertyId'] + ';',
              str(items['latestVersion']) + ';', str(items['stagingVersion']) + ';',
              str(items['productionVersion'])+';')
    print('\n')


def papi_property(account_key, cid, gid, pid, vid, verbose):
    """ Getting a property config information """

    if not cid:
        print('Contract ID is required to get a property\'s configuration.  '
              'To get a list of contracts, use "./' +
              os.path.basename(__file__) + ' contracts"', '\n')
        raise SystemExit
    if not gid:
        print('Group ID is required to get a property\'s configuration.  '
              'To get a list of groups, use "./' +
              os.path.basename(__file__) + ' groups"', '\n')
        raise SystemExit
    if not pid:
        print('Property ID is required to get a property\'s configuration.  '
              'To get a list of properties, use "./' +
              os.path.basename(__file__) + ' properties"', '\n')
        raise SystemExit

    gssapi = ''
    if account_key:
        gssapi = '&accountSwitchKey=' + account_key
    if not vid:
        session = requests.Session()
        session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
        result = session.get(urljoin(BASEURL, '/papi/v1/properties/' + pid + '?contractId=' +
                                     cid + '&groupId=' + gid + gssapi))

        # Get result of dictionaries and put them into a list
        list_dict = result.json()

        verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name,
                      [account_key, cid, gid, pid, vid])
        success_check(result.status_code, "200", list_dict, verbose)

        list_parse(list_dict["properties"]["items"], verbose)
        print('\n')
    else:
        session = requests.Session()
        session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
        result = session.get(urljoin(BASEURL, '/papi/v1/properties/' + pid + '/versions/' + vid +
                                     '?contractId=' + cid + '&groupId=' + gid + gssapi))

        # Get result of dictionaries and put them into a list
        list_dict = result.json()

        verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name,
                      [account_key, cid, gid, pid, vid])
        success_check(result.status_code, "200", list_dict, verbose)

        list_parse(list_dict["versions"]["items"], verbose)
        print('\n')


def papi_edgehostnames(account_key, cid, gid, verbose):
    """ Getting a list of edge Hostnames """

    if not cid:
        print('Contract ID is required to get a list of Edge Hostnames.  '
              'To get a list of contracts, use "./' +
              os.path.basename(__file__) + ' contracts"', '\n')
        raise SystemExit
    if not gid:
        print('Group ID is required to get a list of Edge Hostnames.  '
              'To get a list of groups, use "./' +
              os.path.basename(__file__) + ' groups"', '\n')
        raise SystemExit

    gssapi = ''
    if account_key:
        gssapi = '&accountSwitchKey=' + account_key
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result = session.get(urljoin(BASEURL, '/papi/v1/edgehostnames?contractId=' + cid +
                                 '&groupId=' + gid + '&options=mapDetails' + gssapi))

    # Get result of dictionaries and put them into a list
    list_dict = result.json()

    verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name,
                  [account_key, cid, gid])
    success_check(result.status_code, "200", list_dict, verbose)

    print('accountId:', list_dict["accountId"])
    print('contractId:', list_dict["contractId"])
    print('groupId:', list_dict["groupId"])
    print('Edge Hostnames:')
    sorted_groups = sorted(list_dict["edgeHostnames"]["items"],
                           key=lambda x: x['edgeHostnameDomain'])
    print('\t', 'edgeHostnameDomain;', 'edgeHostnameId;', 'productId;', 'domainPrefix;',
          'domainSuffix;', 'status;', 'secure;', 'SerialNumber;', 'SlotNumber;', 'Map Domain;')
    for items in sorted_groups:
        product_id = items['productId'] if "productId" in items else "n/a"
        status = items['status'] if "status" in items else "n/a"
        slot_number = items['mapDetails:slotNumber'] if "mapDetails:slotNumber" in items else "n/a"
        print(
            '\t',
            items['edgeHostnameDomain'] + ';',
            items['edgeHostnameId']+';',
            product_id + ';',
            items['domainPrefix'] + ';',
            items['domainSuffix'] + ';',
            status + ';',
            str(items['secure']) + ';',
            str(items['mapDetails:serialNumber']) + ';',
            str(slot_number) + ';',
            items['mapDetails:mapDomain'] + ';'
            )
    print('\n')


def papi_versions(account_key, cid, gid, pid, verbose):
    """ Getting a list of versions of a config """

    if not cid:
        print('Contract ID is required to get a list of property versions.  '
              'To get a list of contracts, use "./' +
              os.path.basename(__file__) + ' contracts"', '\n')
        raise SystemExit
    if not gid:
        print('Group ID is required to get a list of property versions.  '
              'To get a list of groups, use "./' +
              os.path.basename(__file__) + ' groups"', '\n')
        raise SystemExit
    if not pid:
        print('Property ID is required to get a list of property versions.  '
              'To get a list of properties, use "./' +
              os.path.basename(__file__) + ' properties"', '\n')
        raise SystemExit

    gssapi = ''
    if account_key:
        gssapi = '&accountSwitchKey=' + account_key
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result = session.get(urljoin(BASEURL, '/papi/v1/properties/' + pid + '/versions?contractId=' +
                                 cid + '&groupId=' + gid + gssapi))

    # Get result of dictionaries and put them into a list
    list_dict = result.json()

    verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name,
                  [account_key, cid, gid, pid])
    success_check(result.status_code, "200", list_dict, verbose)

    print('accountId:', list_dict["accountId"])
    print('contractId:', list_dict["contractId"])
    print('groupId:', list_dict["groupId"])
    print('Versions:')
    sorted_groups = sorted(list_dict["versions"]["items"], key=lambda x: x['propertyVersion'],
                           reverse=True)
    print('\t', 'propertyVersion;', 'updatedDate;', 'updatedByUser;', 'productionStatus;',
          'stagingStatus;', 'ruleFormat;', 'notes;')
    for items in sorted_groups[:10]:
        note = items['note'] if "note" in items else "n/a"
        print(
            '\t',
            str(items['propertyVersion']) + ';',
            items['updatedDate'] + ';',
            items['updatedByUser'] + ';',
            items['productionStatus'] + ';',
            items['stagingStatus'] + ';',
            items['ruleFormat'] + ';',
            note + ';'
            )
    print('\n')


def papi_config(account_key, cid, gid, pid, vid, verbose):
    """ Getting a config detail in JSON format """

    if not cid or not gid or not pid or not vid:
        print('Contract ID, Group ID, Property ID, and Version ID is required to get a the '
              'property config details.  This will be printed in JSON format.')
        raise SystemExit

    gssapi = ''
    if account_key:
        gssapi = '&accountSwitchKey=' + account_key
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result = session.get(urljoin(BASEURL, '/papi/v1/properties/' + pid + '/versions/' + vid +
                                 '/rules?contractId=' + cid + '&groupId=' + gid + gssapi))

    # Get result of dictionaries and put them into a list
    list_dict = result.json()

    verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name,
                  [account_key, cid, gid, pid, vid])
    success_check(result.status_code, "200", list_dict, verbose)

    print(json.dumps(list_dict))


def papi_latest(account_key, cid, gid, pid, version_source, verbose):
    """ Not doing any checks because you should call this directly.  There is no value. """

    gssapi = ''
    if account_key:
        gssapi = '&accountSwitchKey=' + account_key
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result = session.get(urljoin(BASEURL, '/papi/v1/properties/' + pid + '?contractId=' + cid +
                                 '&groupId=' + gid + gssapi))

    # Get result of dictionaries and put them into a list
    list_dict = result.json()

    verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name,
                  [account_key, cid, gid, pid, version_source])
    success_check(result.status_code, "200", list_dict, verbose)

    if version_source == "PRODUCTION":
        source_json = json.dumps(list_dict["properties"]["items"][0]["productionVersion"])
    elif version_source == "STAGING":
        source_json = json.dumps(list_dict["properties"]["items"][0]["stagingVersion"])
    else:
        source_json = json.dumps(list_dict["properties"]["items"][0]["latestVersion"])

    return source_json


def papi_etag(account_key, cid, gid, pid, vid, verbose):
    """ Not doing any checks because you should call this directly.  There is no value. """

    gssapi = ''
    if account_key:
        gssapi = '&accountSwitchKey=' + account_key
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result = session.get(urljoin(BASEURL, '/papi/v1/properties/' + pid + '/versions/' + vid +
                                 '?contractId=' + cid + '&groupId=' + gid + gssapi))

    # Get result of dictionaries and put them into a list
    list_dict = result.json()

    verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name,
                  [account_key, cid, gid, pid, vid])
    success_check(result.status_code, "200", list_dict, verbose)

    return json.dumps(list_dict["versions"]["items"][0]["etag"])


def papi_newconfig(account_key, cid, gid, pid, version_source, verbose):
    """ Creating a new config from Latest, Staging, or Production """

    if not cid:
        print('Contract ID is required to create a new property version.  '
              'To get a list of contracts, use "./' +
              os.path.basename(__file__) + ' contracts"', '\n')
        raise SystemExit
    if not gid:
        print('Group ID is required to create a new property version.  '
              'To get a list of groups, use "./' +
              os.path.basename(__file__) + ' groups"', '\n')
        raise SystemExit
    if not pid:
        print('Property ID is required to create a new property version.  '
              'To get a list of properties, use "./' +
              os.path.basename(__file__) + ' properties"', '\n')
        raise SystemExit

    vid = papi_latest(account_key, cid, gid, pid, version_source, verbose)
    etag = papi_etag(account_key, cid, gid, pid, vid, verbose)

    data = '{"createFromVersion": ' + vid + ',"createFromVersionEtag": ' + etag + '}'
    headers = {'Content-Type': 'application/json'}

    gssapi = ''
    if account_key:
        gssapi = '&accountSwitchKey=' + account_key
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result = session.post(urljoin(BASEURL, '/papi/v1/properties/' + pid +
                                  '/versions?contractId=' + cid + '&groupId=' + gid +
                                  gssapi), data=(data), headers=headers)

    # Get result of dictionaries and put them into a list
    list_dict = result.json()

    verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name,
                  [account_key, cid, gid, pid, version_source])
    success_check(result.status_code, "201", list_dict, verbose)

    if list_dict["versionLink"]:
        string = list_dict["versionLink"]
        paths = string.split('?')
        subpaths = paths[0].split('/')
        print("Your new version is: " + subpaths[6])
        papi_status(string, inspect.currentframe().f_code.co_name, verbose)
        print('\n')


def papi_rules(account_key, cid, gid, pid, vid, verbose):
    """ Not doing any checks because you should call this directly.  There is no value. """

    gssapi = ''
    if account_key:
        gssapi = '&accountSwitchKey=' + account_key
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result = session.get(urljoin(BASEURL, '/papi/v1/properties/' + pid + '/versions/' + vid +
                                 '/rules?contractId=' + cid + '&groupId=' + gid + gssapi))

    # Get result of dictionaries and put them into a list
    list_dict = result.json()

    verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name,
                  [account_key, cid, gid, pid, vid])
    success_check(result.status_code, "200", list_dict, verbose)

    # etag is needed for authentication
    etag = list_dict['etag']

    return (etag, list_dict)


def papi_hostnames(account_key, cid, gid, pid, vid, verbose):
    """ Not doing any checks because you should call this directly.  There is no value. """

    gssapi = ''
    if account_key:
        gssapi = '&accountSwitchKey=' + account_key
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result = session.get(urljoin(BASEURL, '/papi/v1/properties/' + pid + '/versions/' + vid +
                                 '/hostnames?contractId=' + cid + '&groupId=' + gid + gssapi))

    # Get result of dictionaries and put them into a list
    list_dict = result.json()

    verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name,
                  [account_key, cid, gid, pid, vid])
    success_check(result.status_code, "200", list_dict, verbose)

    # etag is needed for authentication
    etag = list_dict['etag']
    hosts = list_dict['hostnames']['items']

    return (etag, hosts)


def papi_patch(account_key, cid, gid, pid, vid, file, verbose):
    """ Special use case example to update hosts and rules on a config """

    if not cid or not gid or not pid or not vid or not file:
        print('Contract ID, Group ID, Property ID, Version ID, and a CSV file are required to '
              'batch patch a config.')
        raise SystemExit

    # Get the current saved version of the property config as our base
    src_rules = papi_rules(account_key, cid, gid, pid, vid, verbose)

    # Parse the CSV file to create a list of dictionaries that will be used
    # to update the CPCodes Rule
    patch_rules = []
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if len(row) >= 1: # the len(row) is the number of columns, not the total character count
                if line_count == 0:
                    print("Processing CSV file for Rules")
                    line_count += 1
                else:
                    patch_rules.append({"op": "add", "path": "/rules/children/0/children/0", "value": {"name": (row[0].strip()), "children": [], "behaviors": [{"name": "cpCode", "options": {"value": {"id": int(row[1].strip()), "name": (row[0].strip()), "description": (row[0].strip()), "products": ["SPM"]}}}], "criteria": [{"name": "hostname", "options": {"matchOperator": "IS_ONE_OF", "values": [(row[0].strip())]}}], "criteriaMustSatisfy": "all"}}.copy())
                    line_count += 1
        print("\tProcessed " + str(line_count - 1) + " rows")

    # pulling everything together for the final save
    rules_etag = src_rules[0]

    # using JsonPatch only for Rules, not hosts
    patch_rules = jsonpatch.JsonPatch(patch_rules)
    rules_data = json.dumps(patch_rules.apply(src_rules[1]))

    # Headers for Content-Type and If-Match verification.  If-Match header value must be wrapped
    # in double quotes.
    rules_headers = {"Content-Type": "application/json", "If-Match": quote(rules_etag)}

    # DO IT!
    gssapi = ''
    if account_key:
        gssapi = '&accountSwitchKey=' + account_key
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result = session.put(urljoin(BASEURL, '/papi/v1/properties/' + pid + '/versions/' + vid +
                                 '/rules?contractId=' + cid + '&groupId=' + gid +
                                 gssapi), data=(rules_data), headers=(rules_headers))

    # Get result of dictionaries and put them into a list
    list_dict = result.json()

    verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name,
                  [account_key, cid, gid, pid, vid, file])
    success_check(result.status_code, "200", list_dict, verbose)

    for keys, values in list_dict.items():
        if keys == "errors":
            for value in values:
                list_parse(value, verbose)
        elif keys == "propertyVersion":
            print("No Errors!  You have updated your rules on config version: " +
                  str(list_dict["propertyVersion"]))

    # Get the current saved version of the property config as our base
    src_hosts = papi_hostnames(account_key, cid, gid, pid, vid, verbose)

    # Parse the CSV file to create a list of dictionaries that will be used to
    # update the CPCodes Rule
    patch_hosts = []
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if len(row) >= 1: # the len(row) is the number of columns, not the total character count
                if line_count == 0:
                    print("Processing CSV file for Hosts")
                    line_count += 1
                else:
                    patch_hosts.append({"cnameType": "EDGE_HOSTNAME", "cnameFrom": (row[0].strip()), "cnameTo": (row[2].strip())}.copy())
                    line_count += 1
        print("\tProcessed " + str(line_count - 1) + " rows")

    # pulling everything together for the final save
    hosts_etag = src_hosts[0]

    # combining hosts lists
    patch_hosts = src_hosts[1] + patch_hosts
    hosts_data = json.dumps(patch_hosts)

    # Headers for Content-Type and If-Match verification.  If-Match header value must be wrapped
    # in double quotes.
    hosts_headers = {"Content-Type": "application/json", "If-Match": quote(hosts_etag)}

    # DO IT!
    gssapi = ''
    if account_key:
        gssapi = '&accountSwitchKey=' + account_key
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result_hosts = session.put(urljoin(BASEURL, '/papi/v1/properties/' + pid + '/versions/' + vid +
                                       '/hostnames?contractId=' + cid + '&groupId=' + gid +
                                       gssapi), data=(hosts_data), headers=(hosts_headers))

    # Get result of dictionaries and put them into a list
    list_dict2 = result_hosts.json()

    verbose_check(verbose, list_dict2, inspect.currentframe().f_code.co_name,
                  [account_key, cid, gid, pid, vid, file])
    success_check(result_hosts.status_code, "200", list_dict2, verbose)

    for keys, values in list_dict2.items():
        if keys == "errors":
            for value in values:
                list_parse(value, verbose)
        elif keys == "propertyVersion":
            print("No Errors!  You have updated your hosts on config version: " +
                  str(list_dict["propertyVersion"]))

    print('\n')


def papi_activate(account_key, cid, gid, pid, vid, network, email, verbose):
    """ activate a config to Staging or Production """

    if not pid or not gid or not pid or not vid:
        print('Contract ID, Group ID, Property ID, Version ID\
            are required to activate a config.')
        raise SystemExit
    if not network or not email:
        print('Akamai Network, and email address\
            are required to activate a config.')
        raise SystemExit

    data = '{"propertyVersion": ' + vid + ',"network": "' + network + '","note": "API activation","notifyEmails": ' + str(json.dumps(email)) + ',"acknowledgeAllWarnings": true,"useFastFallback": false}'
    if verbose != 'False' and network == "PRODUCTION":
        # Akamai Employees need Compliance notes when pushing to prod
        data = '{"propertyVersion": ' + vid + ',"network": "' + network + '","note": "API activation","notifyEmails": ' + str(json.dumps(email)) + ',"acknowledgeAllWarnings": true,"useFastFallback": false,"complianceRecord": {"noncomplianceReason": "NO_PRODUCTION_TRAFFIC"}}'
        print("You are brave sending a Verbose value of " + verbose)
        print("I'll format a non-compliant request to bypass an Akamai employee Change\
            Management requirement, as you wish.")
        print(data)
        print(" ")
    headers = {'Content-Type': 'application/json'}

    gssapi = ''
    if account_key:
        gssapi = '&accountSwitchKey=' + account_key
    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result = session.post(urljoin(BASEURL, '/papi/v1/properties/' + pid +
                                  '/activations?contractId=' + cid + '&groupId=' + gid +
                                  gssapi), data=(data), headers=headers)

    # Get result of dictionaries and put them into a list
    list_dict = result.json()

    verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name,
                  [account_key, cid, gid, pid, vid, network, email])
    success_check(result.status_code, "201", list_dict, verbose)

    if list_dict["activationLink"]:
        string = list_dict["activationLink"]
        print("Activation Request has been sent!  Checking on status...")
        papi_status(string, inspect.currentframe().f_code.co_name, verbose)

    print('\n')


def papi_status(path, stype, verbose):
    """ Not doing any checks because you should call this directly.  There is no value. """

    session = requests.Session()
    session.auth = EdgeGridAuth.from_edgerc(EDGERC, SECTION)
    result = session.get(urljoin(BASEURL, path))

    # Get result of dictionaries and put them into a list
    list_dict = result.json()

    verbose_check(verbose, list_dict, inspect.currentframe().f_code.co_name, [path, stype])
    success_check(result.status_code, "200", list_dict, verbose)

    if stype == "papi_activate":
        list_parse(list_dict["activations"]["items"], verbose)
    elif stype == "papi_newconfig":
        list_parse(list_dict["versions"]["items"], verbose)
    elif stype == "papi_newcpcode":
        list_parse(list_dict["cpcodes"]["items"], verbose)


def verbose_check(verbose, list_dict, function, variables):
    """ -vv will give more information on the python function """
    if verbose != 'False' and verbose >= '3':
        print(list_dict)
        print("\n")
    if verbose != 'False' and verbose >= '2':
        print("function", function, "(", str(variables), ") results\n")


def success_check(status, success, list_dict, verbose):
    """ checking to see if the response code matches what was requested (200/201 usually) """
    if str(status) == '403':
        print('You do not have the correct permission for this API call: (' + str(status) + ')')
        dict_parse(list_dict, verbose)
        raise SystemExit
    elif str(status) != success:
        print('Did not receive a', success, 'response code:', str(status))
        dict_parse(list_dict, verbose)
        print("\n")
        raise SystemExit


def list_parse(my_list, verbose):
    """ printing out a list with key/value pairs, usually when an error occurs """
    if verbose != 'False' and verbose >= '2':
        print("function", inspect.currentframe().f_code.co_name, "(", my_list, ") results\n")

    temporary_array = (json.dumps(my_list))
    for obj in json.loads(temporary_array):
        for key, value in obj.items():
            if key == 'target':
                print('\t', key + ':', value)
            else:
                print('\t\t', key + ':', value)


def dict_parse(my_dict, verbose):
    """ printing out key/value pairs, usually when an error occurs """
    if verbose != 'False' and verbose >= '2':
        print("function", inspect.currentframe().f_code.co_name, "(", my_dict, ") results\n")
    for key, value in sorted(my_dict.items()):
        print('\t', key, '=', value)


def quote(self):
    """ I cannot believe I'm hacking this to overcome an API 'requirement' """
    return '\"' + self + '\"'


if __name__ == "__main__":

    try:
        # Initial Argument Parser and add arguments
        PARSER = ArgumentParser(prog='AkaPAPI.py',
                                description="This script will allow you to collect info on Luna \
                                Groups, Akamai Contracts, Akamai Products, create CPCodes, manipulate \
                                Delivery configs, and activate Delivery configs.",
                                epilog="Use positional arguments first, then optional ones \
                                if needed.",
                                formatter_class=ArgumentDefaultsHelpFormatter)

        # Required to choose one
        PARSER.add_argument('command',
                            choices=[
                                'groups',
                                'contracts',
                                'products',
                                'cpcodes',
                                'new-cpcode',
                                'properties',
                                'property',
                                'edge-hostnames',
                                'versions',
                                'config',
                                'new-config',
                                'patch',
                                'activate'
                            ], help='Primary "Command": Use the "groups" and \
                            "contracts" commands first as they are needed for almost everything \
                            when using the PAPI API.  You will need to use the "products" \
                            command if you are creating a CPCode.')


        # Optional Script variables
        PARSER.add_argument('--cid', dest='cid',
                            help='Optional flag to identify the Contract ID (beginning with ctr_) \
                            when sending commands.')
        PARSER.add_argument('--gid', dest='gid',
                            help='Optional flag to identify the Group ID (beginning with grp_) \
                            when sending commands.')
        PARSER.add_argument('--pid', dest='pid',
                            help='Optional flag to identify the Property ID (beginning with prp_) \
                            when sending commands.')
        PARSER.add_argument('--vid', dest='vid',
                            help='Optional flag to identify the version number for a specific \
                            config.')
        PARSER.add_argument('--VERSION', dest='version_source', default="LATEST",
                            choices=['LATEST', 'STAGING', 'PRODUCTION'],
                            help='Optional flag used when creating a new version of a \
                            configuration, indicating which version to base the new \
                            version from.')
        PARSER.add_argument('--prd', dest='prd',
                            help='Optional flag that you can use to identify your Product in \
                            commands.  You need a product identifier to create new edge \
                            hostnames, CP codes, or properties.')
        PARSER.add_argument('--cpname', dest='cpname',
                            help='Optional flag that you can use to give your CPCode name when \
                            creating a CPCODE')
        PARSER.add_argument('--network', dest='network', default="STAGING",
                            choices=['STAGING', 'PRODUCTION'],
                            help='Optional flag specifying which Akamai Network to push the \
                            configuration.')
        PARSER.add_argument('--email', dest='email', action='append',
                            help='Optional flag that you can use to identify an email address in \
                            commands such as activating a config.  You can use multiple times to \
                            add additional email addresses. (E.X. --email user1@gov.mil \
                            --email user2@gov.mil)')
        PARSER.add_argument('--file', dest='file', default=False,
                            help='Optional flag that you can use for the "patch" command.  At \
                            this time the CSV file would be three columns: "hostname", "cpcode", \
                            and "edgekey name"')

        # Optional Environment Variables
        PARSER.add_argument('--edgerc', dest='edgerc', default=False, action="store",
                            help='Select your ".edgerc" file vs. the default assumption \
                            that it is located in your home directory')
        PARSER.add_argument('--section', dest='section', default='default',
                            help='If your ".edgerc" has multiple [sections], you can pick which \
                            section.')
        PARSER.add_argument('--account-key', dest='account_key',
                            help='Akamai Employees can switch accounts using their GSS API \
                            accountSwitchKey credentials.')
        PARSER.add_argument('-v', '--verbose', dest='verbose', action="count", default=False,
                            help='Optional flag to display extra fields from the Alert API request')
        PARSER.add_argument('-V', '--version', action='version',
                            version='%(prog)s {}'.format(VERSION),
                            help='Show the version of %(prog)s and exit')


        ARGS = PARSER.parse_args()

        # PICK AN EDGERC FILE
        if ARGS.edgerc:
            # If --edgerc option flag is declared, use that vs. the default
            EDGERC_PATH = (ARGS.edgerc)
        else:
            # Default .edgerc file is located in the users home directory
            EDGERC_PATH = (os.path.expanduser('~') + '/.edgerc')

        EDGERC = EdgeRc(EDGERC_PATH)
        SECTION = str(ARGS.section)

        # Error checking the .edgerc file
        if (EDGERC.get(SECTION, 'host').find('://')) > 0:
            print('You have an invalid entry on your --edgerc ' + EDGERC_PATH + ' file '\
                  'under your --section ' + SECTION + '.  '\
                  'Please remove the http(s):// at the beginning.', '\n')
            raise SystemExit

        BASEURL = 'https://%s' % EDGERC.get(SECTION, 'host')

        if str(ARGS.verbose) != 'False' and str(ARGS.verbose) >= '2':
            print("Command variables")
            print('\t', 'command: ' + str(ARGS.command), '\n',
                  '\t', '--cid: ' + str(ARGS.cid), '\n',
                  '\t', '--gid: ' + str(ARGS.gid), '\n',
                  '\t', '--pid: ' + str(ARGS.pid), '\n',
                  '\t', '--vid: ' + str(ARGS.vid), '\n',
                  '\t', '--VERSION: ' + str(ARGS.version_source), '\n',
                  '\t', '--prd: ' + str(ARGS.prd), '\n',
                  '\t', '--cpname: ' + str(ARGS.cpname), '\n',
                  '\t', '--network: ' + str(ARGS.network), '\n',
                  '\t', '--email: ' + str(ARGS.email), '\n',
                  '\t', '--file: ' + str(ARGS.file), '\n',
                  '\t', '--edgerc: ' + str(ARGS.edgerc), '\n',
                  '\t', '--section: ' + str(ARGS.section), '\n',
                  '\t', '--account-key: ' + str(ARGS.account_key), '\n',
                  '\t', '--verbose: ' + str(ARGS.verbose)
                  )
            print("\n")

        if (ARGS.command) == "groups":
            papi_groups(ARGS.account_key, str(ARGS.verbose))
        if (ARGS.command) == "contracts":
            papi_contracts(ARGS.account_key, str(ARGS.verbose))
        if (ARGS.command) == "products":
            papi_products(ARGS.account_key, ARGS.cid, str(ARGS.verbose))
        if (ARGS.command) == "cpcodes":
            papi_cpcodes(ARGS.account_key, ARGS.cid, ARGS.gid, str(ARGS.verbose))
        if (ARGS.command) == "new-cpcode":
            papi_newcpcode(ARGS.account_key, ARGS.cid, ARGS.gid, ARGS.prd,
                           ARGS.cpname, str(ARGS.verbose))
        if (ARGS.command) == "properties":
            papi_properties(ARGS.account_key, ARGS.cid, ARGS.gid, str(ARGS.verbose))
        if (ARGS.command) == "property":
            papi_property(ARGS.account_key, ARGS.cid, ARGS.gid, ARGS.pid,
                          ARGS.vid, str(ARGS.verbose))
        if (ARGS.command) == "edge-hostnames":
            papi_edgehostnames(ARGS.account_key, ARGS.cid, ARGS.gid, str(ARGS.verbose))
        if (ARGS.command) == "versions":
            papi_versions(ARGS.account_key, ARGS.cid, ARGS.gid, ARGS.pid, str(ARGS.verbose))
        if (ARGS.command) == "config":
            papi_config(ARGS.account_key, ARGS.cid, ARGS.gid, ARGS.pid, ARGS.vid, str(ARGS.verbose))
        if (ARGS.command) == "new-config":
            papi_newconfig(ARGS.account_key, ARGS.cid, ARGS.gid, ARGS.pid,
                           ARGS.version_source, str(ARGS.verbose))
        if (ARGS.command) == "patch":
            papi_patch(ARGS.account_key, ARGS.cid, ARGS.gid, ARGS.pid, ARGS.vid,
                       ARGS.file, str(ARGS.verbose))
        if (ARGS.command) == "activate":
            papi_activate(ARGS.account_key, ARGS.cid, ARGS.gid, ARGS.pid, ARGS.vid,
                          ARGS.network, ARGS.email, str(ARGS.verbose))

    except configparser.NoSectionError:
        print('The --section "' + SECTION + '" does not exist in your --edgerc "' +
              EDGERC_PATH + '" file.  Please try again.', '\n')
