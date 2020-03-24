function ClearModel(){
	$('#search_modal').find(".modal-title").html("");
	$('#search_modal').find(".modal-body").html("");
	$('#search_modal').find(".modal-footer").html("");
	$('#search_modal').modal('hide');
}

function FillModel(item){
	if (item['success']){
		$('#search_modal').find(".modal-title").html(item['header']);
		$('#search_modal').find(".modal-body").html(item['body']);
		$('#search_modal').find(".modal-footer").html(item['footer']);
		$('#search_modal').modal('show');
	}else{
		console.log("ERROR:" + item['status'] + ":" + item['reason']);
	}
}

function CallAJAXToModel(url){
	$.ajax(url, {
		success: function(jsonitem) {
			var item = JSON.parse(jsonitem)
			FillModel(item);
		}
	})
}

function SearchMovie(query, year=null, page=1){
	url = '%%BASEURL%%scraper/ripper/searchmovie/' + query + '/' + page + '/'
	if (year != null) url += year + '/';
	CallAJAXToModel(url);
}

function ButtonSearchMovie(){
	name = $('#disctypesection').find('input[name="name"]').val()
	year = $('#disctypesection').find('input[name="year"]').val()
	if (year == "") year = null;
	if (name != ""){
		SearchMovie(name, year, 1);
	}
}

function ButtonFindMovie(){
	imdbid = $('#disctypesection').find('input[name="imdbid"]').val()
	if (imdbid != ""){
		CallAJAXToModel('%%BASEURL%%scraper/ripper/findmovie/' + imdbid + '/');
	}
}

function PopulateMovie(id){
	$.ajax('%%BASEURL%%scraper/ripper/getmovie/' + id + '/', {
		success: function(jsonitem) {
			var item = JSON.parse(jsonitem)
			if (item['success']){
				ClearModel();
				$('#disctypesection').find('input[name="name"]').val(item['response']['title']);
				$('#disctypesection').find('input[name="year"]').val(item['response']['release_date'].substring(0, 4));
				$('#disctypesection').find('input[name="imdbid"]').val(item['response']['imdb_id']);
				$('#disctypesection').find('select[name="originallanguage"]').val(item['response']['original_language']);
				$('#disctypesection').find('input[name="moviedbid"]').val(item['response']['id']);
				 
			}
		}
	})
}

function SearchTVShow(query, page=1){
	CallAJAXToModel('%%BASEURL%%scraper/ripper/searchtvshow/' + query + '/' + page + '/');
}

function ButtonSearchTVShow(){
	name = $('#disctypesection').find('input[name="name"]').val()
	if (name != ""){
		SearchTVShow(name, 1);
	}
}

function ButtonFindTVShow(){
	imdbid = $('#disctypesection').find('input[name="tvdbid"]').val()
	if (imdbid != ""){
		CallAJAXToModel('%%BASEURL%%scraper/ripper/findtvshow/' + imdbid + '/');
	}
}

function PopulateTVShow(id){
	$.ajax('%%BASEURL%%scraper/ripper/gettvshow/' + id + '/', {
		success: function(jsonitem) {
			var item = JSON.parse(jsonitem)
			if (item['success']){
				ClearModel();
				$('#disctypesection').find('input[name="name"]').val(item['response']['name']);
				$('#disctypesection').find('input[name="tvdbid"]').val(item['response']['external_ids']['tvdb_id']);
				$('#disctypesection').find('select[name="originallanguage"]').val(item['response']['original_language']);
				$('#disctypesection').find('input[name="moviedbid"]').val(item['response']['id']);
			}
		}
	})
}