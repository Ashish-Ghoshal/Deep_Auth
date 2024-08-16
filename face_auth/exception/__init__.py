import sys


class AppException(Exception):
    """


    def __init__(self, err_msg: Exception, err_detail: sys):
        """
        :param err_msg: The error message.
        """
        super().__init__(err_msg)
        self.msg = self._format_error(err_msg, err_detail)

    @staticmethod
    def _format_error(err: Exception, err_detail: sys) -> str:
        """
        Formats error message with file and line details.

        :param err: The exception object.
        :param err_detail: sys module providing execution details.
        :return: Formatted error message.
        """
        _, _, tb = err_detail.exc_info()
        file_name = tb.tb_frame.f_code.co_filename
        return (
            f"Error in script [{file_name}], line [{tb.tb_lineno}]: {err}."
        )

    def __repr__(self) -> str:
        """
        Represents the AppException object.
        """
        return self.__class__.__name__

    def __str__(self) -> str:
        """
        Returns the formatted error message for printing.
        """
        return self.msg
