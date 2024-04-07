from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .classes.process_manager import ProcessManager, ProcessAlreadyStarted
from .serializers import IPSerializer


pm = ProcessManager()


class PingManager(APIView):
    def _validate_ip(self, ip):
        serializer = IPSerializer(data={'ip': ip})
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data['ip']

    def post(self, request, ip, format=None):
        try:
            pm.start(self._validate_ip(ip))
        except ProcessAlreadyStarted:
            return Response(
                {'error': 'Task already started.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, ip, format=None):
        pm.stop(self._validate_ip(ip))
        return Response(status=status.HTTP_204_NO_CONTENT)
