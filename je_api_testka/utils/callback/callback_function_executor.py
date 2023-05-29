import typing
from sys import stderr

from je_api_testka.utils.exception.exception_tags import get_bad_trigger_function, get_bad_trigger_method
from je_api_testka.utils.exception.exceptions import CallbackExecutorException
from je_api_testka.utils.global_dict.event_dict import event_dict
from je_api_testka.utils.package_manager.package_manager_class import package_manager


class CallbackFunctionExecutor(object):
    def __init__(self):
        self.event_dict = event_dict

    def callback_function(
            self,
            trigger_function_name: str,
            callback_function: typing.Callable,
            callback_function_param: [dict, None] = None,
            callback_param_method: [str, None] = "kwargs",
            **kwargs
    ) -> typing.Any:
        """
        :param trigger_function_name: what function we want to trigger only accept function in event_dict
        :param callback_function: what function we want to callback
        :param callback_function_param: callback function's param only accept dict
        :param callback_param_method: what type param will use on callback function only accept kwargs and args
        :param kwargs: trigger_function's param
        :return:
        """
        try:
            if trigger_function_name not in self.event_dict.keys():
                raise CallbackExecutorException(get_bad_trigger_function)
            execute_return_value = self.event_dict.get(trigger_function_name)(**kwargs)
            if callback_function_param is not None:
                if callback_param_method not in ["kwargs", "args"]:
                    raise CallbackExecutorException(get_bad_trigger_method)
                if callback_param_method == "kwargs":
                    callback_function(**callback_function_param)
                else:
                    callback_function(*callback_function_param)
            else:
                callback_function()
            return execute_return_value
        except Exception as error:
            print(repr(error), file=stderr)


callback_executor = CallbackFunctionExecutor()
package_manager.executor = callback_executor
