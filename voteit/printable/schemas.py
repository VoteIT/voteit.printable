from pyramid.i18n import TranslationString
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
    return deform.widget.CheckboxChoiceWidget(values=values)


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
    for info in wf._state_info(IProposal):  # Public API goes through permission checker
        item = [info['name']]
        item.append(request.localizer.translate(core_ts(info['title'])))
        state_values.append(item)
    return state_values


@colander.deferred
def include_proposal_states_widget(node, kw):
    request = kw['request']
    return deform.widget.CheckboxChoiceWidget(values=proposal_states(request))


@colander.deferred
def all_proposal_state_ids(node, kw):
    request = kw['request']
    return [x[0] for x in proposal_states(request)]


@colander.deferred
def system_users_widget(node, kw):
    request = kw['request']
    system_users = [(u, u) for u in request.meeting.system_userids]
    if not system_users:
        return deform.widget.HiddenWidget()
    return deform.widget.CheckboxChoiceWidget(values=system_users)


class PrintableMeetingSchema(colander.Schema):
    title = _("Print meeting")
    agenda_items = colander.SchemaNode(
        colander.Set(),
        title=_("Select agenda items"),
        widget=selectable_agenda_items_widget,
        default=all_agenda_items_keys,
    )
    include_ai_body = colander.SchemaNode(
        colander.Bool(),
        title=_("Include agenda item body, if any?"),
        default=True,
    )
    include_proposal_states = colander.SchemaNode(
        colander.Set(),
        widget=include_proposal_states_widget,
        default=all_proposal_state_ids,
        title=_("Include these proposal states"),
        missing=(),
    )
    include_discussion = colander.SchemaNode(
        colander.Bool(),
        default=False,
        title=_("Include discussion posts?"),
    )
    include_discussion_userids = colander.SchemaNode(
        colander.Set(),
        title=_("Limit discussion posts to system users?"),
        widget=system_users_widget,
        missing=(),
    )
    show_states = colander.SchemaNode(
        colander.Bool(),
        title=_("Show proposal states"),
        default=True,
    )
    no_userid = colander.SchemaNode(
        colander.Bool(),
        title=_("Hide userids?"),
        default=False,
    )


class HTMLPrintSchema(PrintableMeetingSchema):
    horizontal_separators = colander.SchemaNode(
        colander.Bool(),
        title=_("Show horizontal separators?"),
        default=True,
    )


class XMLPrintSchema(PrintableMeetingSchema):
    hashtag_number_only = colander.SchemaNode(
        colander.Bool(),
        title=_("Only show hashtag number?"),
        default=False,
    )


def includeme(config):
    config.add_schema('Meeting', HTMLPrintSchema, 'print_html')
    config.add_schema('Meeting', XMLPrintSchema, 'print_xml')
