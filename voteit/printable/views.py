from arche.views.base import BaseForm
from arche.views.base import BaseView
from arche.views.base import button_cancel
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound
from pyramid.traversal import resource_path
from voteit.core.models.interfaces import IMeeting
from voteit.core.security import MODERATE_MEETING
from webhelpers.html.converters import nl2br
import deform

from voteit.printable import _
from voteit.printable.fanstaticlib import printable_css
from voteit.printable.schemas import PrintableMeetingSchema
from voteit.printable.schemas import proposal_states


class PrintableMeetingForm(BaseForm):
    
    buttons = (deform.Button('print', title = _("Create print view")), button_cancel)

    def get_schema(self):
        return PrintableMeetingSchema()

    def print_success(self, appstruct):
        self.request.session['%s:print_agenda_items' % (self.context.uid)] = appstruct
        self.request.session.changed()
        return HTTPFound(location = self.request.resource_url(self.context, 'print_meeting_structure'))


class PrintableMeetingStructure(BaseView):

    @reify
    def settings(self):
        return self.request.session.get('%s:print_agenda_items' % (self.context.uid), {})

    def nl2br(self, text):
        return unicode(nl2br(text))

    def __call__(self):
        printable_css.need()
        settings = self.settings
        if not settings:
            self.flash_messages.add(_("Pick what to print"))
            return HTTPFound(location = self.request.resource_url(self.context, 'print_meeting_structure_form'))
        agenda_items = []
        ai_names = settings.get('agenda_items', ())
        for name in self.context.keys():
            if name in ai_names:
                obj = self.context.get(name, None)
                if obj:
                    agenda_items.append(obj)
        response = dict(settings)
        response['agenda_items'] = agenda_items
        response['proposal_state_titles'] = dict(proposal_states(self.request))
        return response

    def get_proposals(self, ai, state):
        query = "path == '%s' " % resource_path(ai)
        query += "and type_name == 'Proposal' "
        query += "and workflow_state == '%s'" % state
        return tuple(self.catalog_query(query, resolve = True, sort_index = 'created'))

    def get_discussion(self, ai):
        query = "path == '%s' " % resource_path(ai)
        query += "and type_name == 'DiscussionPost' "
        return tuple(self.catalog_query(query, resolve = True, sort_index = 'created'))


def includeme(config):
    config.add_view(PrintableMeetingForm,
                    context = IMeeting,
                    name = 'print_meeting_structure_form',
                    permission = MODERATE_MEETING,
                    renderer = 'arche:templates/form.pt')
    config.add_view(PrintableMeetingStructure,
                    context = IMeeting,
                    name = 'print_meeting_structure',
                    permission = MODERATE_MEETING,
                    renderer = 'voteit.printable:templates/meeting_structure.pt')
