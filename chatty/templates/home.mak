# -*- coding: utf-8 -*-
<%inherit file="/base.mak" />

<div id="wrap-outer">
<div id="wrap-middle">
<div id="wrap-inner">

${self.flash()}
<div class="container">
<div class="divide-form-left">
<h2>Start a Public Chat</h2>
<p>Public chats are accessible to everyone. They are listed on this page, and are indexed by search engines.</p>
		
% if not request.session.get('is_authenticated'):
<p>You'll need an active account in order to start a public chat.
You can <a href="/p/login" class="login" title="Login / Register">login or register here</a>.</p> 
% endif

<form method="post" action=".">
	<ul>		
% if not request.session.get('is_authenticated'):
		<li>
			<label for="login_nickname">Nickname</label>
			${self.form_errors('login_nickname')}${h.text('login_nickname', login_nickname or (not errors.has_key('login_nickname') and request.session.get('nickname')) or '')}
		</li>
		<li>
			<label for="login_password">Password</label>
   			${self.form_errors('login_password')}${h.password('login_password', login_password or '')}
   		</li>	
% endif	
		<li>
			<label for="title">Title</label>
			${self.form_errors('title')}${h.text('title', title or '')}
		</li>
	</ul>
	<p>${h.submit('start_public', 'Start a public chat')}</p>
</form>
</div>

<div class="divide-form">
<h2>Start an Anonymous Chat</h2>
<p>Anonymous chats have randomized URLs which are not published anywhere on this site.
You do not need an account to start one.</p>  
<form method="post" action=".">
	<p>${h.submit('start_anonymous', 'Start an anonymous chat')}</p>
</form>
</div>
</div>
</div>
</div>
</div>

<div id="sidebar">
${self.login_section()}
</div>

<div id="sidebar-lower">
${self.friend_section()}
</div>

<div id="chats">
<h2>Public Chats</h2>
<ul>
	% for row in conversations:
	<li>
		<div class="head"><a href="/${row.get('title')}">${row.get('title')}</a></div>
		% if row.get('topic'):
		<div class="sub-head">Topic: <strong>${row.get('topic')}</strong></div>
		% endif
		<div class="details">created by <strong>${row.get('created_by')}</strong> on ${row.get('created')}</div>
	</li>
	% endfor
</ul>
</div>

<%def name="body_class()">
	main
</%def>