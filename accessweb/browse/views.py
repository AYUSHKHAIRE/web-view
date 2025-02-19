from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from browse.memory_manager import memoryManager
from browse.sessionmanager import sessionManager
import time
from browse.logger_config import logger
from django.http import JsonResponse
from accessweb.settings import BASE_DIR
import json
import os 
# Proceed with other setups

logger.debug("[ MASTER ] Initializing managers...")

MM = memoryManager()
SSM = sessionManager()

# WSS.start_in_thread()

@login_required
def index(
    request
):
    user_id = UserProfile.objects.get(
        user = request.user.id
    ).uuid
    return render(
        request,
        "browse/main.html", 
        {
            'user_id': user_id
        }
    )

@login_required
def getCookie(
    request
):
    user_profile = UserProfile.objects.get(
        user=request.user.id
    )
    user_id = str(user_profile.uuid)  
    if request.method == "POST":
        try:
            data = json.loads(
                request.body
            )
            cookie = data.get('cookie')
            if not cookie:
                return JsonResponse(
                    {
                        'status': "Error", 
                        'message': "Cookie is required."
                    },
                    safe=False
                )
            file_data = {
                'user_id': user_id, 
                'cookie': cookie
            }
            directory_path = f'{BASE_DIR}/browse/docker_containers/docker_{user_id}/'
            os.makedirs(
                directory_path, 
                exist_ok=True
            )
            with open(
                f'{directory_path}/cookie.json', 
                "w"
            ) as f:
                json.dump(
                    file_data, 
                    f
                )
            return JsonResponse(
                {
                    'status': "OK"
                }, 
                safe=False
            )
        except Exception as e:
            return JsonResponse(
                {
                    'status': "Error", 
                    'message': str(e)
                }, 
                safe=False
            )
    return JsonResponse(
        {
            'status': "Error", 
            'message': "Invalid request method."
        }, 
        safe=False
    )

@login_required
def start_session(
    request,
    user_id,
    screen_dex
):
    time.sleep(0.1)
    logger.debug(f"received and passed {user_id} to main server and container .")
    SSM.setup_docker(
        user_id=user_id,
        screendex=screen_dex
    )
    time.sleep(0.1)
    MM.setup_memory(
        user_id=user_id
    )
    time.sleep(0.1)
    data = MM.read_memory(
        user_id=user_id
    )
    jsn_to_send = {
        'status':'OK'
    }
    return JsonResponse(
        jsn_to_send
    )