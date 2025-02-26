import ast


def value_has_forbidden_character(value):
    """
    Checks if a given string contains any forbidden characters.

    Parameters
    ----------
    value : str
        The string to be checked for forbidden characters.

    Returns
    -------
    list
        A list of forbidden characters found in the input string.
    """
    forbidden_characters = "<>:\"|?*[]"
    found_forbidden = []
    for fc in forbidden_characters:
        if fc in value:
            found_forbidden.append(fc)
    
    return found_forbidden


def is_number(num):
    """
    Checks if a string can be converted to a valid number (both integer and float).

    Parameters
    ----------
    num : str
        The string to be checked.

    Returns
    -------
    bool
        True if the string can be converted to a valid number, False otherwise.
    """
    try:
        float(num)
        int(num)
        return True
    except ValueError:
        return False


def is_number_or_empty(num):
    """
    Checks if a string is either empty or can be converted to a valid number.

    Parameters
    ----------
    num : str
        The string to be checked.

    Returns
    -------
    bool
        True if the string is empty or can be converted to a valid number, False otherwise.
    """
    if num == "":
        return True
    else:
        try:
            float(num)
            return True
        except ValueError:
            return False


def isfloat(num):
    """
    Checks if a string can be converted to a float.

    Parameters
    ----------
    num : str
        The string to be checked.

    Returns
    -------
    bool
        True if the string can be converted to a float, False otherwise.
    """
    try:
        float(num)
        return True
    except ValueError:
        return False


def is_int_or_empty(num):
    """
    Checks if a string is either empty or can be converted to an integer.

    Parameters
    ----------
    num : str
        The string to be checked.

    Returns
    -------
    bool
        True if the string is empty or can be converted to an integer, False otherwise.
    """
    if num == "":
        return True
    else:
        try:
            int(num)
            return True
        except ValueError:
            return False


def isint(num):
    """
    Checks if a string can be converted to an integer.

    Parameters
    ----------
    num : str
        The string to be checked.

    Returns
    -------
    bool
        True if the string can be converted to an integer, False otherwise.
    """
    try:
        int(num)
        return True
    except ValueError:
        return False


def value_is_empty_or_none(val):
    """
    Checks if a value is either an empty string or None.

    Parameters
    ----------
    val : str or None
        The value to be checked.

    Returns
    -------
    bool
        True if the value is an empty string or None, False otherwise.
    """
    if val == '' or val is None:
        return True
    else:
        return False


def widget_value_is_positive_int_or_empty(widget):
    """
    Checks if the value of a widget is either an empty string or a positive integer.

    Parameters
    ----------
    widget : widget
        The widget whose value is to be checked.

    Returns
    -------
    bool
        True if the widget value is empty or a positive integer, False otherwise.
    """
    value = widget.get()
    if value == '':
        return True
    try:
        n = int(value)
        if not n >= 0:
            return False
        else:
            return True
    except ValueError:
        return False


def convert_to_type(value: str):
    """
    Converts a string representation of a variable into its corresponding Python type.

    Examples:
    '1' -> int(1)
    'True' -> bool(True)
    'None' -> None
    '0.5' -> float(0.5)
    '[1, 2, 3]' -> list([1, 2, 3])

    :param value: str - The string representation of the variable
    :return: The value converted to its corresponding type
    """
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        # If literal_eval fails, return the original string
        return value