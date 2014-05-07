#!/usr/bin/env python
# encoding: utf-8
from flask import Flask

app = Flask(__name__)
from app import views
