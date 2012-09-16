/* Lyle Scott, III
 * lyle@digitalfoo.net
 * http://digitalfoo.net
 */

var KEY_ENTER = 13;
var HOST = 'http://localhost:8080';


//
// getAutocompletes
//
//

function getSuggestionAjaxCall(query) {
	// Make an AJAX call to get a list of suggestions.
    $.ajax({
        url: HOST + '',
        data: {'userinput': query, 'cb': 'get_autocompletes', 'n': 7,
        	   'mark': true},
        datatype: 'jsonp',
        jsonp: 'callback',
        jsonpCallback: 'get_autocompletes',
        success: getAutocompletesCallback,
        error: ajaxError
    });
}

function getAutocompletesCallback(data, textStatus, jqXHR) {
	// 
    var html = '';
    var json = parseJsonp(data, 'get_autocompletes(', 'getAutocompletes');
    
    if (json) {
    	html = 'query added...';
    } 
    
    if (json) {
        html = json.results.join('<br>');
        html = markToStrong(html);
    }
    
    $('#suggestions').html(html);
}


//
// submitQuery
//
//

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
    // Check for a successful return and show a success message.	
    var html = '';
    var json = parseJsonp(data, 'submit_query(', 'submitQueryCallback');
    
    if (json) {
    	html = 'query added...';
    } 
    
    $('#status').html(html);
    setTimeout(function() { $('#status').html(''); }, 1500);
}


//
// getExisting
//
//

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
    // Get all existing queries and print them in the #existing div.
    var html = '';
    var json = parseJsonp(data, 'get_existing(', 'getExistingQueries');
    
    if (json) {
    	html = json['results'].join('<br>');
    }
 
    $('#existing').html(html);
}

//
// Utilities.
//
//

function ajaxError(jqXHR, textStatus, errorThrown) {
	// Attempt to gracefully print an error in a jQuery AJAX call.
    if (console && console.log) {
        console.log('jQuery AJAX error:\n' +
        		    textStatus + '\n' +
        		    errorThrown);
    }
}

function markToStrong(query) {
	// Replace the MARKS with strongs.
	query = query.replace(/__MARK_START__/g, '<strong>');
    query = query.replace(/__MARK_END__/g, '</strong>');
 
    return query;
}

function parseJsonp(data, prefix, error_label) {
	// Parse a jsonp callback valid JSON.
	data = data.substring(prefix.length, data.length); 
	data = data.substring(0, data.length-1);
	
    try {
        return json = $.parseJSON(data);
    } catch (e) {
        if (console && console.log) {
        	console.log('error ' + error_label + ': ' + e);                      	
        	console.log(e);
        }
    	
    	return 'ERROR';
    }
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
