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


def make_tags(**kwargs):
    """
    For each kwarg, produce a {"Key": key, "Value": value}.
    """
    return [{"Key": key, "Value": value} for key, value in kwargs.items()]


main = {
    "AWSTemplateFormatVersion": "2010-09-09",

    "Description": "CloudFormation for newsreader.scraperwiki.com",

    "Parameters": {

        "InstanceType": {
            "Description": "WebServer EC2 instance type",
            "Type": "String",
            "Default": "t2.micro",
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

        "HostedZoneName": {
            "Default": "scraperwiki.com",
            "Description": "Top level domain to use.",
            "Type": "String",
        }
    },

    "Resources": {
        "NewsreaderSecurityGroup": {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "VpcId": ref('VpcId'),
                "Tags": make_tags(Name='Newsreader', Project='newsreader'),
                "GroupDescription": "Enable SSH, HTTP and HTTPS from everywhere",
                "SecurityGroupIngress": [
                    {"IpProtocol": "tcp", "FromPort": "22",
                     "ToPort": "22", "CidrIp": "0.0.0.0/0"},
                    {"IpProtocol": "tcp", "FromPort": "80",
                     "ToPort": "80", "CidrIp": "0.0.0.0/0"},
                    {"IpProtocol": "tcp", "FromPort": "443",
                     "ToPort": "443", "CidrIp": "0.0.0.0/0"},
                ]
            }
        },

        "NewsreaderInstance": {
            "Type": "AWS::EC2::Instance",
            "Properties": {
                "Tags": make_tags(Name='Newsreader', Project='newsreader'),
                "ImageId": COREOS_AMI,
                "SubnetId": ref('SubnetId'),
                "InstanceType": {"Ref": "InstanceType"},
                "SecurityGroupIds": [{"Ref": "NewsreaderSecurityGroup"}],
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
