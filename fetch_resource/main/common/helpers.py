from .constants import Constants


def response(status_code, body):
    return {
        Constants.RESPONSE_STATUS_CODE: status_code,
        Constants.RESPONSE_BODY: body
    }