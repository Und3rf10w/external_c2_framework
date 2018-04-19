"""

Main controller class for Traficante

Contains the various menu loops
"""

import sys
import cmd
import sqlite3
import os
import hashlib
import time
import importlib
import base64
import threading
import json
import logging

from pydispatch import dispatcher

# local utils imports
import helpers
import messages
import sessions
import listeners
import configs

# Set up this module's logger
log = logging.getLogger(__name__)


# A lot of the following logic is repurposed from Empire

class NavMain(Exception):
    """
    Custom exception class abused to return back to the main menu
    """
    pass


class NavListeners(Exception):
    """
    Custom exception class to go to the listeners menu
    """
    pass


class NavSessions(Exception):
    """
    Custom exception class to go to the sessions menu
    """
    pass


class NavConfigs(Exception):
    """
    Custom exception class to go to the configs menu
    """
    pass

# TODO: implement any other menu return exceptions required


class MainMenu(cmd.Cmd):
    """
    The main class used by Traficante to drive the 'main' menu displayed when Traficante starts
    """
    def __init__(self, args=None):
        cmd.Cmd.__init__(self)

        # setup event handling
        dispatcher.connect(self.handle_event, sender=dispatcher.any)

        # traficante_options[option_name] = (value, required, description)
        self.traficante_options = {}

        # empty db object
        self.conn = self.database_connect()
        time.sleep(1)

        # Create the threading lock
        self.lock = threading.Lock()

        # TODO: parse common config info here, if any: https://github.com/EmpireProject/Empire/blob/master/lib/common/empire.py#L92

        # Set the prompt for the user
        self.prompt = '[Traficante]# '
        self.do_help.__func__.__doc__ = '''Displays help menu'''
        self.doc_header = 'Commands'

        # Set default menu state to 'Main'
        self.menu_state = 'Main'

        # Instantiate objects
        # TODO: fix this section
        self.sessions = sessions.Sessions(self, args=args)
        self.listeners = listeners.Listeners(self, args=args)
        self.configs = configs.Configs(self, args=args)
        self.resource_queue = []

        # Parse command line arguments
        self.args = args
        # TODO: actually parse arguments

        message = "[*] Traficante is booting..."
        signal = json.dumps({
            'print': True,
            'message': message
        })
        dispatcher.send(signal, sender="traficante")
        messages.loading()

    def get_db_connection(self):
        """
        Returns the db connection
        """
        self.lock.acquire()
        self.conn.row_factory = None
        self.lock.release()
        return self.conn

    def handle_event(self, signal, sender):
        """
        When an event is recieved from the dispatcher, log it to the DB, print it if needed
        :param signal: The actual message received from the sender
        :param sender: The dispatcher of the message
        """
        try:
            signal_data = json.loads(signal)
        except ValueError:
            log.error("[!] Error: bad signal recieved {} from sender {}".format(signal,sender))
            return

        # apply a timestamp if not set
        if 'timestamp' not in signal_data:
            signal_data['timestamp'] = helpers.get_datetime()

        # TODO: do we need a task_id? probably not?

        if 'event_type' in signal_data:
            event_type = signal_data['event_type']
        else:
            event_type = 'dispatched_event'

        event_data = json.dumps({'signal': signal_data, 'sender': sender})

        # Prints any signal data if we need to
        if 'print' in signal_data and signal_data['print']:
            print(helpers.color(signal_data['message']))

        # Get db cursor, log event to db, then close cursor
        cur = self.ccnn.cursor()
        # TODO: implement log_event() function
        # TODO: add "_event" within log_event instead of here
        log_event(cur, sender, (signal_data['event_type'] + "_event"), json.dumps(signal_data), signal_data['timestamp']) # TODO: see above
        cur.close()

        # TODO: log all dispatcher signals with logging if debug argument is passed

    # TODO: implement a check to see if we're running as root. May not need this...

    # def handle_args(self):
    #     """
    #     Handle any passed arguments
    #     """
    # TODO: Implement the above function

    def shutdown(self):
        """
        Perform any shutdown actions
        """
        print("\n" + helpers.color("[!] Traficante is shutting down..."))
        log.info("Traficante is shutting down...")

        message = "[*] Traficante shutting down..."
        signal = json.dumps({
            'print': True,
            'message': message
        })
        dispatcher.send(signal, sender="traficante")

        # TODO: shutdown all sessions here
        # self.sessions.shutdown_session('all')

        # Close the database connection object
        if self.conn:
            self.conn.close()

    def database_connect(self):
        """
        Connect with the backend ./traficante.db sqlite database and return connection object
        :return: self.conn object
        """
        try:
            # S
            self.conn = sqlite3.connect('./data/traficante.db', check_same_thread=False)
            self.conn.text_factory = str
            self.conn.isolation_level = None
            return self.conn

        except Exception:
            message = "[!] Could not connect to database"
            log.error(message)
            print(helpers.color(message))
            sys.exit()

    def cmdloop(self):
        """
        The main cmdloop logic that handles menu navigation
        :return:
        """
        while True:
            try:
                if self.menu_state == 'Sessions':
                    self.do_sessions('')
                elif self.menu_state == 'Listeners':
                    self.do_listeners('')
                elif self.menu_state == 'Configs':
                    self.do_configs('')
                else:
                    # Display the main title
                    messages.title()

                    # TODO: Implement a counter feature that will display: how many modules exist, individual
                    #   counters for 'frameworks', 'encoders', 'transports', and active sessions
                    #
                    # # Get active sessions and loaded framework, encoder, and transport modules
                    # # Get active sessions
                    # num_sessions = self.sessions.get_sessions_db()
                    # if num_sessions:
                    #     num_sessions = len(num_sessions)
                    # else:
                    #     num_sessions = 0
                    #
                    # num_transports =self.modules.transports
                    num_sessions = "TODO" # TODO: fix me
                    num_frameworks = "1" # TODO: fix me
                    num_encoders = "TODO" # TODO: fix me
                    num_transports = "TODO" # TODO: fix me

                    print("\t" + helpers.color((str(num_sessions) + " active session\n")))
                    print("\t" + helpers.color((str(num_frameworks) + " frameworks supported\n")))
                    print("\t" + helpers.color((str(num_transports) + " transports loaded\n")))
                    print("\t" + helpers.color((str(num_encoders) + " encoders loaded")))

                    if len(self.resource_queue) > 0:
                        self.cmdqueue.append(self.resource_queue.pop(0))

                    cmd.Cmd.cmdloop(self)

            # ^C received
            except KeyboardInterrupt as e:
                self.menu_state = "Main"
                try:
                    choice = raw_input(helpers.color("\n[#] Exit? [y/N] ", warning=True))
                    if choice.lower() != "" and choice.lower()[0] == "y":
                        self.shutdown()
                        return True
                    else:
                        continue
                except KeyboardInterrupt as e:
                    continue

            except NavMain:
                self.menu_state = "Main"

            except NavConfigs:
                self.menu_state = "Configs"

            except NavSessions:
                self.menu_state = "Sessions"

            except NavListeners:
                self.menu_state = "Listeners"

        def print_topics(self, header, commands, cmdlen, maxcol):
            """
            Print a nicely formatted help menu.
            Adapted from recon-ng
            """
            if commands:
                self.stdout.write("%s\n" % str(header))
                if self.ruler:
                    self.stdout.write("%s\n" % str(self.ruler * len(header)))
                for command in commands:
                    self.stdout.write("%s %s\n" % (command.ljust(17), getattr(self, 'do_' + command).__doc__))
                self.stdout.write("\n")

        def emptyline(self):
            """
            Ignore empty lines
            """
            pass

        #################
        ## CMD Methods ##
        #################

        def postcmd(self, stop, line):
            if len(self.resource_queue) > 0:
                nextcmd = self.resource_queue.pop(0)
                self.cmdqueue.append(nextcmd)

        # TODO: Will resource files be supported?
        # def do_resource(self, arg):
        #     """
        #     Read and execute a list of Traficante commands from a file
        #     """
        #     self.resource_queue.extend(self.build_queue(arg))
        # def build_queue(self, resource_file, auto_run=False):
        #     return cmds # TODO: fix me

        def do_exit(self, line):
            "Exit Traficante"
            raise KeyboardInterrupt

        def do_configs(self, line):
            "Jump to Configs menu"
            try:
                configs_menu = ConfigsMenu(self)
                configs_menu.cmdloop()
            except Exception as e:
                log.error(("Encountered exception:\n" + str(e)))
                raise e

        def do_sessions(self, line):
            "Jump to sessions menu"
            try:
                sessions_menu = SessionsMenu(self)
                sessions_menu.cmdloop()
            except Exception as e:
                log.error(("Encountered exception:\n" + str(e)))
                raise e

        def do_listeners(self, line):
            "Jump to listeners menu"
            try:
                listeners_menu = ListenersMenu(self)
                listeners_menu.cmdloop()
            except Exception as e:
                log.error(("Encountered exception:\n" + str(e)))
                raise e

        # TODO: Create a do_list command that lists active sessions


class SubMenu(cmd.Cmd):
    def __init__(self, mainMenu):
        cmd.Cmd.__init__(self)
        self.mainMenu = mainMenu

    def cmdloop(self):
        if len(self.mainMenu.resource_queue) > 0:
            self.cmdqueue.append(self.mainMenu.resource_queue.pop(0))
        cmd.Cmd.cmdloop(self)

    def emptyline(self):
        pass

    def postcmd(self, stop, line):
        if line == "back":
            return True
        if len(self.mainMenu.resource_queue) > 0:
            nextcmd = self.mainMenu.resource_queue.pop(0)
            self.cmdqueue.append(nextcmd)

    def do_back(self, line):
        "Go back a menu"
        return True

    def do_configs(self, line):
        "Jump to configs menu"
        raise NavConfigs()

    def do_sessions(self, line):
        "Jump to sessions menu"
        raise NavSessions()

    def do_listeners(self, line):
        "Jump to listeners menu"
        raise NavListeners()

    def do_main(self, line):
        "Go to main menu"
        raise NavMain()

    def print_topics(self, header, commands, cmdlen, maxcol):
        """
        Print a nicely formatted help menu.
        Adapted from recon-ng
        """
        if commands:
            self.stdout.write("%s\n" % str(header))
            if self.ruler:
                self.stdout.write("%s\n" % str(self.ruler * len(header)))
            for command in commands:
                self.stdout.write("%s %s\n" % (command.ljust(17), getattr(self, 'do_' + command).__doc__))
            self.stdout.write("\n")
