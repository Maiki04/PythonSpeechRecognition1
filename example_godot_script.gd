extends Node3D

var http_request: HTTPRequest
var url: String = "http://127.0.0.1:5000/"
var get_text: String = "get_text"
var get_text_id: String = "get_text_id"
var text_id: int = -1


func _ready():
	http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.request_completed.connect(_on_request_completed)

	# Make an initial request to the Flask server
	make_request(get_text)

	var timer: Timer = Timer.new()
	timer.wait_time = 1.0
	timer.one_shot = false
	add_child(timer)
	timer.timeout.connect(func() -> void:
		make_request(get_text)
	)
	timer.start(timer.wait_time)


func make_request(endpoint: String):
	var full_url: String = url + endpoint
	var error := http_request.request(full_url)

	if error != OK:
		print("Request failed with error code: ", error)
	else:
		print("Request sent successfully to: ", full_url)


func _on_request_completed(_result, response_code, _headers, body):
	if response_code == 200:
		# Convert the body to a string and display it
		var response_body = body.get_string_from_utf8()
		if response_body.strip_edges() != "":
			print("Recognized text: ", response_body)
		else:
			print("No recognized text yet.")
	else:
		print("Request failed with response code: ", response_code)
