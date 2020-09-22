from datetime import datetime


def get_logger_funcs(logger):
    func_dict = {
        "warning": logger.warning,
        "error": logger.error,
        "critical": logger.critical,
    }

    def get_test_func(key, func):
        def test_func(postfix):
            datetime_now = datetime.now()
            message = "This is a " + key + " message" + postfix
            func(message)
            return message, datetime_now

        return test_func

    funcs = [get_test_func(k, func_dict[k]) for k in func_dict]
    return funcs
