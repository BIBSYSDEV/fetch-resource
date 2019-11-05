from fetch_resource.main.common.constants import Constants
from fetch_resource.main.RequestHandler import RequestHandler


def handler(event, context):
    if event is None:
        raise ValueError(Constants.ERROR_MISSING_EVENT)
    else:
        request_handler = RequestHandler()
        return request_handler.handler(event, context)
