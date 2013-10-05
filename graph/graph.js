var Graph = {
    layout : function(data) {
        var shares = data["shares"];

        var w = 960, h = 500;

        var labelDistance = 0;

        var vis = d3.select("body").append("svg:svg").attr("width", w).attr("height", h);

        // markers
        vis.append('svg:defs').append('svg:marker')
            .attr('id', 'end-arrow')
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 6)
            .attr('markerWidth', 3)
            .attr('markerHeight', 3)
            .attr('orient', 'auto')
          .append('svg:path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', '#000');

        // hold nodes, links, etc.
        var nodes = [];
        var labelAnchors = [];
        var labelAnchorLinks = [];
        var links = [];

        var count = 0;

        for(var i = 0; i < shares.length; i++) {
            var from = {
                label: shares[i]["from"]["name"],
                id: shares[i]["from"]["fbid"],
                type: "from"
            };

            var to = {
                label: shares[i]["to"]["name"],
                id: shares[i]["to"]["fbid"],
                type: "to"
            };

            var interacted = shares[i]["interacted"].map(function (d) {
                return {
                    label: d.name,
                    id: d.fbid,
                    type: "interacted"
                };
            });

            var share_nodes = [from, to].concat(interacted);

            // add label anchors
            for (var j = 0; j < share_nodes.length; j++) {
                var node = share_nodes[j];
                nodes.push(node);
                labelAnchors.push({
                    node: node
                });
                labelAnchors.push({
                    node: node
                });
            }

            // link from 'from' to 'to'
            links.push({
                source: count,
                target: count + 1,
                weight: 1
            });

            // link from 'from' to each 'interacted'
            for (var j = 0; j < interacted.length; j++) {
                links.push({
                    source: count,
                    target: count + 1 + (j + 1),
                    weight: 0.5
                });
            }

            count += share_nodes.length;
        }

        // add labelAnchorLinks
        for (var i = 0; i < nodes.length; i++) {
            labelAnchorLinks.push({
                source : i * 2,
                target : i * 2 + 1,
                weight : 1
            });
        }

        var force = d3.layout.force().size([w, h]).nodes(nodes).links(links).gravity(1).linkDistance(100).charge(-3000).linkStrength(function(x) {
            return x.weight * 10
        });

        force.start();

        var force2 = d3.layout.force().nodes(labelAnchors).links(labelAnchorLinks).gravity(0).linkDistance(0).linkStrength(8).charge(-100).size([w, h]);
        force2.start();

        var link = vis.selectAll("line.link").data(links).enter().append("svg:line").attr("class", "link").style("stroke", "#CCC").style('marker-end', 'url(#end-arrow)');

        var node = vis.selectAll("g.node").data(force.nodes()).enter().append("svg:g").attr("class", "node");

        var profPic = function(d) {
            return "http://graph.facebook.com/" + d.id + "/picture?type=square";
        }

        var getSize = function(d) {
            return (d.type == "from")? 60 : (d.type == "to")? 40 : 20;
        }

        vis.append("clipPath").attr("id", "clipLarge").append("circle").attr("r", "30");
        vis.append("clipPath").attr("id", "clipMedium").append("circle").attr("r", "20");
        vis.append("clipPath").attr("id", "clipSmall").append("circle").attr("r", "10");

        var getClipPath = function(d) {
            return (d.type == "from")? "clipLarge" : (d.type == "to")? "clipMedium" : "clipSmall";
        }

        node.append("svg:circle").attr("class", function (d) { return d.type; }).attr("r", getSize);
        node.append("image").attr("xlink:href", function (d) { return profPic(d); })
            .attr("height", getSize)
            .attr("width", getSize)
            .attr("x", function(d) { return -1*getSize(d)/2 })
            .attr("clip-path", function(d) { return "url(#" + getClipPath(d) + ")"; })
            .attr("y", function(d) { return -1*getSize(d)/2 });
        node.call(force.drag);

        var anchorLink = vis.selectAll("line.anchorLink").data(labelAnchorLinks)

        var anchorNode = vis.selectAll("g.anchorNode").data(force2.nodes()).enter().append("svg:g").attr("class", "anchorNode");
        anchorNode.append("g").append("svg:circle").attr("r", 0).style("fill", "#FFF");
            anchorNode.append("svg:text").text(function(d, i) {
            return i % 2 == 0 ? "" : d.node.label
        }).style("fill", "#555").style("font-family", "Arial").style("font-size", 12);

        var updateLink = function() {
            this.attr("x1", function(d) {
                return d.source.x;
            }).attr("y1", function(d) {
                return d.source.y;
            }).attr("x2", function(d) {
                return d.target.x;
            }).attr("y2", function(d) {
                return d.target.y;
            });

        }

        var updateNode = function() {
            this.attr("transform", function(d) {
                return "translate(" + d.x + "," + d.y + ")";
            });
        }

        force.on("tick", function() {

            force2.start();

            node.call(updateNode);

            anchorNode.each(function(d, i) {
                if(i % 2 == 0) {
                    d.x = d.node.x;
                    d.y = d.node.y;
                } else {
                    var b = this.childNodes[1].getBBox();

                    var diffX = d.x - d.node.x;
                    var diffY = d.y - d.node.y;

                    var dist = Math.sqrt(diffX * diffX + diffY * diffY);

                    var shiftX = b.width * (diffX - dist) / (dist * 2);
                    shiftX = Math.max(-b.width, Math.min(0, shiftX));
                    var shiftY = 5;
                    this.childNodes[1].setAttribute("transform", "translate(" + shiftX + "," + shiftY + ")");
                }
            });

            anchorNode.call(updateNode);

            link.call(updateLink);
            anchorLink.call(updateLink);

        });
    }
};