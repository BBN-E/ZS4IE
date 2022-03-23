/*
 * Copyright 2013 by Raytheon BBN Technologies Corp.
 * All Rights Reserved.
 */

// [XX] TODO: GET RID OF doc_url_prefix

function selectSentenceFromURLAnchor(href) {
    var sentno = (""+href).match(/#(sent-(.*)-[0-9]+)/);
    if (sentno)
	selectSentenceFromSentNo(sentno[1]);
}

function selectSentenceFromSentNo(sentno, do_not_update_details) {
    var textFrame = parent.frames["serifxmlTextFrame"];
    if (!textFrame) return;
    var sent = $("#"+sentno, textFrame.document)[0];
    if (sent) {
	//alert("SELECTING "+sentno+" -> "+sent+", "+sent.id);
	selectSentence(sent, do_not_update_details);
    }
}

function setupTextFrame(noMentionLinks) {
    // When the user clicks on a sentence, show it in the details frame.
    $("span.sentence").click(function() {
	selectSentence(this);
    });

    // If the users hovers over a mention, then highlight any coreferent
    // mentions.
    setupMentions(noMentionLinks);
    
    // Add next/prev key support.
    bind_next_prev_keypress()
    
    // If the URL contains a sentence, then select that sentence.
    selectSentenceFromURLAnchor(document.location);

    // Highlight the currently viewed document.
    var docNavFrame = parent.frames["serifxmlDocNavFrame"];
    if (docNavFrame && docNavFrame.doc_url_prefix) {
	var docFound = false;
	$("a.doc", docNavFrame.document).each(function() {
	    $(this.parentNode).toggleClass(
		"selected", this.id == "doc-"+docNavFrame.doc_url_prefix);
	    if (this.id == "doc-"+docNavFrame.doc_url_prefix) docFound=true;
	});
	// If the nav frame doesn't contain this document, then
	// load the first document that does occur in the nav frame.
	if (!docFound) {
	    var firstDoc = $("a.doc", docNavFrame.document)[0];
	    if (firstDoc) {
		document.location = firstDoc.href;
		var detailsFrame = parent.frames["serifxmlDetailsFrame"];
		if (detailsFrame) detailsFrame.location = "blank_page.html";
		var navUrl = firstDoc.href.replace(/.html$/, "-nav.html");
		var navFrame = parent.frames["serifxmlNavFrame"];
		if (navFrame) navFrame.location = navUrl;
	    }
	}
    }

    var $text = $("#doc-body");
    $("#toggle-names").change(function(){
	$text.toggleClass("mark-names", $(this).is(':checked'));
    });

    $("#toggle-prons").change(function(){
	$text.toggleClass("mark-prons", $(this).is(':checked'));
    });

    $("#toggle-descs").change(function(){
	$text.toggleClass("mark-descs", $(this).is(':checked'));
    });

    $("#toggle-icews-actors").change(function(){
	$text.toggleClass("mark-icews-actors", $(this).is(':checked'));
    });

    $("#toggle-unprocessed").change(function(){
	    $("#doc-body span.unprocessed").toggle($(this).is(':checked'));
	});

    $text.toggleClass("mark-names", $("#toggle-names").is(':checked'));
    $text.toggleClass("mark-prons", $("#toggle-prons").is(':checked'));
    $text.toggleClass("mark-descs", $("#toggle-descs").is(':checked'));
    $text.toggleClass("mark-icews-actors", 
		      $("#toggle-icews-actors").is(':checked'));
    $("#doc-body span.unprocessed").toggle($("#toggle-unprocessed").is(':checked'));
}

function getSvgSize(svg, dimension) {
    var widthAttr = svg.getAttribute(dimension);
    var ptMatch = widthAttr.match(/([0-9]+)pt/);
    if (ptMatch) {
	return 60+parseInt(ptMatch[1]);
    } else {
	return 500; // just pick an arbitrary starting point.
    }
}

function zoom(svg, factor) {
    var $svg = $(svg);
    var width = $svg.width();
    var height = $svg.height();
    if (!width) width = getSvgSize(svg, "width");
    if (!height) height = getSvgSize(svg, "height");
    //alert("zoom from "+width+"x"+height+" to "+
    //(width*factor)+"x"+(height*factor));
    $svg.width(width*factor);
    $svg.height(height*factor);
}

function setupGraphZoom() {
    $("a.graph-zoom-out").click(function() {
	zoom($("div.graph svg", this.parentNode)[0], 0.8);
	return false;
    });
    $("a.graph-zoom-in").click(function() {
	zoom($("div.graph svg", this.parentNode)[0], 1.25);
	return false;
    });
}

function setupDocGraphFrame(nav_url) {
    var navFrame = parent.frames["serifxmlNavFrame"];
    if (navFrame) navFrame.location=nav_url;

    // Add next/prev key support.
    bind_next_prev_keypress()

    // Set up zoom buttons.
    setupGraphZoom();
}

function setupDocEntitiesFrame(nav_url) {
    var navFrame = parent.frames["serifxmlNavFrame"];
    if (navFrame) navFrame.location=nav_url;

    // Set up zoom buttons.
    setupGraphZoom();

    $("a.expand-entity").click(function() {
	var $entityDiv = $(this.parentNode.parentNode);
	$entityDiv.toggleClass("collapsed-entity");
	return false;
    });
    $("tr.mention td.location a").click(function() {
	var sentno = (""+this.href).match(/-(sent-[0-9]+)-details.html/);
	if (sentno)
	    selectSentenceFromSentNo(sentno[1]);
    });
    $("a.show-entity-graph").click(function() {
	var $graph = $("div.doc-entity-graph", this.parentNode);
	if ($graph.hasClass("collapsed")) {
	    $(this).html("Hide entity graph");
	} else {
	    $(this).html("Show entity graph");
	}
	$graph.toggleClass("collapsed");
    });

    var entity = (""+document.location).match(/#(entity-.*)/);
    if (entity) showDocEntity(entity[1]);
}

function showDocEntity(id) {
    $("#"+id).removeClass("collapsed-entity");
    document.location = "#"+id;
}

function selectSentence(sent, do_not_update_details) {
    var textFrame = parent.frames["serifxmlTextFrame"];
    if (!textFrame) return;
    var oldSent = $(".selected-sentence", textFrame.document)[0];
    if (sent == "prev") {
	sent = $(oldSent).prevAll(".sentence")[0];
	if (!sent)
	    sent = $(oldSent.parentNode).prevAll(".match").find(".sentence")[0];
    } else if (sent == "next") {
	sent = $(oldSent).nextAll(".sentence")[0];
	if (!sent)
	    sent = $(oldSent.parentNode).nextAll(".match").find(".sentence")[0];
    }
    if (!sent) sent = $(".sentence", textFrame.document)[0]
    if (!sent) return; // No prev/next sentence.

    // Update the selection marking.
    if (oldSent) { $(oldSent).removeClass("selected-sentence"); }
    if (sent) { $(sent).addClass("selected-sentence"); }

    // If it's inside a match, then mark the match as well.
    if (oldSent) {
	if ($(oldSent.parentNode).is(".match")) {
	    $(oldSent.parentNode).removeClass("selected-match"); 
	}
    }
    if (sent) { 
	if ($(sent.parentNode).is(".match")) {
	    $(sent.parentNode).addClass("selected-match"); 
	}
    }

    // Make sure the sentence is visible.
    if ($(sent).position()) {
	var sent_top = $(sent).position().top;
	var sent_bot = sent_top + $(sent).height();
	var frame_top = $(textFrame).scrollTop();
	var frame_bot = frame_top + $(textFrame).height();
	if (sent_top < frame_top) {
	    $(textFrame).scrollTop(sent_top-50);
	} else if (sent_bot > frame_bot) {
	    $(textFrame).scrollTop(sent_bot-(frame_bot-frame_top)+50);
	}
    }

    // Show the sentence in the nav & details frames.
    if (!do_not_update_details) {
	var navFrame = parent.frames["serifxmlNavFrame"];
	var detailsFrame = parent.frames["serifxmlDetailsFrame"];
	var m = sent.id.match(/sent-(.*)-([0-9]+)/);
	navFrame.location = m[1]+"-sent-"+m[2]+"-nav.html";
	detailsFrame.location = m[1]+"-sent-"+m[2]+"-details.html";
    }
}

function setupDetailsFrame() {
    setupParse();
    $("ul.nav-tabs li").click(function() {
	selectDetailsTab(this);});
    
    // Add next/prev key support.
    bind_next_prev_keypress()

    // Set up zoom buttons.
    setupGraphZoom();

    var textFrame = parent.frames["serifxmlTextFrame"];
    if (!textFrame.selected_tab_id)
	textFrame.selected_tab_id = "parse";
    if (textFrame) {
	var tab = $("#"+textFrame.selected_tab_id)[0];
	selectDetailsTab(tab);
    } else {
	selectDetailsTab($("#parse")[0]);
    }

}

function setupDocNavFrame() {
    $("#doc-nav").jstree({
        "plugins": ["html_data", "themes"],
        "core": {"animation": 0},
        "themes": {"theme": "classic", icons: false},
    });

    // Add next/prev key support.
    bind_next_prev_keypress()
    
    // If the user clicks a sentence, then select it.
    $("a.sent-details").live("click", function() {
	selectSentenceFromURLAnchor(this.href);
    });

    // When viewing a doc-details page, view the doc as well.
    $("a.doc-details").live("click", function() {
	var textFrame = parent.frames["serifxmlTextFrame"];
	if (textFrame) {
	    var doc_url = $(this).closest("li.doc").find("a.doc")[0].href;
	    old_url = (""+textFrame.location).match("[^#]*")[0];
	    if (doc_url && (old_url != doc_url)) 
		textFrame.location = doc_url;
	}
    });

    // When viewing a doc, clear the details page
    $("a.no-details").live("click", function() {
	var detailsFrame = parent.frames["serifxmlDetailsFrame"];
	if (detailsFrame) detailsFrame.location = "blank_page.html";
	var navUrl = this.href.replace(/.html$/, "-nav.html");
	var navFrame = parent.frames["serifxmlNavFrame"];
	if (navFrame) navFrame.location = navUrl;
    });
}

function setupSentContextFrame() {
    $("#prev-sent").click(function() {
	selectSentence("prev"); });
    $("#next-sent").click(function() {
	selectSentence("next"); });
    // Add next/prev key support.
    bind_next_prev_keypress()
}

function selectDetailsTab(tab) {
    if ($(tab).hasClass("selected"))
	return;
    $(tab).siblings().removeClass("selected");
    $(tab).addClass("selected");
    $("div.nav-pane").hide();
    $("#"+tab.id+"-pane", $(tab).parent().parent()).show();
    // Record which tab is selected.
    var textFrame = parent.frames["serifxmlTextFrame"];
    if (textFrame) textFrame.selected_tab_id=tab.id;
}

function setupMentions(noMentionLinks) {
    $("span.mention").hover(enterMention, exitMention);
    if (!noMentionLinks) {
	$("span.mention").click(function() {
	    var entity_id = entityForMention(this);
	    if (entity_id) {
		var textFrame = parent.frames["serifxmlTextFrame"];
		var detailsFrame = parent.frames["serifxmlDetailsFrame"];
		// Get the docid from the containing sentence.
		var sent_id = $(this).closest(".sentence")[0].id;
		var doc_prefix = sent_id.match(/sent-(.*)-([0-9]+)/)[1]
		detailsFrame.location = doc_prefix+"-entities.html#"+entity_id;
		$("#"+entity_id, detailsFrame.document)
		    .removeClass("collapsed-entity");
		return false;
	    }
	});
    }
}

function entityForMention(mention) {
    var entity_css = mention.className.match(/entity-[a-zA-Z_0-9]+/);
    if (entity_css) {
	return entity_css[0];
    }
}

function enterMention() {
    $("span.mention").removeClass("highlight-mention");
    var entity_id = entityForMention(this);
    if (entity_id) {
	$("span."+entity_id).addClass("highlight-mention");
    }
    return false;
}

function exitMention() {
    $("span.mention").removeClass("highlight-mention");
    $(this).parent().closest("span.mention").each(enterMention);
}

function setupParse(root) {
    // Add a top-border to each word to line them up.
    $("div.syntree", root).each(function() {
	var $syntree = $(this);
	var total_height = $syntree.children().height();

	$("div.word", $syntree).each(function() {
	    var bottom = ($syntree.scrollTop() + 
			  $(this).position().top+
			  $(this).outerHeight());
	    var dy = total_height - bottom;
	    //alert("x: "+total_height+", "+bottom+", "+dy);
	    this.previousSibling.style.paddingBottom = dy+"px";
	    //this.style.borderTopWidth = dy+"px";
	});
    });

    // Center children relative to their parents (except the 
    // top-level syntree.)
    $("div.syntree div.syntree ul", root).each(function() {
	var ul_width = $(this).outerWidth(true);
	var li_width = $(this.parentNode).width();
	if (ul_width < li_width) {
	    this.style.marginLeft = (li_width-ul_width)/2 + "px";
	}
    });
}

function bind_next_prev_keypress() {
    $(document).keypress(function(event) {
	// Ignore keypress if we're in any kind of input area.
	var element;
	if(event.target) element=event.target;
	else if(event.srcElement) element=event.srcElement;
	if ($(element).closest("INPUT, TEXTAREA, SELECT")[0])
	    return;
	if ( event.which == 110 ) {
	    selectSentence("next");
	    event.preventDefault();
	}
	else if ( event.which == 112 ) {
	    selectSentence("prev");
	    event.preventDefault();
	}
    });
}

function setupSearchFrame() {
    setupTextFrame(true);

/*



    setupGraphZoom();
    $("input.show-graph").click(function() {
        $(this).closest(".sentence").find(".sent-graph").toggle();
        $(this).val($(this).val()=="Show Graph"?"Hide Graph":"Show Graph");
    });
    $("input.show-parse").click(function() {
        $(this).closest(".sentence").find(".sent-parse").toggle();
        if (!this.parse_is_setup) {
            setupParse($(this).closest(".sentence"));
            this.parse_is_setup = true;
        }
        $(this).val($(this).val()=="Show Parse"?"Hide Parse":"Show Parse");
    });
    $("input.show-context").click(function() {
        $(this).closest(".sentence").find("div.context").toggle();
        $(this).val($(this).val()=="Show Context"?"Hide Context":"Show Context");
    });
*/
}
