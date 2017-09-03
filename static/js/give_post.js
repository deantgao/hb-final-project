$("#submit_post").on('click', function() {
	var disable_button = $('#submit_post').prop('disabled', false);
});

// $('#saveButton').on('click', function() {
// 			var disabled_value = $('.category').prop('disabled');
// 			$('.category').prop('disabled', !disabled_value);
// 		});

// $('#saveButton').on('click', function() {

// $('#editButton').hide()

// 	$('#editButton').on('click', function() {
// 			var enabled_value = $('.category').prop('disabled', false);
// 		});

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

