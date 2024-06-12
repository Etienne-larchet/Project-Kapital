from typing import Union

def display_progress(prefix: str = '', sufix: str = '', ratio: Union[int, str] = 'auto', replace_text=True, display_percent: bool = False) -> callable:
    """
        Decorator to visualize the progress of a function's execution.

        **Requirements:**
            - The decorated function must include '_iteration_nb' as a parameter.

        **Parameters:**
            - prefix (str): The string to display before the progress number.
            - suffix (str): The string to display after the progress number.
            - ratio (Union[int, str]): Controls the frequency of progress updates. Accepts an integer or 'auto' for automatic selection.
            - replace_text (bool): Determines whether progress is displayed on a single line. Set to False if the decorated function contains print statements.
            - display_percent (bool): Controls whether to display progress as a percentage.

        **Example:**
        ```python
        @display_progress(suffix=': Done', ratio=5) # Decorator
        def add_function(_iteration_nb): # Decorated function
            return 1

        b = 0
        for _ in range(25):
            b += my_function(_iteration_nb=25)
        print('Result is', b)
        ```

        **Notes:**
            - The 'ratio' parameter determines the frequency of progress updates. If set to 'auto', it dynamically adjusts based on the total number of iterations.
            - When 'replace_text' is True, progress updates occur on the same line, providing a cleaner display. This option is useful when the decorated function doesn't involve print statements.
            - If 'display_percent' is True, progress is shown as a percentage alongside the count.

        """
    def decorator(func):
        call_count = 0
        end_type = '\n'
        gap = ''
        percentage = ''
        _ratio = None # ratio argument must be redefine in decorator to not be local to wrapper => avoid multiple recalculation of ratio when set up tp auto 
        if replace_text:
                end_type = '\r'  
                gap = '  '

        def wrapper(*args, **kwargs):
            nonlocal call_count, end_type, gap, _ratio, percentage
            
            _iteration_nb = kwargs.pop('_iteration_nb', None)  # Extract _iteration_nb from kwargs
            if _iteration_nb is None:
                raise ValueError("The '_iteration_nb' parameter is required.")
            
            result = func(*args, **kwargs)
            call_count += 1

            if not isinstance(_ratio, int):
                if isinstance(ratio, int):
                    _ratio = ratio
                else:
                    _ratio = dynamic_counter(_iteration_nb)

            if call_count % _ratio == 0:
                if display_percent:
                    percentage = f" - {round(call_count/_iteration_nb*100, 2)}%"
                if call_count == _iteration_nb:
                    print(' ' * (len(sufix) + len(prefix) + len(str(call_count)) + len(percentage) + 2), end="\r")
                    print(f"{prefix}{call_count}{sufix}{percentage}")
                else:    
                    print(f"{gap}{prefix}{call_count}{sufix}{percentage}", end=end_type)
            
            return result
        return wrapper
    
    def dynamic_counter(total_iterations):
        '''Choose the ratio based on the total number of iterations'''
        ratios_list = [10, 100, 1000, 10000, 100000, 1000000, 10000000]
        selected_ratio = ratios_list[-1] * 10
        for ratio in ratios_list:
            if total_iterations // ratio <= ratio:
                selected_ratio = ratio *10
                break
        return selected_ratio
    
    return decorator