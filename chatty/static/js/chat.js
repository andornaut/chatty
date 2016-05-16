var PsstyScroller = function(selector) {
	this.element = $(selector);
}

PsstyScroller.prototype = {	
	threshold: 25,
	
	append: function(content) {
		var is_scrollable = this.is_scrollable();
		this.element.append(content);
      	if (is_scrollable) {
	  		this.scroll();
		}		
	},
	
	prepend: function(content) {
		var is_scrollable = this.is_scrollable();
		this.element.prepend(content);
      	if (is_scrollable) {
	  		this.scroll();
		}		
	},
	
	is_scrollable: function() {
		var scroll_height = 0,
			scroller = this.element[0];
		if (scroller.scrollHeight > 0) {
			scroll_height = scroller.scrollHeight;
		} 
		var offset = scroller.style.pixelHeight ? scroller.style.pixelHeight : scroller.offsetHeight;
		var scrollTop = this.element.scrollTop();
		return scroll_height - scrollTop - offset < this.threshold;
	},
	
	scroll: function() {
  		var scroll_top = this.element.attr('scrollHeight') - this.element.height();
		this.element.scrollTop(scroll_top);	
	},
}

var PasswordStore = function(cookie_name, key) {
	this.cookie_name = cookie_name;
	this.key = $.sha1(key);
}

PasswordStore.prototype = {	
	remove: function() {
		this.password_cache = null;
		this._write();
	},
	
	get: function() {
		if (! this.password_cache) {
			this.password_cache = this._read(); 
		}
		return this.password_cache;
	},
	
	save: function(password) {
		if (!(typeof password == 'string' && password.length)) {
			throw 'InvalidPassword';
		}
		password = $.sha1(password); 
		if (password != this.password_cache) {	
			this.password_cache = password;
			this._write();
		}
	},

	_read_map: function() {
		var map = {};
		var cookie_value = $.cookie(this.cookie_name);
		if (cookie_value) {
			var values = cookie_value.split(',');
			for (var i=0; i< values.length; i++) {
				key_value = values[i].split(':');
				var key = key_value[0];
				if (typeof key == 'string' && key.length) {
					map[key] = key_value[1];
				}
			}
		}
		return map;
	},

	_read: function() {
		var pw = this._read_map()[this.key];
		if (!(typeof pw == 'string' && pw.length)) {
			pw = null;
		}
		return pw;
	},

	_write: function() {
		var map = this._read_map();
		if (this.password_cache) {
			map[this.key] = this.password_cache;
		} else {
			delete map[this.key];
		}
		var cookie_value = '';
		for (var key in map) {
			cookie_value += key + ':' + map[key] + ',';
		} 
		$.cookie(this.cookie_name, cookie_value);
	}
}

var Pssty = function(options) {  	
	var defaults = 	{
		chat_selector: '#chat',
		friends_selector: '#friends',
		cookie_name: 'chat-store',
		error_class: 'chat-error',
		add_input_class: 'chat-add-input',
		send_class: 'chat-send',
		message_class: 'chat-message',
		encrypted_message_class: 'chat-encrypted-message',
		private_message_class: 'chat-private-message',
		system_message_class: 'chat-system-message',
		orbited_port: 61613,
		orbited_user: 'guest',
		orbited_pass: 'guest',
	}
	options = options || {};
    for (var value in defaults) {
      	if (!options.hasOwnProperty(value))
	        options[value] = defaults[value];
    }
    this.options = options;
}

Pssty.prototype = {	
	init: function() {
		var self = this,	
			chat = $(this.options.chat_selector).first(),
			url = window.location.href;
		this.conversation = chat.find('ul').first()
		this.send_button = chat.find('input[type=submit]').first();
		this.text_input = chat.find('[name=body]').first().focus();	
		this.friends = $(this.options.friends_selector).first();	
		this.nickname = this.options.nickname;	
		this.private_key = this.options.private_key;
     	this.scroller = new PsstyScroller(this.conversation);
		this.title = url.substr(url.lastIndexOf('/')+1);
		this.password_store = new PasswordStore(this.options.cookie_name, this.title);	
		this.is_encrypted = this.password_store.get() ? true : false;
		this.send_button.click(function(event) {
			event.preventDefault();
			self._send();	
		}).blur(function(event) {
			self.text_input.focus();
		});
		this.text_input.keydown(function(event) {
			if (event.which == 13) {
				event.preventDefault();
				self._send();
       		}
       	});
		$('.' + this.options.add_input_class).live('click', function(event) {
			event.preventDefault();
			var input_val =  $(event.target).attr('rel');
		 	self._add_input(input_val);
		});
		$('.' + this.options.send_class).live('click', function(event) {
			event.preventDefault();
			var input_val =  $(event.target).attr('rel');
			self._process_input(input_val);
		});	
       	$(window).resize(function() {
  			self.scroller.scroll();
		});		
		this._get_latest_messages();
		this._subscribe();
	},
	
	scroll: function() {
		this.scroller.scroll();
	},
	
	_add_input: function(input_val) {
		this.text_input.val(input_val).focus();
	},
	
	_decrypt: function(message) {
		var password = this.password_store.get();
		if (password) {
 			message = Aes.Ctr.decrypt(message, password, 256);
 		}
 		return message;	
	},
	
	_encrypt: function(message) {
		var password =  this.password_store.get();
		if (password) {
  			return Aes.Ctr.encrypt(message, password, 256);	
  		}
		throw 'PasswordNotFound';
	},
	
	_error: function(detail) {
		var msg = 'Sorry, chat experienced an error. ';
		if(detail !== undefined) {
			msg += detail;
		}
		alert(msg);
	},
	
	_get_latest_messages: function() {
		var self = this,
			url = window.location.href + '/latest';
			//oldest_id = this.conversation.find('li input').first().val();
		$.ajax({url: url, 
			type: 'GET', 
			cache: false,
			error: function(XMLHttpRequest, textStatus, errorThrown) {
				self._error();
			},
			success: function(data, textStatus, xhr) {
				var html = new Array();
				$.each(data.messages, function() { 
					html.push(self._render_message(this)[0]);
				});	
				self.scroller.prepend(html);			
		   	}
		});
	},
	
	_process_input: function(input_val) {
		var self = this,
			body = input_val,
			command = null;
		if (input_val.startsWith('/')) {
			command = input_val.toLowerCase();
			var pos = command.indexOf(' ');
			var end = (pos > 0 ? pos : command.length);
			command = command.substr(1, end - 1);	
			body = $.trim(input_val.substr(end));
		}
		
		function create_message(body, is_error) {
			return {'status': is_error ? 'ERROR' : 'OK', 'body': body}			
		}		

		switch (command) {	
		case 'c':
		case 'clr':
		case 'clear':
			var last_message = this.conversation.find('li:has(input):last');
			last_message.css('display','none').find('table').remove();
			this.conversation.find('li').not(last_message).remove();
			break;
		case 'encrypt':	
		case 'private':	
			var response = null;
			if (body.length > 2) {		
				this.is_encrypted = true;		
				this.password_store.save(body);
				response = create_message('Your messages are now private! <a href="' + window.location.href + '">Reload previous messages</a>');
			} else {
				response = create_message('Your encryption password must contain at least 3 characters',true);
			}
			this._process_response(response);
			break;		
		case 'nocrypt':		
		case 'public':
			this.is_encrypted = false;
			this.password_store.remove();
			response = create_message('Your messages are now public');
			this._process_response(response);	
			break;			
		default:
			var data = command ? '&command=' + encodeURIComponent(command) : '';
			if (!command && this.is_encrypted) {
				body = this._encrypt(body);
	 			data = '&is_encrypted=True';
			}
			body = encodeURIComponent(body);
	 		data += '&body=' + body;			
			$.ajax({url: window.location.href + '/post', 
				type: 'POST', 
				cache: false,
				data: data,
				error: function(XMLHttpRequest, textStatus, errorThrown) {
					self._error();
				},
				success: function(data, textStatus, xhr){
					self._process_response(data);    					
	    		},
			});
		}
	},
	
	_process_response: function(data) {
		var self = this;
		
		function add_response(data) {
			if (data.body !== undefined) {							
				var html = $('<li/>', {
							'class': data.status=='ERROR' ? self.options.error_class : self.options.system_message_class,
							'html': data.body,
							});
				self.conversation.append(html);
				self.scroller.scroll();
			}	
		}
		
		switch (data.status) {
		case 'FRIEND':
			add_response(data);
			break;
		case 'MESSAGE':
			var html = this._render_message(data);
			this.scroller.append(html);		
			break;	
		case 'NICKNAME':
			this.nickname = data.nickname;
			add_response(data);
			break;
		case 'REDIRECT':
			window.location.href = data.body;
			break;	
		default:
			add_response(data);
		}
	},
	
	_render_message: function(data) {
		var self = this,
			id = data.id,
			body = data.body,
			nickname = data.nickname,
			is_encrypted = data.is_encrypted,
			is_private = data.is_private,
			message_class = this.options.message_class;
		if (is_encrypted) {
			body = this._decrypt(body);
			message_class = this.options.encrypted_message_class;
		} else if (is_private) {
			message_class = this.options.private_message_class;
		}
		var nickname_element = null;
		if (nickname == this.nickname) {
			nickname_element = ($('<span/>', {'text': nickname}));
		} else {
			nickname_element = $('<a/>', {
				'class': this.options.add_input_class,
				'href': '#',
				'rel': '/msg ' + nickname + ' ',
				'text': nickname,
			});
		}
		var td = $('<td/>').text(body),
			th = $('<th/>').append('&lt;').append(nickname_element).append('&gt;');
		if (this.nickname && this.nickname != nickname) {
			var td_el = td[0];
			td_el.innerHTML = td_el.innerHTML.replace(this.nickname, '<strong>' + this.nickname + '</strong>');					
		}
		return $('<li/>', {'class': message_class})			
			.append($('<input/>', {
				'type': 'hidden',
				'val': id}))
			.append($('<table/>')
				.append($('<tr/>')
					.append(th)
					.append(td)
				)
			);	
	},
		
	_send: function() {
		var input_val = this.text_input.val();
		this.text_input.val('').focus();
		this._process_input(input_val);
	},
	
	_subscribe: function() {
		var self = this;
		document.domain=document.domain; // Required for cross-port iframe JS
        TCPSocket = Orbited.TCPSocket;
        stomp = new STOMPClient();
        stomp.onclose = function(code) {
        	self._error('Lost connection (' + code + ')');
        };
        stomp.onerror = function(error) {
        	self._error(error);
        };
        stomp.onerrorframe = function(frame) {
        	self._error(frame.body);
            stomp.reset();
            stomp.subscribe('/exchange/conversation/' + self.title);
            if (self.private_key) {
				stomp.subscribe('/exchange/private/' + self.private_key);
			}
        };
        stomp.onconnectedframe = function(){
            stomp.subscribe('/exchange/conversation/' + self.title);
            if (self.private_key) {
          	 	stomp.subscribe('/exchange/private/' + self.private_key);
            }
        };
        stomp.onmessageframe = function(frame){
            self._process_response(jQuery.parseJSON(frame.body));
        };
        stomp.connect('localhost',
        				this.options.orbited_port,
        				this.options.orbited_user,
        				this.options.orbited_pass);  
	},	
}

String.prototype.startsWith = function(str){
    return this.substr(0, str.length) === str;
}
