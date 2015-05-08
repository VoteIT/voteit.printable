from arche.views.base import BaseForm
from arche.views.base import button_cancel
from voteit.core.models.interfaces import IMeeting
from voteit.core.security import MODERATE_MEETING
import deform
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from arche.views.base import BaseView
from pyramid.decorator import reify
from pyramid.traversal import resource_path

from voteit.printable.schemas import PrintableMeetingSchema
from voteit.printable import _
from voteit.printable.fanstaticlib import printable_css


class PrintableMeetingForm(BaseForm):
    
    buttons = (deform.Button('print', title = _("Create print view")), button_cancel)

    def get_schema(self):
        return PrintableMeetingSchema()

    def print_success(self, appstruct):
        self.request.session['%s:print_agenda_items' % (self.context.uid)] = appstruct
        return HTTPFound(location = self.request.resource_url(self.context, 'print_meeting_structure'))

#
#    include_ai_body = colander.SchemaNode(colander.Bool(),
#                                          title = _("Include agenda item body, if any?"),
#                                          default = True)
#    include_proposal_states = colander.SchemaNode(colander.Set(),
#                                                  widget = include_proposal_states_widget,
#                                                  default = all_proposal_state_ids,
#                                                  title = _("Include these proposal states"),
#                                                  missing = ())
#    include_discussion = colander.SchemaNode(colander.Bool(),
#                                             default = False,
#                                             title = _("Include discussion posts?"))



class PrintableMeetingStructure(BaseView):

    @reify
    def settings(self):
        return self.request.session.get('%s:print_agenda_items' % (self.context.uid), {})

    def __call__(self):
        printable_css.need()
        settings = self.settings
        if not settings:
            raise HTTPForbidden("Nothing to do")
        agenda_items = []
        for name in settings.get('agenda_items', ()):
            obj = self.context.get(name, None)
            if obj:
                agenda_items.append(obj)
        response = dict(settings)
        response['agenda_items'] = agenda_items
        return response

    def get_proposals(self, ai):
        query = "path == '%s' " % resource_path(ai)
        query += "and type_name == 'Proposal' "
        query += "and workflow_state in any(%s)" % list(self.settings.get('include_proposal_states', ()))
        return self.catalog_query(query, resolve = True)

    def get_discussion(self, ai):
        query = "path == '%s' " % resource_path(ai)
        query += "and type_name == 'DiscussionPost' "
        return self.catalog_query(query, resolve = True)

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
                    #renderer = '')
