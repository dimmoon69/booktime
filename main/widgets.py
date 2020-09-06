from django.forms.widgets import Widget


class PlusMinusNumberInput(Widget):
    template_name = 'forms/widgets/plusminusnumber.html'

    class Media:
        css = {'all': ('css/plusminusnumber.css',)}
        js = ('js/plusminusnumber.js',)
