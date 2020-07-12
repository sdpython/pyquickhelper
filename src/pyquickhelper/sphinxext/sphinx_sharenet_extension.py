# -*- coding: utf-8 -*-
"""
@file
@brief Defines a sphinx extension to add button to share a page
"""
import sphinx
from docutils import nodes
from docutils.parsers.rst import Directive, directives


class sharenet_node(nodes.Structural, nodes.Element):

    """
    Defines *sharenet* node.
    """
    pass


class ShareNetDirective(Directive):
    """
    Adds buttons to share a page. It can be done by
    adding::

        .. sharenet::
            :facebook: 1
            :linkedin: 2
            :twitter: 3
            :head: False

    Which gives:

    .. sharenet::
        :facebook: 1
        :linkedin: 2
        :twitter: 3
        :head: False

    The integer indicates the order in which they need to be displayed.
    It is optional. The option ``:head: False`` specifies the javascript
    part is added to the html body and not the header.
    The header can be overwritten by other custom commands.
    """
    available_networks = {'facebook', 'linkedin', 'twitter'}
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'facebook': directives.unchanged,
                   'linkedin': directives.unchanged,
                   'twitter': directives.unchanged,
                   'size': directives.unchanged,
                   'head': directives.unchanged,
                   }
    has_content = True
    sharenet_class = sharenet_node

    def run(self):
        """
        Runs the directve.

        @return      a list of nodes
        """
        def options_to_int(s):
            "local function"
            if s is None:
                return -1
            elif len(s) == 0:
                return 1e6
            else:
                return int(s)

        # list of networks
        bool_set = (True, 1, "True", "1", "true")
        p = [(options_to_int(self.options.get(net, None)), net)
             for net in ShareNetDirective.available_networks]
        p.sort()
        p = [a[1] for a in p if a[0] >= 0]

        # build node
        node = self.__class__.sharenet_class(networks=p,
                                             size=self.options.get('size', 20),
                                             inhead=self.options.get('head', True) in bool_set)
        node['classes'] += ["sharenet"]
        ns = [node]
        return ns


def sharenet_role(role, rawtext, text, lineno, inliner,
                  options=None, content=None):
    """
    Defines custom roles *sharenet*. The following instructions defines
    buttons of size 20 (:sharenet:`facebook-linkedin-twitter-20-body`)::

        :sharenet:`facebook-linkedin-twitter-20-body`

    The last term indicates the javascript part will be included in the
    HTML body instead of the head as this part might be tweaked by other
    custom commands.

    :param role: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """
    if options is None:
        options = {}
    if content is None:
        content = []
    spl = [a.strip().lower() for a in text.split('-')]
    networks = []
    size = 20
    inhead = True
    for v in spl:
        if v in ShareNetDirective.available_networks:
            networks.append(v)
        elif v == "body":
            inhead = False
        elif v == "head":
            inhead = True
        else:
            try:
                i = int(v)
                size = i
            except ValueError:  # pragma: no cover
                msg = inliner.reporter.error(
                    "unable to interpret {0} from {1}".format(v, rawtext), line=lineno)
                prb = inliner.problematic(rawtext, rawtext, msg)
                return [prb], [msg]

    if len(networks) == 0:
        msg = inliner.reporter.error(
            "no specified network from {0}".format(rawtext), line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]

    # ref = inliner.document.settings.rfc_base_url + inliner.rfc_url % rfcnum
    # set_classes(options)
    node = sharenet_node(networks=networks, size=size, inhead=inhead)
    node['classes'] += ["sharenet"]
    return [node], []


def visit_sharenet_node(self, node):
    """
    what to do when visiting a node sharenet
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    pass


def depart_sharenet_node_html(self, node):
    """
    what to do when leaving a node sharenet
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.

    It does only html for the time being.
    """
    if node.hasattr("networks"):
        networks = node["networks"]
        size = node["size"]
        inhead = node["inhead"]
        if len(networks) > 0:

            script = """
                        <script>
                        function share_url(share) {
                            var url = share + encodeURIComponent(window.location.href);
                            window.location.href = url;
                        }

                        function share_icon(divid, text) {
                            var canvas = document.getElementById(divid);
                            var context = canvas.getContext('2d');
                            var centerX = canvas.width / 2;
                            var centerY = canvas.height / 2;
                            var radius = centerX;

                            context.beginPath();
                            context.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);
                            context.fillStyle = '#444444';
                            context.fill();
                            context.font = '' + (centerX*4/3) + 'pt Calibri';
                            context.textAlign = 'center';
                            context.fillStyle = '#FFFFFF';
                            context.fillText(text, centerX, centerY+centerY*16/30);
                        }
                        </script>
                        """.replace("                        ", "")

            mapping = dict(facebook="f", linkedin="in", twitter="t")
            urls = dict(facebook="https://www.facebook.com/sharer/sharer.php?u=",
                        twitter="https://twitter.com/home?status=",
                        linkedin="https://www.linkedin.com/shareArticle?mini=true&amp;title=&amp;summary=&amp;source=&amp;url=")
            link = """<a href="#" onclick="share_url('{0}');return false;"><canvas height="{2}" id="canvas-{1}" width="{2}"/>""" + \
                   """</a><script>share_icon('canvas-{1}', '{1}');</script>"""

            rows = []
            for key in networks:
                text = mapping[key]
                ld = link.format(urls[key], text, size)
                rows.append(ld)

            if len(rows) > 0:
                if inhead:
                    self.head.append(script)
                else:
                    self.body.append(script)
                self.body.extend(rows)


def depart_sharenet_node(self, node):
    """
    what to do when leaving a node sharenet
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.

    It does only html for the time being.
    """
    pass


def visit_sharenet_node_rst(self, node):
    """
    what to do when visiting a node sharenet
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    inside = "-".join(node['networks'])
    inside = "{0}-{1}-{2}".format(inside,
                                  node["size"], "head" if node['inhead'] else "body")
    self.add_text(":sharenet:`{0}`".format(inside))


def depart_sharenet_node_rst(self, node):
    """
    what to do when leaving a node sharenet
    the function should have different behaviour,
    depending on the format, or the setup should
    specify a different function for each.
    """
    pass


def setup(app):
    """
    setup for ``sharenet`` (sphinx)
    """
    if hasattr(app, "add_mapping"):
        app.add_mapping('sharenet', sharenet_node)

    app.add_node(sharenet_node,
                 html=(visit_sharenet_node, depart_sharenet_node_html),
                 epub=(visit_sharenet_node, depart_sharenet_node_html),
                 elatex=(visit_sharenet_node, depart_sharenet_node),
                 latex=(visit_sharenet_node, depart_sharenet_node),
                 rst=(visit_sharenet_node_rst, depart_sharenet_node_rst),
                 md=(visit_sharenet_node_rst, depart_sharenet_node_rst),
                 text=(visit_sharenet_node, depart_sharenet_node))

    app.add_directive('sharenet', ShareNetDirective)
    app.add_role('sharenet', sharenet_role)
    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}
