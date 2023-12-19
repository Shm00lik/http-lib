from enum import Enum
import json


class Request:
    class RequestMethod(Enum):
        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        UNKNOWN = "UNKNOWN"

        @staticmethod
        def fromRequestData(requestData: str):
            mapper: dict = {v.value: v for v in Request.RequestMethod}

            if requestData.split(" ")[0] not in mapper:
                return Request.RequestMethod.UNKNOWN

            return mapper[requestData.split(" ")[0]]

    def __init__(self, data: str) -> None:
        self.splittedData = data.split("\r\n")

        self.method: Request.RequestMethod = Request.RequestMethod.UNKNOWN
        self.url: str = ""
        self.params: dict[str, str] = {}
        self.body: str = ""
        self.headers: dict[str, str] = {}
        self.payload: dict[str, str] = {}

        if len(self.splittedData) < 2:
            return

        self.parse()

    def parse(self) -> None:
        self.method = self.getMethod()
        self.url = self.getUrl()
        self.params = self.getParams()
        self.body = self.getBody()
        self.headers = self.getHeaders()
        self.payload = self.getPayload()

    def getMethod(self) -> RequestMethod:
        return Request.RequestMethod.fromRequestData(self.splittedData[0])

    def getUrl(self) -> str:
        return self.splittedData[0].split(" ")[1].split("?")[0]

    def getParams(self) -> dict[str, str]:
        params: dict[str, str] = {}

        splitted = self.splittedData[0].split(" ")[1].split("?")

        if len(splitted) < 2:
            return params

        for param in splitted[1].split("&"):
            params[param.split("=")[0]] = param.split("=")[1]

        return params

    def getBody(self) -> str:
        return self.splittedData[-1]

    def getHeaders(self) -> dict[str, str]:
        headers: dict[str, str] = {}

        for header in self.splittedData[1:-2]:
            headers[header.split(": ")[0]] = header.split(": ")[1]

        return headers

    def getPayload(self) -> dict[str, str]:
        if self.method != Request.RequestMethod.POST:
            return {}

        try:
            return json.loads(self.body)
        except:
            return {}

    def __str__(self) -> str:
        return str(self.splittedData)


class Response:
    """
    This class is responsible for creating a response to the client.
    """

    class StatusCode(Enum):
        OK = 200
        CREATED = 201
        BAD_REQUEST = 400
        NOT_FOUND = 404
        INTERNAL_SERVER_ERROR = 500

        @staticmethod
        def fromInt(statusCode: int):
            mapper: dict = {v.value: v for v in Response.StatusCode}

            if statusCode not in mapper:
                return Response.StatusCode.INTERNAL_SERVER_ERROR

            return mapper[statusCode]

        def __str__(self) -> str:
            return str(self.value) + " " + self.name.replace("_", " ").title()

        def __bool__(self) -> bool:
            return str(self.value).startswith("2")

    def __init__(
        self,
        content: str = "",
        statusCode: StatusCode = StatusCode.OK,
        headers: dict[str, str] = {},
    ) -> None:
        self.headers: dict[str, str] = headers
        self.content = ""

        self.setContent(content)

        self.statusCode: Response.StatusCode = statusCode

    def setContent(self, content: str) -> "Response":
        self.content = content

        if len(self.content) > 0:
            self.setHeader("Content-Length", str(len(self.content)))

        return self

    def setHeader(self, key: str, value: str) -> "Response":
        self.headers[key] = value

        return self

    def setStatusCode(self, statusCode: StatusCode) -> "Response":
        self.statusCode = statusCode

        return self

    def generate(self) -> str:
        response: str = "HTTP/1.1 " + str(self.statusCode) + "\r\n"

        response += "\r\n".join(
            [f"{key}: {value}" for key, value in self.headers.items()]
        )

        if len(self.content) > 0:
            response += "\r\n\r\n" + self.content

        response += "\r\n"
        return response

    def __str__(self) -> str:
        return self.generate()
