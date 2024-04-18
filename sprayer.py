import requests
import os
from urllib3.exceptions import InsecureRequestWarning
import base64

requiredEnvVars = ["METHOD_ENC", "URL_ENC", "HEADERS_ENC", "BODY_ENC"]
missingEnvVars = [var for var in requiredEnvVars if os.getenv(var) is None]

if missingEnvVars:
    missingVarsStr = ", ".join(missingEnvVars)
    raise ValueError(f"Missing environment variables: {missingVarsStr}")

methodEnc = os.getenv("METHOD_ENC")
urlEnc = os.getenv("URL_ENC")
headersEnc = os.getenv("HEADERS_ENC", default="")
bodyEnc = os.getenv("BODY_ENC", default="")

def parseInputs(methodEnc, urlEnc, headersEnc, bodyEnc):
    method = base64.b64decode(methodEnc).decode()
    url = base64.b64decode(urlEnc).decode()
    
    headers = {}
    if len(headersEnc) > 0:
        headersRaw = base64.b64decode(headersEnc).decode()
        headersLines = headersRaw.splitlines()
        if len(headersLines)%2 != 0:
            raise Exception("Can not parse the request headers.")

        for i in range(0, len(headersLines), 2):
            headers[headersLines[i]] = headersLines[i+1]

    body = None
    if len(bodyEnc) > 0:
        body = base64.b64decode(bodyEnc).decode()

    return method, url, headers, body

def encodeOutputs(status, headers, body):
    statusEnc = ""
    if status != None:
        statusEnc = base64.b64encode(str(status).encode()).decode()

    headersStr = ""
    if headers != None:
        for key in headers:
            headersStr += key + "\n" + headers[key] + "\n"
        if len(headersStr) > 0:
            headersStr = headersStr[:-1]
    headersEnc = base64.b64encode(headersStr.encode()).decode()

    bodyEnc = ""
    if body != None:
        bodyEnc = base64.b64encode(body.encode()).decode()

    return statusEnc, headersEnc, bodyEnc

def makeRequest(method, url, headers=None, body=None):
    try:
        response = requests.request(method, url, headers=headers, data=body, verify=False)
    
        status = response.status_code
        headers = response.headers
        body = response.text

        return status, headers, body, None
    except requests.RequestException as e:
        return None, None, None, str(e)


reqMethod, reqUrl, reqHeaders, reqBody = parseInputs(methodEnc, urlEnc, headersEnc, bodyEnc)

print("REQ_DATA", (reqMethod, reqUrl, reqHeaders, reqBody))

respStatus, respHeaders, respBody, respErr = makeRequest(reqMethod, reqUrl, reqHeaders, reqBody)

if respErr != None:
    print("RESP_ERR", respErr)
else:
    respStatusEnc, respHeadersEnc, respBodyEnc = encodeOutputs(respStatus, respHeaders, respBody)

    print("RESP_STATUS_ENC", respStatusEnc)
    print("RESP_HEADERS_ENC", respHeadersEnc)
    print("RESP_BODY_ENC", respBodyEnc)