#!/usr/bin/env python

# Stdlib imports
import sqlite3, argparse, sys, logging, json, string, subprocess
import os, re, time, base64, random
from flask import Flask, request, jsonify, make_response, abort, url_for
from time import localtime, sleep
import hashlib


# Traficante imports
# TODO: add Traficante related imports
from utils import traficante

# Set up this module's logger
log = logging.getLogger(__name__)

# A lot of the code below was repurposed from the empire project, so thanks to them:
#    https://github.com/EmpireProject/Empire




def execute_db_query(conn, query, args=None):
    """
    Execute the supplied query on the provided db conn object with optional args for a paramterized query
    """
    cur = conn.cursor()
    if args:
        cur.execute(query, args)
    else:
        cur.execute(query)
    results = cur.fetchall()
    cur.close()
    return results


# TODO: If opt for the rest api, implement the logic to start it and assign mappings here.
#   Should probably focus on imeplementing the main logic first, then build a flask api around it

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # TODO: Determine what additional options would be useful to implement, then implement them
    traficante_options = parser.add_argument('Traficante Options')
    traficante_options.add_argument('-v', action='store_true', help='Enable verbose output',
                                       dest='verbose', default=False)

    args = parser.parse_args()

    # TODO: Implement a threading utility that can be used to start the eventual rest api
    # TODO: Implement the main menu

    main = traficante.MainMenu(args=args)
    traficante.cmdloop()

    # Cleanly exit once execution is done
    sys.exit()
