#!/usr/bin/env python3

"""
Daemon class to turn any program into an UNIX daemon process.
Inspired from "Launching a Daemon Process on Unix"
http://chimera.labs.oreilly.com/books/1230000000393/ch12.html#_discussion_209
"""


import os
import sys
import atexit
import signal
import codecs
import builtins
import datetime


__all__ = ['Daemon']


class Daemon:

    def __init__(self, pidfile, action=None, kargs={},
                stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.pidfile = pidfile
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        if action:
            self.action = action
        else:
            self.action = self.run
        self.kargs = kargs

    def daemonize(self):
        """Start the daemon process"""
        if os.path.exists(self.pidfile):
            raise RuntimeError("Daemon already running.")

        # First fork (detaches from parent)
        try:
            if os.fork() > 0:           # > 0 means parent process
                raise SystemExit(0)     # Parent exit
        except OSError as e:
            raise RuntimeError("Fork #1 failed.")

        os.chdir('/')   # Set the root path as working directory
                        # to avoid unmount folder failure
        os.umask(0)     # Set chmod of the file to 777
        os.setsid()     # Create a new process id group

        # Second fork (relinquish session leadership)
        try:
            if os.fork() > 0:
                raise SystemExit(0)
        except OSError as e:
            raise RuntimeError("Fork #2 failed.")

        # Flush I/O buffers
        sys.stdout.flush()
        sys.stderr.flush()

        # Deal with UTF-8 encoding issue when pipe to log file
        if sys.stdout.encoding != 'UTF-8':
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        if sys.stderr.encoding != 'UTF-8':
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

        # Replace file descriptors for stdin, stdout, stderr
        with open(self.stdin, 'rb', 0) as f:
            os.dup2(f.fileno(), sys.stdin.fileno())
        with open(self.stdout, 'ab', 0) as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
        with open(self.stderr, 'ab', 0) as f:
            os.dup2(f.fileno(), sys.stderr.fileno())

        # Write PID file
        with open(self.pidfile, 'w') as f:
            f.write("{}\n".format(os.getpid()))

        # Arrange to have the PID file removed on exit/signal
        atexit.register(lambda: os.remove(self.pidfile))

        # Signal bandler for termination (required)
        def sigterm_handler(signo, frame):
            self.before_stop()
            raise SystemExit(1)
        signal.signal(signal.SIGTERM, sigterm_handler)

    def start(self):
        """Start command to daemonize and run the script"""
        self.daemonize()
        if self.kargs:
            # Run the main function of the daemon with
            # keyword arguments passed through
            self.action(**self.kargs)
        else:
            self.action()

    def restart(self):
        """Restart command (stop and start again)"""
        self.stop()
        self.start()

    def stop(self):
        """Stop command to stop the daemon"""
        if os.path.exists(self.pidfile):
            with open(self.pidfile) as f:
                os.kill(int(f.read()), signal.SIGTERM)
                # Wait that the daemon stop
                # Function is asynchronous and do not wait...
                while os.path.exists(self.pidfile):
                    pass
        else:
            print("Daemon is not running.", file=sys.stderr)
            raise SystemExit(0)


    def before_stop(self):
        """Run just before the method stop. Override to customize."""
        pass

    def run(self):
        """Main program that will do something. Override to customize"""
        pass

    def commands(self):
        """Implements the basic commands start, stop to control the daemon"""
        if len(sys.argv) < 2:
            print("Usage: {} [start|stop|restart]".format(sys.argv[0]), file=sys.stderr)
            raise SystemExit(1)

        if sys.argv[1] == 'start':
            self.start()
        elif sys.argv[1] == 'stop':
            self.stop()
        elif sys.argv[1] == 'restart':
            self.restart()
        else:
            if not self.others_commands():
                print("Unknown command {!r}".format(sys.argv[1]), file=sys.stderr)
                raise SystemExit(1)

    def others_commands(self):
        """
        Override to add your own daemon commands.
        Must return True is there is at least one customized command.
        """
        return False
