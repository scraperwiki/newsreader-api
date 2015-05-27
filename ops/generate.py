#!/usr/bin/env pypy
from __future__ import print_function

import json
import os
import sys

stdout = sys.stdout
sys.stdout = sys.stderr

# We use pypy so that dictionary order is preserved.
# pypy2 preserves dictionary order everywhere! Even for kwargs!
# A convenient docker container is provided if you just run 'make'.
assert "pypy" in sys.executable, "DO NOT PROCEED."

# CoreOS version 633.1.0
COREOS_AMI = "ami-21422356"


def ref(x):
    return {'Ref': x}


def join(*args, **kwargs):
    """
    Return an intrinsic joining each argument together with an empty seperator.
    join("foo", bar) is shorthand for:
    {"Fn::Join": ["", list(("foo", bar))]}
    """
    sep = kwargs.pop("sep", "")
    assert not kwargs, "unknown params specified: {}".format(kwargs.keys())
    return {"Fn::Join": [sep, list(args)]}


main = {
    "AWSTemplateFormatVersion": "2010-09-09",

    "Description": "CloudFormation for newsreader.scraperwiki.com",

    "Parameters": {

        "InstanceType": {
            "Description": "WebServer EC2 instance type",
            "Type": "String",
            "Default": "m1.small",
        },

        "NewsreaderUsername": {
            "Description": "Newsreader SPARQL username",
            "Type": "String",
        },

        "NewsreaderPassword": {
            "Description": "Newsreader SPARQL password",
            "Type": "String",
        },

        "NewsreaderSimpleApiKey": {
            "Description": "Newsreader Simple API keys",
            "Type": "String",
        },

        "VpcId": {
            "Description": "",
            "Type": "AWS::EC2::VPC::Id",
        },

        "SubnetId": {
            "Description": "",
            "Type": "AWS::EC2::Subnet::Id",
        },

    },

    "Resources": {
        "WebServerSecurityGroup": {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "Enable HTTP access via port 80 locked down to the load balancer + SSH access",
                "SecurityGroupIngress": [
                    {"IpProtocol": "tcp", "FromPort": "80",
                     "ToPort": "80", "CidrIp": "0.0.0.0/0"},
                    {"IpProtocol": "tcp", "FromPort": "22",
                     "ToPort": "22", "CidrIp": {"Ref": "SSHLocation"}}
                ]
            }
        },

        "NewsreaderInstance": {
            "Type": "AWS::EC2::Instance",
            "Properties": {
                "ImageId": COREOS_AMI,
                "InstanceType": {"Ref": "InstanceType"},
                "SecurityGroups": [{"Ref": "NewsreaderSecurityGroup"}],
                "UserData": {"Fn::Base64": {"Fn::Join": ["", [
                    "#cloud-config\n",
                    "users:\n",
                    "  - name: pwaller\n",
                    "    groups: [sudo, docker, systemd-journal]\n",
                    "    coreos-ssh-import-github: pwaller\n",
                    "  - name: drj\n",
                    "    groups: [sudo, docker, systemd-journal]\n",
                    "    coreos-ssh-import-github: drj11\n",
                    "  - name: frabcus\n",
                    "    groups: [sudo, docker, systemd-journal]\n",
                    "    coreos-ssh-import-github: frabcus\n",
                    "  - name: dragon\n",
                    "    groups: [sudo, docker, systemd-journal]\n",
                    "    coreos-ssh-import-github: scraperdragon\n",
                    "  - name: sm\n",
                    "    groups: [sudo, docker, systemd-journal]\n",
                    "    coreos-ssh-import-github: StevenMaude\n",
                ]]}}
            },
        },

        "NewsreaderDNS": {
            "Type": "AWS::Route53::RecordSet",
            "Properties": {
                "HostedZoneName": join(ref("HostedZoneName"), "."),
                "Comment": "DNS name for newsreader.scraperwiki.com",

                # e.g, newsreader-20150413-pw-dev-eu-west-1.scraperwiki.com
                "Name": join(
                    join(
                        ref("AWS::StackName"),
                        ref("AWS::Region"),
                        sep="-",
                    ),
                    ref("HostedZoneName"),
                    "",  # Must end with a ".", so join empty.
                    sep="."
                ),
                "Type": "A",
                "TTL": "60",
                "ResourceRecords": [
                    {'Fn::GetAtt': ['NewsreaderInstance', 'PublicIp']},
                ],
            },
        },
    },

    "Outputs": {
        "NewsreaderDNS": {
            "Value": ref("NewsreaderDNS"),
            "Description": "DNS name of Newsreader instance"
        }
    }
}

json.dump(main, stdout, indent=2)
stdout.write('\n')
