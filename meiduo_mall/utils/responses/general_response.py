from django.http import JsonResponse
from meiduo_mall.errors import NO_ERROR

from django.http import JsonResponse


class JsonResponsePass(JsonResponse):
    """
    JSON response for successful requests.

    Args:
        code (int, optional):
            Response status code. Defaults to 200.
        errmsg (str, optional):
            Response message. Defaults to NO_ERROR.

    Response Format:
        {
            "code": 0,
            "errmsg": "OK"
        }
    """

    def __init__(
        self,
        code: int = 0,
        errmsg: str = NO_ERROR
    ) -> None:
        """
        Initialize a success response.

        Args:
            code:
                Response status code.
            errmsg:
                Success message.
        """
        data = {
            'code': code,
            'errmsg': errmsg,
        }

        super().__init__(data)

class JsonResponseCount(JsonResponse):
    """
    JSON response containing a count value.

    Args:
        arg (int):
            The count to be returned in the response.

    Response Format:
        {
            "code": 200,
            "count": <arg>,
            "errmsg": "OK"
        }
    """

    def __init__(self, arg: int, code=200, errmsg=NO_ERROR) -> None:
        """
        Initialize a count response.

        Args:
            arg (int):
                The count value to include in the response.
        """
        data = {
            'code': code,
            'count': arg,
            'errmsg': errmsg,
        }
        super().__init__(data)

class JsonResponseError(JsonResponse):
    """
    JSON response for error messages.

    Args:
        errmsg (str):
            The error message to return.
        code (int, optional):
            The error status code. Defaults to 400.

    Response Format:
        {
            "code": <code>,
            "errmsg": <errmsg>
        }
    """

    def __init__(self, errmsg: str, code: int = 400) -> None:
        """
        Initialize an error response.

        Args:
            errmsg (str):
                Error message describing the failure.
            code (int, optional):
                Error code for the response.
                Defaults to 400.
        """
        data = {
            'code': code,
            'errmsg': errmsg,
        }
        super().__init__(data, status=code)
