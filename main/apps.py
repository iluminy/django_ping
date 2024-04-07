from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        # WARNING: NOT SUITABLE FOR PRODUCTION!
        # The following code reinitializes some keys in the Redis DB to prevent
        # using old values since the last server shutdown.
        #  * This process will be called each time the Django server
        #    or WSGI/ASGI app starts (multiple calls possible).
        #  * It will also be called on any manage.py command
        #    (such as makemigrations, migrate, etc.).
        #  * Additionally, it will be called when a new worker
        #    on your production server boots.
        # Therefore, it is not suitable for production. You need to use
        # a Django management command:
        # https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/
        # and run it only once before starting your WSGI/ASGI app.
        from django.conf import settings
        from main.classes.connected_users import ConnectedUsers
        from main.classes.process_manager import ProcessManager

        if settings.DEBUG:
            with ConnectedUsers(sync_mode=True) as cu:
                cu.flush_users()
            with ProcessManager() as pm:
                pm.flush_processes()
            print('Redis data DB reinitialized!')
