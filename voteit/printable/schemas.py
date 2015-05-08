from repoze.workflow.workflow import get_workflow
from voteit.core.models.interfaces import IAgendaItem
from voteit.core.models.interfaces import IProposal
import colander
import deform

from voteit.printable import _
from voteit.core import _ as core_ts


@colander.deferred
def selectable_agenda_items_widget(node, kw):
    context = kw['context']
    values = []
    for (name, obj) in context.items():
        if not IAgendaItem.providedBy(obj):
            continue
        values.append((name, obj.title))
    return deform.widget.CheckboxChoiceWidget(values = values)
 
 
@colander.deferred
def all_agenda_items_keys(node, kw):
    context = kw['context']
    values = []
    for (name, obj) in context.items():
        if IAgendaItem.providedBy(obj):
            values.append(name)
    return values

def proposal_states(request):
    wf = get_workflow(IProposal, 'Proposal')
    state_values = []
    for info in wf._state_info(IProposal): #Public API goes through permission checker
        item = [info['name']]
        item.append(request.localizer.translate(core_ts(info['title'])))
        state_values.append(item)
    return state_values
    
@colander.deferred
def include_proposal_states_widget(node, kw):
    request = kw['request']
    return deform.widget.CheckboxChoiceWidget(values = proposal_states(request))
 
@colander.deferred
def all_proposal_state_ids(node, kw):
    request = kw['request']
    return [x[0] for x in proposal_states(request)]


class PrintableMeetingSchema(colander.Schema):
    title = _("Print meeting")
    agenda_items = colander.SchemaNode(colander.Set(),
                                       title = _("Select agenda items"),
                                       widget = selectable_agenda_items_widget,
                                       default = all_agenda_items_keys)
    include_ai_body = colander.SchemaNode(colander.Bool(),
                                          title = _("Include agenda item body, if any?"),
                                          default = True)
    include_proposal_states = colander.SchemaNode(colander.Set(),
                                                  widget = include_proposal_states_widget,
                                                  default = all_proposal_state_ids,
                                                  title = _("Include these proposal states"),
                                                  missing = ())
    include_discussion = colander.SchemaNode(colander.Bool(),
                                             default = False,
                                             title = _("Include discussion posts?"))
