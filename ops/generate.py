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

main = {
    "AWSTemplateFormatVersion": "2010-09-09",

    "Description": "CloudFormation for newsreader.scraperwiki.com",

    "Parameters": {

        "InstanceType": {
            "Description": "WebServer EC2 instance type",
            "Type": "String",
            "Default": "m1.small",
        },

        "NEWSREADER_USERNAME": {
            "Description": "Newsreader SPARQL username",
            "Type": "String",
        },

        "NEWSREADER_PASSWORD": {
            "Description": "Newsreader SPARQL password",
            "Type": "String",
        },

        "NEWSREADER_SIMPLE_API_KEY": {
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

        "WebServer": {
            "Type": "AWS::EC2::Instance",
            "Metadata": {
                "AWS::CloudFormation::Init": {
                    "configSets": {
                        "wordpress_install": ["install_cfn", "install_wordpress", "configure_wordpress"]
                    },
                    "install_cfn": {
                        "files": {
                            "/etc/cfn/cfn-hup.conf": {
                                "content": {"Fn::Join": ["", [
                                    "[main]\n",
                                    "stack=", {"Ref": "AWS::StackId"}, "\n",
                                    "region=", {"Ref": "AWS::Region"}, "\n"
                                ]]},
                                "mode": "000400",
                                "owner": "root",
                                "group": "root"
                            },
                            "/etc/cfn/hooks.d/cfn-auto-reloader.conf": {
                                "content": {"Fn::Join": ["", [
                                    "[cfn-auto-reloader-hook]\n",
                                    "triggers=post.update\n",
                                    "path=Resources.WebServer.Metadata.AWS::CloudFormation::Init\n",
                                    "action=/opt/aws/bin/cfn-init -v ",
                                    "         --stack ", {"Ref":
                                                          "AWS::StackName"},
                                    "         --resource WebServer ",
                                    "         --configsets wordpress_install ",
                                    "         --region ", {"Ref":
                                                           "AWS::Region"}, "\n"
                                ]]},
                                "mode": "000400",
                                "owner": "root",
                                "group": "root"
                            }
                        },
                        "services": {
                            "sysvinit": {
                                "cfn-hup": {"enabled": "true", "ensureRunning": "true",
                                            "files": ["/etc/cfn/cfn-hup.conf", "/etc/cfn/hooks.d/cfn-auto-reloader.conf"]}
                            }
                        }
                    },

                    "install_wordpress": {
                        "packages": {
                            "yum": {
                                "php": [],
                                "php-mysql": [],
                                "mysql": [],
                                "mysql-server": [],
                                "mysql-devel": [],
                                "mysql-libs": [],
                                "httpd": []
                            }
                        },
                        "sources": {
                            "/var/www/html": "http://wordpress.org/latest.tar.gz"
                        },
                        "files": {
                            "/tmp/setup.mysql": {
                                "content": {"Fn::Join": ["", [
                                    "CREATE DATABASE ", {
                                        "Ref": "DBName"}, ";\n",
                                    "CREATE USER '", {"Ref": "DBUser"}, "'@'localhost' IDENTIFIED BY '", {
                                        "Ref": "DBPassword"}, "';\n",
                                    "GRANT ALL ON ", {
                                        "Ref": "DBName"}, ".* TO '", {"Ref": "DBUser"}, "'@'localhost';\n",
                                    "FLUSH PRIVILEGES;\n"
                                ]]},
                                "mode": "000400",
                                "owner": "root",
                                "group": "root"
                            },

                            "/tmp/create-wp-config": {
                                "content": {"Fn::Join": ["", [
                                    "#!/bin/bash -xe\n",
                                    "cp /var/www/html/wordpress/wp-config-sample.php /var/www/html/wordpress/wp-config.php\n",
                                    "sed -i \"s/'database_name_here'/'", {
                                        "Ref": "DBName"}, "'/g\" wp-config.php\n",
                                    "sed -i \"s/'username_here'/'", {
                                        "Ref": "DBUser"}, "'/g\" wp-config.php\n",
                                    "sed -i \"s/'password_here'/'", {
                                        "Ref": "DBPassword"}, "'/g\" wp-config.php\n"
                                ]]},
                                "mode": "000500",
                                "owner": "root",
                                "group": "root"
                            }
                        },
                        "services": {
                            "sysvinit": {
                                "httpd": {"enabled": "true", "ensureRunning": "true"},
                                "mysqld": {"enabled": "true", "ensureRunning": "true"}
                            }
                        }
                    },

                    "configure_wordpress": {
                        "commands": {
                            "01_set_mysql_root_password": {
                                "command": {"Fn::Join": ["", ["mysqladmin -u root password '", {"Ref": "DBRootPassword"}, "'"]]},
                                "test": {"Fn::Join": ["", ["$(mysql ", {"Ref": "DBName"}, " -u root --password='", {"Ref": "DBRootPassword"}, "' >/dev/null 2>&1 </dev/null); (( $? != 0 ))"]]}
                            },
                            "02_create_database": {
                                "command": {"Fn::Join": ["", ["mysql -u root --password='", {"Ref": "DBRootPassword"}, "' < /tmp/setup.mysql"]]},
                                "test": {"Fn::Join": ["", ["$(mysql ", {"Ref": "DBName"}, " -u root --password='", {"Ref": "DBRootPassword"}, "' >/dev/null 2>&1 </dev/null); (( $? != 0 ))"]]}
                            },
                            "03_configure_wordpress": {
                                "command": "/tmp/create-wp-config",
                                "cwd": "/var/www/html/wordpress"
                            }
                        }
                    }
                }
            },
            "Properties": {
                "ImageId": {"Fn::FindInMap": ["AWSRegionArch2AMI", {"Ref": "AWS::Region"},
                                              {"Fn::FindInMap": ["AWSInstanceType2Arch", {"Ref": "InstanceType"}, "Arch"]}]},
                "InstanceType": {"Ref": "InstanceType"},
                "SecurityGroups": [{"Ref": "WebServerSecurityGroup"}],
                "KeyName": {"Ref": "KeyName"},
                "UserData": {"Fn::Base64": {"Fn::Join": ["", [
                    "#!/bin/bash -xe\n",
                    "yum update -y aws-cfn-bootstrap\n",

                    "/opt/aws/bin/cfn-init -v ",
                    "         --stack ", {"Ref": "AWS::StackName"},
                    "         --resource WebServer ",
                    "         --configsets wordpress_install ",
                    "         --region ", {"Ref": "AWS::Region"}, "\n",

                    "/opt/aws/bin/cfn-signal -e $? ",
                    "         --stack ", {"Ref": "AWS::StackName"},
                    "         --resource WebServer ",
                    "         --region ", {"Ref": "AWS::Region"}, "\n"
                ]]}}
            },
            "CreationPolicy": {
                "ResourceSignal": {
                    "Timeout": "PT15M"
                }
            }
        }
    },

    "Outputs": {
        "WebsiteURL": {
            "Value": {"Fn::Join": ["", ["http://", {"Fn::GetAtt": ["WebServer", "PublicDnsName"]}, "/wordpress"]]},
            "Description": "WordPress Website"
        }
    }
}

json.dump(main, stdout, indent=2)
stdout.write('\n')
