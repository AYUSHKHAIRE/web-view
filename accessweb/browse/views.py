from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from browse.browser_manager import browserManager
from browse.memory_manager import memoryManager
from browse.sessionmanager import sessionManager
from browse.internal_server_manager import WebSocketServer
import time
from browse.logger_config import logger
from .internal_server_manager import WebSocketServer
from django.http import JsonResponse

# Proceed with other setups

logger.debug("[ MASTER ] Initializing managers...")

BM = browserManager()
MM = memoryManager()
WSS = WebSocketServer(port=9876)
SSM = sessionManager()

WSS.start_in_thread()


@login_required
def index(request):
    user_id = UserProfile.objects.get(user = request.user.id).uuid
    return render(request,"browse/main.html", {'user_id': user_id})

@login_required
def start_session(request,user_id):
    time.sleep(0.1)
    logger.debug(f"received and passed {user_id} to main server and container .")
    SSM.setup_docker(user_id=user_id)
    time.sleep(0.1)
    MM.setup_memory(user_id=user_id)
    time.sleep(0.1)
    data = MM.read_memory(user_id=user_id)
    return JsonResponse(data=data,safe=False)