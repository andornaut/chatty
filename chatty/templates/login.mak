# -*- coding: utf-8 -*-

<%namespace file="base_min.mak" import="*"/>

${flash()}

<div class="divide-form">
<h3>Login</h3>
<form action="/p/login" method="post">
	<ul>
		<li>
			<label for="login_nickname">Nickname</label>
			${form_errors('login_nickname')}${h.text('login_nickname', login_nickname or '')}
		</li>
		<li>
			<label for="login_password">Password</label>
   			${form_errors('login_password')}${h.password('login_password', login_password or '')}
   		</li>
   	</ul>
	<p>${h.submit('login', 'Login')}</p>    
</form>
</div>

<div class="divide-form-right">
<h3>Register</h3>
<form action="/p/register" method="post">
	<ul>
		<li>
			<label for="register_nickname">Nickname</label>
			${form_errors('register_nickname')}${h.text('register_nickname', register_nickname or '')}
		</li>
		<li>
			<label for="register_email">Email <em>(Optional)</em></label>
			${form_errors('register_email')}${h.text('register_email', register_email or '')}
		</li>
   		<li>
   			<label for="register_password">Password</label>
   			${form_errors('register_password')}${h.password('register_password', register_password or '')}
		</li>
   		<li>
   			<label for="register_confirm_password">Confirm password</label>
   			${form_errors('register_confirm_password')}${h.password('register_confirm_password', register_confirm_password or '')}
		</li>
	</ul>
	<p>${h.submit('register', 'Register')}</p>    
</form>
</div>
<a href="#" class="close" title="Close">x</a>