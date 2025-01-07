from tkinter import messagebox


# todo : need to add unit tests
def dict_has_duplicate_values(my_dict, ):
    rev_multidict = {}
    for key, value in my_dict.items():
        rev_multidict.setdefault(value, set()).add(key)
    duplicates_keys = [key for key, values in rev_multidict.items() if len(values) > 1]
    return duplicates_keys

def value_has_forbidden_character(value):
    # forbidden_characters = "<>:\"/\\|?*[]" with slashes
    forbidden_characters = "<>:\"|?*[]"
    found_forbidden = []
    for fc in forbidden_characters:
        if fc in value:
            found_forbidden.append(fc)

    return found_forbidden


def is_number(num):
    try:
        float(num)
        int(num)
        return True
    except ValueError:
        return False


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def isint(num):
    try:
        int(num)
        return True
    except ValueError:
        return False


def value_is_empty_or_none(val):
    if val == '' or val is None:
        return True
    else:
        return False


def widget_value_is_positive_int_or_empty(widget):
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


