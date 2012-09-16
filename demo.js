/* Lyle Scott, III
 * lyle@digitalfoo.net
 * http://digitalfoo.net
 */

var KEY_ENTER = 13;
var HOST = 'http://localhost:8080';

function ajaxError(jqXHR, textStatus, errorThrown) {
	// Attempt to gracefully print an error in a jQuery AJAX call.
    if (console && console.log) {
        console.log('jQuery AJAX error:\n' +
        		    textStatus + '\n' +
        		    errorThrown);
    }
}

function getSuggestionAjaxCall(query) {
	// Make an AJAX call to get a list of suggestions.
    $.ajax({
        url: HOST + '',
        data: {'userinput': query, 'cb': 'get_suggestions', 'n': 7, 'mark': true, 'next_token_only': true},
        datatype: 'jsonp',
        jsonp: 'callback',
        jsonpCallback: 'get_suggestions',
        success: getSuggestionsCallback,
        error: ajaxError
    });
}

function getSuggestionsCallback(data, textStatus, jqXHR) {
	// Parse the returned value as JSON.
    data = data.substring('get_suggestions('.length, data.length); 
    data = data.substring(0, data.length-1);
    
    var html = '';
    
    try {
        var json = $.parseJSON(data);
        if (json && json.results) {
            html = json.results.join('<br>');
        }
    } catch (e) {
    	if (console && console.log) {
            console.log('error in the get_suggestions() callback: ' + e);                          
            console.log(e);
        }
    }
    
    if (html.length) {
        html = html.replace(/__MARK_START__/g, '<strong>');
        html = html.replace(/__MARK_END__/g, '</strong>');
    }

    $('#suggestions').html(html);
}

function submitQueryAjaxCall(query) {
    // Make an AJAX call to get a list of suggestions.
    $.ajax({
        url: HOST,
        data: {'userinput': query, 'cb': 'submit_query'},
        datatype: 'jsonp',
        jsonp: 'callback',
        jsonpCallback: 'submit_query',
        success: submitQueryCallback,
        error: ajaxError
    });
}

function submitQueryCallback(data, textStatus, jqXHR) {
    // Parse the returned value as JSON.
    data = data.substring('submit_query('.length, data.length); 
    data = data.substring(0, data.length-1);
    
    var html = '';
    
    try {
        var json = $.parseJSON(data);
        if (json) {
        	html = 'query added...';
        }
    } catch (e) {
        if (console && console.log) {
        	console.log('error in the submit_query() callback: ' + e);                      	
        	console.log(e);
        }
    }
    
    $('#status').html(html);
    setTimeout(function() { $('#status').html(''); }, 1500);
}

function getExistingQueriesAjaxCall(query) {
    // Make an AJAX call to get a list of suggestions.
    $.ajax({
        url: HOST,
        data: {'cb': 'get_existing'},
        datatype: 'jsonp',
        jsonp: 'callback',
        jsonpCallback: 'get_existing',
        success: getExistingQueriesCallback,
        error: ajaxError
    });
}

function getExistingQueriesCallback(data, textStatus, jqXHR) {
    // Parse the returned value as JSON.
    data = data.substring('get_existing('.length, data.length); 
    data = data.substring(0, data.length-1);

    var html = '';
    
    try {
        var json = $.parseJSON(data);
        if (json) {
        	html = json['results'].join('<br>');
        }
    } catch (e) {
        if (console && console.log) {
        	console.log('error in the get_existing() callback: ' + e);                      	
        	console.log(e);
        }
    }
 
    $('#existing').html(html);
}


$(document).ready(function(){
	
	getExistingQueriesAjaxCall();
	
    $("#userinput").bind('keyup', function(event) {
    	
    	// Bail if no input in the text entry.
    	if (!$(this).val()) {
            return;
        }
    	
    	var query = $(this).val();

    	if (event && event.keyCode == KEY_ENTER) {
            // Add the query to the collection of known queries.
            submitQueryAjaxCall(query);
            $(this).val('');
            $('#suggestions').html('');
            getExistingQueriesAjaxCall();
    	} else {
            // Get suggestions based on what the user is typing.
    		getSuggestionAjaxCall(query);
    	}
    });  // userinput keyup
    
});  // end document ready
