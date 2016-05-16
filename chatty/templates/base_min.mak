# -*- coding: utf-8 -*-
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" xmlns:tal="http://xml.zope.org/namespaces/tal">
<head>
	<title>chatty.ca</title>
	<meta name="google-site-verification" content="xvzPIyrH9my0uDsbTSX0qaJayMhNbGgK3EVluheHc7U" />
	<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
	<meta name="description" content="Secure encrypted web-based communication" />
	<meta name="keywords" content="communication, secure, encryption, encrypted, web" />
	<link rel="stylesheet" href="/css/main.css" type="text/css" media="screen" charset="utf-8" />
	<link rel="stylesheet" href="/css/chat.css" type="text/css" media="screen" charset="utf-8" />	
	<!--[if IE]>
		<link rel="stylesheet" href="/css/ie.css" type="text/css" media="screen" charset="utf-8" />
	<![endif]-->	
	<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.5.0/jquery.min.js"></script>
	<script type="text/javascript" src="/js/main.js"></script>
% if hasattr(self, 'extra_head'):
	${self.extra_head()}
% endif
</head>
<body ${set_body_class()}>
${next.body()}
</body>
</html>

<%def name="flash()">
    % if request.session.has_key('flash'):
    <div id="flash"><p>${request.session.get('flash')}</p></div>
    <%
        del request.session['flash']
        request.session.save()
    %>
	<script type="text/javascript">
    	flash_callback();
    </script>
    % endif
</%def>

<%def name="flash_message()">
    % if request.session.has_key('flash'):    
    <li id="flash"><p>${request.session.get('flash')}</p></li>
    <%
        del request.session['flash']
        request.session.save()
    %>
	<script type="text/javascript">
    	flash_callback();
    </script>
    % endif
</%def>

<%def name="footer()">
	<div id="footer">
		<p>&copy; 2011 chatty.ca</p>
	</div>
</%def>

<%def name="form_errors(field_name)">
	% if errors and field_name in errors:
		<ul class="errors">
		% for message in errors.get(field_name):
	    	<li>${message}</li>
	    % endfor
	    </ul>
	% endif
</%def>

<%def name="friend_section()">
	% if request.session.get('is_authenticated'):
		<div id="friends"></div>
	% endif	
</%def>

<%def name="login_section()">
	% if request.session.get('is_authenticated'):
		<a href="/p/logout?from=${request.url}" title="Logout">Logout</a>
	% else:
		<a href="#" class="login" title="Login / Register">Login / Register</a>
	% endif	
	<hr/>
	<div id="nickname"></div>
</%def>

<%def name="set_body_class()">
	% if hasattr(self, 'body_class'):
		class="${self.body_class()}"
	% else:
		class="default"
	% endif
</%def>