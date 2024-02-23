class LamodaCategoriesNotFoundException(Exception):
    """
    Custom exception for wrong lamoda categories and subcategories specifed in route.

    Attributes:
    - details (list, optional) - List of existing categories or subcategories to replace category specifed by user.
    - message (str, optional) - Error message describing exception.
    """

    def __init__(self, message: str = "", details: list = []):
        super().__init__(message)
        self.details = details
        self.message = message
