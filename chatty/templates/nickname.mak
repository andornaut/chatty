# -*- coding: utf-8 -*-

<%namespace file="base_min.mak" import="*"/>

<form action="/p/nickname" method="post">
	<ul>
		<li>
			<label>
			% if request.session.has_key('nickname'):
				Change your nickname
			% else:
				Choose a nickname
			% endif
			</label>
			${form_errors('changed_nickname')}${h.text('changed_nickname', changed_nickname or (not errors.has_key('changed_nickname') and request.session.get('nickname')) or '')}
		</li>
	</ul>
	<p>
	% if request.session.has_key('nickname'):
		<input type="submit" name="change_nickname" value="Change"/>
		<input type="button" name="reset" value="Reset" onclick="$('#changed_nickname').val('${request.session.get('nickname')}');return false;"/>
	% else:
		<input type="submit" name="set_nickname" value="Set"/>
	% endif			
	</p>
</form>