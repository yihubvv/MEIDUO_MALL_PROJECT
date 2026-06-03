from django.http import JsonResponse

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

    def __init__(self, arg: int, code=200, errmsg='OK'):
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