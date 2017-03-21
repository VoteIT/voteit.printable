voteit.printable - Export/Print meeting structure
=================================================

Good if you need a physical copy of the meeting structure

To register a new view to render a structure:

- Create a class with a title attribute set.
- Register it as a view for IMeeting.
- Register it with add_printable_view
- Include your code

(See Pyramid docs for the specifics)


Example:

.. code:: python

    from arche.views.base import BaseView
    from voteit.core.models.interfaces import IMeeting


    class MyView(BaseView):
        title = 'My view'

        def __call__(self):
            return {}


    def includeme(config):
        config.add_view(MyView,
                        context = IMeeting,
                        name = 'my_print_view',
                        permission = MODERATE_MEETING,
                        renderer = '<your template>')
        config.add_printable_view(DefaultPrintMeeting, 'my_print_view')
