$(document).ready(function() {
	var ajax_login = new AjaxPage('#window-overlay',
									'/p/login?from=' + window.location.href);								
	$('a.login').live('click',function(event) {
		window_overlay.open(event);
		ajax_login.open();
	});
	$('#window-overlay .close').live('click', window_overlay.close);	
	var ajax_nick = new AjaxPage('#nickname',
									'/p/nickname?from=' + window.location.href);
	ajax_nick.open();
	
	var friend_list = new FriendList('#friends');
	friend_list.update();		
});

var FriendList = function(selector) {
	this.element = $(selector);
}

FriendList.prototype = {
	update: function(no_timeout) {
		var self = this;
		$.ajax({url: '/p/friends', 
			type: 'GET', 
			cache: false,
			error: function(XMLHttpRequest, textStatus, errorThrown) {
				alert(errorThrown);
			},
			success: function(data, textStatus, xhr) {
				self.element.html(data);
				if (!no_timeout) { 
					setTimeout(function() { self.update(); } ,30000);
				}	
		   	}
		});
	},
}

var AjaxPage = function(selector, url) {
	this.selector = selector;
	this.url = url;
}

AjaxPage.prototype = {	
	open: function() {
		var self = this; 
		$.ajax({
			url: this.url, 
			type: 'GET', 
			cache: false,
			error: function(XMLHttpRequest, textStatus, errorThrown) {
				alert(errorThrown);
			},
			success: function(data, textStatus, xhr) {	
				if (data.status == 'REDIRECT') {
					window.location.href=data.body;
				} else {
					$(self.selector).html(data)
						.find('form')
						.live('submit', function(event) {
							self.post(event);
						});
				}
	   		}
		});
	},
	
	post: function(event) {
		event.preventDefault();
		$('#flash').remove();
		var self = this,
			form = $(event.target),
			data = form.serialize(),
			url = form.attr('action') + '?from=' + window.location.href;		
		$.ajax({
			url: url, 
			type: 'POST', 
			cache: false,
			data: data,
			error: function(XMLHttpRequest, textStatus, errorThrown) {
				alert(errorThrown);
			},
			success: function(data, textStatus, jqXHR) {	
				if (data.status == 'REDIRECT') {
					window.location.href=data.body;
				} else {
					$(self.selector).html(data);
				}
	   		},	   	
		});
	},
}

var window_overlay = {
	open: function(event) {
		event.preventDefault();
		var self = this;
		$('body')
			.append($('<div/>',{'id':'cover'}).click(function(event) { self.close(event); }))
			.append($('<div/>',{'id':'window-overlay'}));
	},
	
	close: function(event) {
		event.preventDefault();
		$('#window-overlay').remove();
		$('#cover').remove();
	},
}

function flash_callback() {
    var flash = $('#flash');
   	setTimeout(function() {
    	flash.animate({opacity: 0},1000)
    	.animate({height: 0,margin: 0,padding:0}, 1000, function() {
   				$(this).next('script').remove();
   				$(this).remove();
		});
    }, 15000);
}