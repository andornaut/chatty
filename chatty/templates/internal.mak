# -*- coding: utf-8 -*-
<%inherit file="/base.mak" />

<div id="wrap-chat" class="clearfix">
<div id="chat">
${self.flash()}
${next.body()}
</div>

<div id="sidebar">
${self.login_section()}
</div>
</div>