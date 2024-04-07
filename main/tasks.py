import signal
from subprocess import Popen, PIPE

import channels.layers
from asgiref.sync import async_to_sync
from celery import shared_task
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils import timezone

import main.classes.process_manager
from main.classes.connected_users import ConnectedUsers


def _listen_to_ping_and_signals_loop(ip, process, channel_layer, pm, cu, now):
    """
    Receive ping's output in a loop and send it through websockets to the browser.
    Also, pay attention to the signals in the Redis DB.
    """
    last_checked_at = now
    lifetime = now + relativedelta(seconds=settings.PROCESS_LIFETIME)
    sigint_sent = False
    while True:
        output = process.stdout.readline()
        if not output:
            process.kill()
            print('Process killed because of no output')
            break
        print(repr(output))

        # Send data through WebSocket to client's browser.
        async_to_sync(channel_layer.group_send)(
            ip,
            {
                'type': 'send_data',
                'message': output,
            },
        )

        # If SIGINT was sent, we don't need to check anything else.
        # Just process remaining output.
        if sigint_sent:
            continue

        # If task should be terminated.
        terminating_tasks = pm.get_terminating()
        if ip in terminating_tasks:
            print('sending SIGINT')
            process.send_signal(signal.SIGINT)
            sigint_sent = True

        # Check if there are listeners.
        now = timezone.now()
        check_online_at = last_checked_at + relativedelta(seconds=settings.PROCESS_ONLINE_CHECK_FREQUENCY)
        is_time_to_check_online = now > check_online_at
        if is_time_to_check_online:
            last_checked_at = now
            users = cu.get_for_process(ip)
            if not users:
                process.kill()
                print('Process killed because of no listeners')
                break

        # Check if lifetime exceeded.
        is_time_to_terminate = now > lifetime
        if is_time_to_terminate:
            process.kill()
            print('Process killed because of exceeded lifetime')
            break


@shared_task
def ping_task(ip):
    """
    Starts ping subprocess and process its output.
    """
    now = timezone.now()

    with main.classes.process_manager.ProcessManager() as pm:
        if ip in pm.get_running():
            print('Process is already running')
            return
        if ip not in pm.get_pending():
            print('Process is not pending')
            return
        pm.mark_as_running(ip)

        with ConnectedUsers(sync_mode=True) as cu:
            channel_layer = channels.layers.get_channel_layer()

            with Popen(['ping', ip],
                       stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True) as process:
                _listen_to_ping_and_signals_loop(ip, process, channel_layer, pm, cu, now)
                process.communicate()
            pm.clean_up_process(ip)
