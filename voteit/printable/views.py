# -*- coding: utf-8 -*-
from HTMLParser import HTMLParser
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring

from arche.views.base import BaseForm
from arche.views.base import BaseView
from arche.views.base import button_cancel
from betahaus.viewcomponent import view_action
from fanstatic import clear_needed
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPException
from pyramid.response import Response
from pyramid.traversal import resource_path
from voteit.core.models.interfaces import IMeeting
from voteit.core.security import MODERATE_MEETING
from webhelpers.html.converters import nl2br
from webhelpers.html.tools import strip_tags
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
        return HTTPFound(location = self.request.resource_url(self.context, appstruct['renderer']))


class DefaultPrintMeeting(BaseView):
    title = _("Printable HTML (default)")

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
        response = dict(settings)
        response['agenda_items'] = self.get_agenda_items()
        response['proposal_state_titles'] = dict(proposal_states(self.request))
        return response

    def get_agenda_items(self):
        agenda_items = []
        ai_names = self.settings.get('agenda_items', ())
        for name in self.context.keys():
            if name in ai_names:
                obj = self.context.get(name, None)
                if obj:
                    agenda_items.append(obj)
        return agenda_items

    def get_proposals(self, ai, state=None):
        query = "path == '%s' " % resource_path(ai)
        query += "and type_name == 'Proposal' "
        if state:
            query += "and workflow_state == '%s'" % state
        return tuple(self.catalog_query(query, resolve = True, sort_index = 'created'))

    def get_discussion(self, ai):
        query = "path == '%s' " % resource_path(ai)
        query += "and type_name == 'DiscussionPost' "
        return tuple(self.catalog_query(query, resolve = True, sort_index = 'created'))


class XMLExportMeetingView(DefaultPrintMeeting):
    title = _("XML export")

    @reify
    def unescape(self):
        parser = HTMLParser()
        return parser.unescape

    def __call__(self):
        values = super(XMLExportMeetingView, self).__call__()
        if isinstance(values, HTTPException):
            raise values
        output = self.export_xml(values)
        #Kill all output from fanstatic
        clear_needed()
        return Response(output, content_type = 'text/xml')

    def cleanup(self, text, html=True, trim=True):
        if html:
            text = strip_tags(text)
        text = self.unescape(text)
        if trim:
            text = "\n".join([x.strip() for x in text.splitlines()])
        return text

    def export_xml(self, values):
        proposal_state_titles = values['proposal_state_titles']
        root = Element('root')
        for ai in values['agenda_items']:
            ai_elem = SubElement(root, 'AgendaItem')
            title = SubElement(ai_elem, 'title')
            title.text = ai.title
            body = SubElement(ai_elem, 'body')
            body.text = self.cleanup(ai.body)
            #Proposals
            proposals = SubElement(ai_elem, 'Proposals')
            for obj in self.get_proposals(ai):
                proposal = SubElement(proposals, 'Proposal')
                #Attributes
                creators = SubElement(proposal, 'creators')
                creators.text = self.request.creators_info(obj.creator, portrait = False, no_tag = True).strip()
                text = SubElement(proposal, 'text')
                text.text = obj.text
                aid = SubElement(proposal, 'aid')
                aid.text = obj.aid
                state = SubElement(proposal, 'state')
                wf_state = obj.get_workflow_state()
                state.text = proposal_state_titles.get(wf_state, wf_state)
        #Discussion
        if self.settings.get('include_discussion', None):
            discussion_posts = SubElement(ai_elem, 'DiscussionPosts')
            for obj in self.get_discussion(ai):
                discussion_post = SubElement(discussion_posts, 'DiscussionPost')
                #Attributes
                creators = SubElement(discussion_post, 'creators')
                creators.text = self.request.creators_info(obj.creator, portrait = False, no_tag = True).strip()
                text = SubElement(discussion_post, 'text')
                text.text = obj.text
        body = """<?xml version="1.0" encoding="UTF-8" ?>\n"""
        body += tostring(root)
        return body


#FIXME:
#class JSONPrintMeeting(DefaultPrintMeeting):
#    title = _("JSON export")


@view_action('actions_menu', 'print_meeting_structure',
             title=_("Print meeting"),
             priority=30,
             permission=MODERATE_MEETING)
def print_meeting_structure_action(context, request, va, **kw):
    if getattr(request, 'meeting', False):
        return """<li><a href="%(url)s">%(title)s</a></li>""" % \
               {'url': request.resource_url(request.meeting, 'print_meeting_structure_form'),
                'title': request.localizer.translate(va.title)}


def includeme(config):
    config.add_view(PrintableMeetingForm,
                    context = IMeeting,
                    name = 'print_meeting_structure_form',
                    permission = MODERATE_MEETING,
                    renderer = 'arche:templates/form.pt')
    config.add_view(DefaultPrintMeeting,
                    context = IMeeting,
                    name = 'print_meeting_structure',
                    renderer = 'voteit.printable:templates/meeting_structure.pt',
                    permission = MODERATE_MEETING)
    config.add_view(XMLExportMeetingView,
                    context = IMeeting,
                    name = 'meeting_export.xml',
                    permission = MODERATE_MEETING)
    config.add_printable_view(DefaultPrintMeeting, 'print_meeting_structure')
    config.add_printable_view(XMLExportMeetingView, 'meeting_export.xml')
    config.scan(__name__)
