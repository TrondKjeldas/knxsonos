#
# Simple proxy to be able to control the Sonos system
# from the KNX bus. Requires a running eibd daemon.
#

from brisa.core.reactors import install_default_reactor
reactor = install_default_reactor()

from brisa.core.threaded_call import run_async_function

import sonos
import knx

from time import sleep

def _exit():
    """Stops the _handle_cmds loop
    """
    global running_handle_cmds
    running_handle_cmds = False
    

def _help():
    """Prints the available commands that are used in '_handle_cmds' method.
    """
    print 'Available commands: '
    for x in commands.keys():
        print '\t%s' % x


#Control the loop at _handle_cmds method
running_handle_cmds = True
commands = {'exit': _exit, 
            'help': _help}


def _handle_cmds():
    while running_handle_cmds:
        try:
            input = raw_input('>>> ').strip()
            if len(input.split(" ")) > 0:
                try:
                    commands[input.split(" ")[0]]()
                except KeyError, IndexError:
                    print 'Invalid command, try help'
        except KeyboardInterrupt, EOFError:
            global c
            c.stop()
            break
        sleep(100)
        import threading
        print "THREADS: %s" %str(threading.enumerate())

    # Stops the main loop
    reactor.main_quit()




c  = None
if __name__ == '__main__':

    # Create and start Sonos interface
    c = sonos.SonosCtrl()
    commands.update(c.commands())
    c.start()

    # Create and start KNX interface
    k = knx.KnxInterface(c)
    k.start()

    # Run command interface as well...
    run_async_function(_handle_cmds, ())
    reactor.add_after_stop_func(c.stop)
    reactor.add_after_stop_func(k.stop)
    reactor.main()
    












