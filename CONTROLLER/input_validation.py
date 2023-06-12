from tkinter import messagebox


# todo : when adding include exclude target, check if not empty
# todo : need to add unit tests


def AND(elements):  # todo : logic gates to fiiireflyyy
    if all(elements):
        return 1
    else:
        return 0


def NAND(elements):  # todo : logic gates to fiiireflyyy
    if all(elements):
        return 0
    else:
        return 1


def OR(elements):  # todo : logic gates to fiiireflyyy
    if any(elements):
        return 1
    else:
        return 0


def XOR(elementA, elementB):  # todo : logic gates to fiiireflyyy
    if elementA != elementB:
        return 1
    else:
        return 0


def INVERTER(element):  # todo : logic gates to fiiireflyyy
    return not element


def NOR(elements):  # todo : logic gates to fiiireflyyy
    if any(elements):
        return 0
    else:
        return 1


def XNOR(elementA, elementB):  # todo : logic gates to fiiireflyyy
    if elementA == elementB:
        return 1
    else:
        return 0


def widget_value_has_forbidden_character(widget):
    # forbidden_characters = "<>:\"/\\|?*[]" with slashes
    forbidden_characters = "<>:\"|?*[]"
    value = str(widget.get())
    for fc in forbidden_characters:
        if fc in value:
            messagebox.showerror("Value error", message=f"Usage of forbidden character {fc} in value"
                                                        f" {value}.\nThe forbidden characters "
                                                        f"are {forbidden_characters}")
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


def widget_value_is_positive_int_or_empty(widget):
    value = widget.get()
    if value == '':
        return True
    try:
        n = int(value)
        if not n >= 0:
            messagebox.showerror("Value error", f"entry \'{value}\' is not positive.")
            return False
        else:
            return True
    except ValueError:
        messagebox.showerror("Value error", f"entry \'{value}\' is not an integer.")
        return False
