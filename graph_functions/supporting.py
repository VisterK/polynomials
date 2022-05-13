from io import BytesIO

import matplotlib.pyplot as plt

plt.rc('mathtext', fontset='cm')


def tex2svg(formula, fontsize=12, dpi=300):
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, r'${}$'.format(formula), fontsize=fontsize)

    output = BytesIO()
    fig.savefig(output, dpi=dpi, transparent=True, format='svg',
                bbox_inches='tight', pad_inches=0.0)
    plt.close(fig)

    output.seek(0)
    return output.read()


def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


def to_raw(string):
    return fr"{string}"
