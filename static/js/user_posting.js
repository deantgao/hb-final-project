// $('#saveButton').on('click', function() {
// 			var disabled_value = $('.category').prop('disabled');
// 			$('.category').prop('disabled', !disabled_value);
// 		});

// $('#saveButton').on('click', function() {

// $('#editButton').hide()

// 	$('#editButton').on('click', function() {
// 			var enabled_value = $('.category').prop('disabled', false);
// 		});
function postComment(evt) {
	evt.preventDefault();
	var comment = $('#comment_body').val();
	var post_id = $('#post_id').val();
	var data = {'comments' : comment,
				'post_id' : post_id};
	$.post('/save_comment', data, function (results) {
		$('#new_comment').append("<div class='post_comment'>" + comment + " posted at: " + results['results'] + "</div>");
});}

$('#post_comment').on('submit', postComment);

function makeGetRequest(evt) {
	evt.preventDefault();
	var request_message = $('#get_request').val();
	var post_id = $('#post_id').val();
	var data = {'request_message' : request_message,
				'post_id' : post_id};
	$.post('/make_get_request', data, function (results) {
			var disable_request = $('#get_request').prop('disabled', true);
			var request_receipt = $('#request_receipt').append("<h6>" + results['results'] + "</h6>");
		})
}

$('#get_request').on('click', makeGetRequest);

// function receiveGetRequest() {
// 	var post_id = $('#post_id').val();
// 	var request_message = $('#get_request').val();
// 	var data = {'request_message' : request_message,
// 				'post_id' : post_id};
// 	$.post('/send_get_request', data, function (results) {

// 	})
// }

// $('#get_request').on('click', receiveGetRequest)

// function saveCategories(evt) {
// 	evt.preventDefault();
// 	var categories = $('#save_categories').serialize(); // $ -> jquery
// 	$.get('/save_categories?' + categories, function (categories) {
// 		$('#category_tags').html("");
// 		for (category of categories.results) {
// 			$('#category_tags').append("<span class='category_tag'>" + category + "</span>");
// 		}

// 	}); 
// }

// $('#save_categories').on('submit', saveCategories);

// function confirmGivePost(evt) {
// 	evt.preventDefault();
// 	var categories = $('#save_categories').serialize();
// 	var give_form = $('#confirm_post').serialize();
// 	var data = categories + give_form
// 	console.log(data)
// 	$.post('/confirm_post', data, function(results) {
// 		console.log('hi');
// 	}); // function() {update user homepage})
// }

// $('#confirm_post').on('submit', confirmGivePost);
// go to the server function in 1st
// argument, take the return results and pass them into function
// in 2nd argument

// $.get -> jquery implementation of ajax get request