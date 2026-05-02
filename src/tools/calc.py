def calculate(expression: str):
    try:
        result = eval(expression, {"__builtins__": {}})
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Calculation error: {e}"
