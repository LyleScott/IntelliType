/* Lyle Scott, III
 * lyle@digitalfoo.net
 * http://digitalfoo.net
 */

DEBUG = true


var KEY_ENTER = 13;
var HOST = 'http://localhost:5000';
var identifier = location.hostname + '_' + $.browser.version.replace(/[^A-Za-z0-9]+/, '');

function debug(msg) {
	if (DEBUG && typeof console !== undefined) {
		console.log(msg);
	}
}

debug('identifier: ' + identifier);


//
// getAutocompletes
//
//

function getAutocompletesAjaxCall(query) {
	// Make an AJAX call to get a list of autocompletes.
	
	var args = {'n': 2,
			    'mark': true,
			    'query': query,
			    'mark': true,
			    'markL': '<strong>',
			    'markR': '</strong>'}
	var args_ = '?';
	for (i in args) {
		args_ += i + '=' + args[i] + '&';
	}
	
    $.ajax({
        url: HOST + '/' + identifier + args_,
        type: 'OPTIONS',
        datatype: 'json',
        success: getAutocompletesCallback,
        error: ajaxError
    });
}

function getAutocompletesCallback(data, textStatus, jqXHR) {
	// Show possible autocompletes to user.
    var json = JSON.parse(data);
    
    if (typeof json == undefined) {
    	debug('submitAutocompletesCallback: !json:');
    	debug(json);
    	
    	return;
    }
    
    var html = json.join('<br>');
    $('#suggestions').html(html);
}


//
// submitQuery
//
//

function submitQueryAjaxCall(query) {
    // Make an AJAX call to put a query into storage.
    $.ajax({
        url: HOST + '/' + identifier,
        type: 'PUT',
        data: {'query': query},
        datatype: 'json',
        success: submitQueryCallback,
        error: ajaxError
    });
}

function submitQueryCallback(data, textStatus, jqXHR) {
    // Check for a successful return and show a success message.	
    var json = JSON.parse(data);
    
    if (json != true) {
    	debug('submitQueryCallback: !json:');
    	debug(json);
 
    	return;
    }
    
    $('#status').html('query added...');
    
    setTimeout(function() { 
    	$('#status').html('<br>'); 
    	getExistingQueriesAjaxCall();
	}, 500);
}


//
// getExisting
//
//

function getExistingQueriesAjaxCall() {
    // Make an AJAX call to get a list of suggestions.
    $.ajax({
        url: HOST + '/' + identifier,
        type: 'GET',
        datatype: 'json',
        success: getExistingQueriesCallback,
        error: ajaxError
    });
}

function getExistingQueriesCallback(data, textStatus, jqXHR) {
    // Get all existing queries and print them in the #existing div.
    var json = JSON.parse(data);
    
    if (!json || json.length == 0) {
    	debug('getExistingQueriesCallback: !json:');
    	debug(json);
  
    	return;
    }
    
	var html = json.join('<br>');
    $('#existing').html(html);
}


//
// Utilities.
//
//

function ajaxError(jqXHR, textStatus, errorThrown) {
	// Attempt to gracefully print an error in a jQuery AJAX call.
	debug('jQuery AJAX error:');
	debug(textStatus);
	debug(errorThrown);
	$('#existing').html('There was a problem communicating with the server.');
}


$(document).ready(function(){
	
	getExistingQueriesAjaxCall();
	
    $("#query").bind('keyup', function(event) {
    	
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
    	} else {
            // Get suggestions based on what the user is typing.
    		getAutocompletesAjaxCall(query);
    	}
    	
    });  // query keyup
    
});  // end document ready
