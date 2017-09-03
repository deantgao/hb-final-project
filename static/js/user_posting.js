$('#if-deleted').hide();

function postComment(evt) {
	evt.preventDefault();
	var comment = $('#comment_body').val();
	var post_id = $('#post_id').val();
	var data = {'comments' : comment,
				'post_id' : post_id};
	$.post('/save_comment', data, function (results) {
		$('#new_comment').append("<div class='post_comment'>" + comment + " posted at: " + results['results'] + "</div>");
		$('#comment_body').val("");
});}

$('#post_comment').on('submit', postComment);

function makeGetRequest() {
	var request_message = $('#message').val();
	var post_id = $('#post_id').val();
	var data = {'request_message' : request_message,
				'post_id' : post_id};
	console.log(data);
	$.post('/make_get_request', data, function (results) {
			var disable_request = $('#get_request').prop('disabled', true);
			var request_receipt = $('#sent_receipt').append("<h6>" + results['results'] + "</h6>");
			$('#message').val("")
		})
}

$('#get_request').on('click', makeGetRequest);

function makeGiveOffer() {
	var offerMessage = $('#message').val();
	console.log(offerMessage);
	var postId = $('#post_id').val();
	var data = {'message' : offerMessage,
				'post_id' : postId};
	console.log(data);
	$.post('/make_give_offer', data, function (results) {
			var disable_button = $('#give_offer').prop('disabled', true);
			var request_receipt = $('#sent_receipt').append("<h6>" + results['results'] + "</h6>");
			$('#message').val("")
		})
}

$('#give_offer').on('click', makeGiveOffer);

function deletePosting() {
	var postId = $('#delete').val();
	var data = {post_id : postId};
	$.get('/delete_posting', data, function (results) {
		console.log(results['results']);
		$('#active_post').remove();
		$('#if-deleted').append("Your posting has been deleted.");
		$('#if-deleted').show();
	})
}
$('#delete').on('click', deletePosting)