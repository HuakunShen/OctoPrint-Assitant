from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse

from .constants import OCTOPRINT_X_API_KEY, MASTER_NAME

import requests
import io
from .utils import get_octoprint_url_prefix, build_url, time_struct_to_text, convert_seconds
from .models import DurationPrecision



def index(request):
    return HttpResponse("Hello, world. You're at the index.")

def octoprint_state(request):
    url = build_url(get_octoprint_url_prefix(), '/api/connection')
    res = requests.get(url, headers={"Accept": "application/json", "x-api-key": OCTOPRINT_X_API_KEY})
    if res.status_code != 200:
        return HttpResponse(f"Request to OctoPrint failed: Status Code={res.status_code}")
    res_json = res.json()
    state = res_json['current']['state']
    return HttpResponse(state)

def octoprint_job_status(request):
    url = build_url(get_octoprint_url_prefix(), '/api/job')
    res = requests.get(url, headers={"Accept": "application/json", "x-api-key": OCTOPRINT_X_API_KEY})
    if res.status_code != 200:
        return HttpResponse(f"Request to OctoPrint failed: Status Code={res.status_code}")
    res_json = res.json()
    state = res_json['state']
    print_time = res_json['progress']['printTime']
    print_time_left = res_json['progress']['printTimeLeft']
    response = io.StringIO()
    
    if print_time is None or print_time_left is None:
        response.write(f"{state}, Not Printing")
    else:
        print_time_text = time_struct_to_text(convert_seconds(print_time), DurationPrecision.minutes)
        print_time_left_text = time_struct_to_text(convert_seconds(print_time_left), DurationPrecision.minutes)
        response.write(f"Dear {MASTER_NAME}, I am {state}, ")
        response.write(f"I Have printed for {print_time_text}, ")
        response.write(f"and printing time left is {print_time_left_text}\n")
    return HttpResponse(response.getvalue(), content_type="text/plain")


def send_command(command: str, action: str=None):
    url = build_url(get_octoprint_url_prefix(), '/api/job')
    json_data = {"command": command, "action": action}
    if action is not None:
        json_data.update({"action": action})
    return requests.post(url, headers={"Accept": "application/json", "x-api-key": OCTOPRINT_X_API_KEY}, json=json_data)

def octoprint_job_cancel(request):
    res = send_command(command="cancel")
    response_text = res.text if res.status_code != 204 else f"Yes {MASTER_NAME}, Job Cancelled"
    return HttpResponse(response_text, status=200)

def octoprint_job_start(request):
    res = send_command(command="start")
    response_text = res.text if res.status_code != 204 else f"Yes {MASTER_NAME}, Job Started"
    return HttpResponse(response_text, status=200)

def octoprint_job_toggle(request):
    res = send_command(command="pause", action="toggle")
    response_text = res.text if res.status_code != 204 else f"Yes {MASTER_NAME}, Job Toggled"
    return HttpResponse(response_text, status=200)

