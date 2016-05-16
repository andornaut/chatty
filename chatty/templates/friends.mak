<h3>Friends (<span>${count}</span>)</h3>
<ul>
	% for friend in friends:
		% if friend.get('is_online'):
			<li><a href="#" rel="/msg ${friend.get('nickname','')} " class="chat-add-input">${friend.get('nickname','')}</a></li>
		% else:
			<li>${friend.get('nickname','')}</li>
		% endif
	% endfor
</ul>