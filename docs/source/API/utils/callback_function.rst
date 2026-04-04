=================
Callback Function
=================

.. code-block:: python

   def callback_function(
       self,
       trigger_function_name: str,
       callback_function: typing.Callable,
       callback_function_param: [dict, None] = None,
       callback_param_method: [str, None] = "kwargs",
       **kwargs
   ):

Execute a trigger function then call a callback function with results.

:param trigger_function_name: function to trigger (must be in ``event_dict``)
:param callback_function: function to call after trigger completes
:param callback_function_param: callback function parameters (dict)
:param callback_param_method: ``"kwargs"`` or ``"args"``
:param kwargs: parameters for the trigger function
