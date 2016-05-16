# -*- coding: utf-8 -*-
<%inherit file="/internal.mak" />

<h1>Help</h1>

<div id="documentation">
<h3>Commands</h3>
<dl>
	<dt>/clear</dt>
	<dd>Clears the conversation screen</dd>
	<dt>/end</dt>
	<dd>Permanently deletes the conversation and purges your encryption password</dd>
	<dt>/encrypt &lt;password&gt;</dt>
	<dd>Encrypts all subsequent messages with the supplied password</dd>
	<dt>/nocrypt</dt>
	<dd>Deletes your encryption password; all subsequent messages will be public</dd>
	<dt>/logout</dt>
	<dd>Deletes your encryption password and logs you out of your current session</dd>
	<dt>/msg &lt;nickname&gt; &lt;message&gt;</dt>
	<dd>Sends a private (though unencrypted) message</dd>
	<dt>/reply &lt;message&gt;</dt>
	<dd>Sends a private (though unencrypted) message to the last user who sent you a private message</dd>
	<dt>/topic &lt;topic&gt;</dt>
	<dd>Changes the conversation topic</dd>
</dl>
</div>