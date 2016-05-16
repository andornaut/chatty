# -*- coding: utf-8 -*-
<%inherit file="/base.mak" />

<%def name="extra_head()">
<link type="text/css" rel="stylesheet" href="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.8/themes/base/jquery-ui.css"/>
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.9/jquery-ui.min.js"></script>
<script type="text/javascript" src="/js/aes-encryption.js"></script>
<script type="text/javascript" src="/js/jquery.cookie.js"></script>
<script type="text/javascript" src="/js/jquery.sha1.js"></script>
<script type="text/javascript" src="${url_orbited}/static/Orbited.js"></script>
<script type="text/javascript" src="${url_orbited}/static/protocols/stomp/stomp.js"></script>
<script type="text/javascript" src="/js/chat.js"></script>

<script type="text/javascript">
//<![CDATA[
$(document).ready(function() {
	var chat = new Pssty({'nickname': '${request.session.get('nickname')}',							
							'cookie_name': '${cookie_name}',
							'private_key': '${private_key or ''}'});
	chat.init();
	$('#pop-out').click(pop_out);
	var chat_scroll = function(event) {
		event.preventDefault();
		chat.scroll();
	}	
	$("#chat").resizable({ 
		alsoResize: '#chat ul',
		handles: 's',
		minHeight: 200,
		resize: chat_scroll 
	});
	$('.ui-resizable-handle')
		.addClass('ui-icon')
		.addClass('ui-icon-carat-1-s')
		.attr('style', 'background-position: -62px -1px;bottom: 0;height: 10px;left:288px;padding:2px 0;width: 21px;');

});

function pop_out(event) {
	var child = window.open(
				String(window.location),
				'chat','width=300,height=465,directories=no,location=no,menubar=no,resizable=yes,status=no,toolbar=no'); 
	child.focus();
	event.preventDefault();
	window.location.href='/';
}
//]]>
</script>
</%def> 

<div id="wrap-chat">
<div id="chat">
	<ul>
		<li>
		% if conversation.get('is_anonymous'):
			-- This is an anonymous conversation<br/>
		% else:
			-- Title: <strong>${conversation.get('title')}</strong><br/>
		% endif
		% if conversation.get('topic'):
			-- Topic: <strong>${conversation.get('topic')}</strong><br/>
			-- Topic set by <strong>${conversation.get('topic_changed_by')}</strong> on ${conversation.get('topic_changed')}<br/>
		% else:
			-- A topic has not been set. Use /topic &lt;topic&gt; to set one.<br/>
		% endif
		% if not conversation.get('is_anonymous'):
			-- Created by <strong>${conversation.get('created_by')}</strong> on ${conversation.get('created')}
		% else:		
			-- Created on ${conversation.get('created')}
		% endif
		${self.flash_message()}		
		</li>
	</ul>
% if request.session.has_key('nickname'):
	<form action="." method="post">
		<p><textarea name="body" rows="2" cols="2" tabindex="1000"></textarea>
		<input type="submit" value="send" tabindex="1001"/><a href="#" title="Pop Out" id="pop-out" class="ui-icon ui-icon-newwin"></a></p>
	</form>
% else:
	<p class="note">In order to send messages or issue commands, you must first enter your nickname into the input box above and click on the "set" button.</p>
% endif
</div>

<div id="sidebar">
${self.login_section()}
	
% if request.session.get('is_authenticated'):
	<hr/>
	<div id="friends"></div>
% endif
</div>
</div>