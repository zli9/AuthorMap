$('input[type=checkbox]').on('change', function (e) {
	if ($('input[type=checkbox]:checked').length > 2) {
	$(this).prop('checked', false);
	alert("A maximum of two authors can be marked for comparison!");
	} else if ($('input[type=checkbox]:checked').length == 2) {
	checkedAuthors = []
	$('input[type=checkbox]:checked').each(function(){
	checkedAuthors.push($(this).val());
	});
	update_values(checkedAuthors)
	}
});

function update_values(a) {
        $.getJSON("/getsharedpublications",
	{
	   author1 : a[0],
	   author2 : a[1]
	},
	function(data) {
		$("#num_shared_pub").text(data.num_shared_pub)});
}
