def http_request(
    path: str = "/qr-code", method: str = "GET", body: str = "test"
) -> dict:
    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": path,
        "rawQueryString": "",
        "headers": {},
        "body": body,
        "requestContext": {
            "accountId": "anonymous",
            "apiId": "e6sirlw4f6kx7s6osdrik5qs4i0veiia",
            "domainName": "e6sirlw4f6kx7s6osdrik5qs4i0veiia.lambda-url.us-east-1.on.aws",
            "domainPrefix": "e6sirlw4f6kx7s6osdrik5qs4i0veiia",
            "http": {
                "method": method,
                "path": path,
                "protocol": "HTTP/1.1",
                "sourceIp": "87.71.254.204",
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70",
            },
            "requestId": "fc5d0537-0fc1-444a-ab3e-90b3c163bb97",
            "routeKey": "$default",
            "stage": "$default",
            "time": "04/Feb/2023:20:44:27 +0000",
            "timeEpoch": 1675543467633,
        },
        "isBase64Encoded": False,
    }
