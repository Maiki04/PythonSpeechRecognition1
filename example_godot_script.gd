extends Node

const URL: String = "ws://127.0.0.1:5000/ws"
var socket: WebSocketPeer = WebSocketPeer.new()

var event: InputEventAction = InputEventAction.new()
var event_timer: Timer = Timer.new()
const EVENT_TIMER_WAIT_TIME: float = 0.06

var debug_timer: float = 0.0

var max_connection_retries: int = 3
var connection_retry_count: int = 0
var connection_timer: Timer = Timer.new()
const CONNECTION_RETRY_WAIT_TIME: float = 2.0


func _notification(what: int) -> void:
	match what:
		NOTIFICATION_PREDELETE:
			event_timer.queue_free(); connection_timer.queue_free()


func _ready():
	event_timer.one_shot = true
	add_child(event_timer, false, Node.INTERNAL_MODE_FRONT)
	connection_timer.one_shot = true
	add_child(connection_timer, false, Node.INTERNAL_MODE_FRONT)

	var err: Error = socket.connect_to_url(URL)
	if err == OK:
		print("WebSocket connection attempt initiated.")
	else:
		print("WebSocket connection error: ", err)
		_retry_connection()


func _retry_connection():
	if connection_retry_count < max_connection_retries:
		connection_retry_count += 1
		print("Retrying connection... Attempt ", connection_retry_count)

		connection_timer.start(CONNECTION_RETRY_WAIT_TIME)
		await connection_timer.timeout

		socket.connect_to_url(URL)

	else:
		print("Failed to connect after ", max_connection_retries, " attempts.")


func _physics_process(delta):
	# WebSocket-Polling
	socket.poll()
	var state: WebSocketPeer.State = socket.get_ready_state()

	if state == WebSocketPeer.STATE_OPEN:
		while socket.get_available_packet_count():
			var packet: PackedByteArray = socket.get_packet()
			#var is_packet_empty: bool = packet.is_empty()

			# Convert the paket to String.
			var data_string: String = packet.get_string_from_utf8()

			print(packet)
			print("Received: ", data_string)

			await _process_content(data_string)

	elif state == WebSocketPeer.STATE_CLOSING:
		print("Connection is being closed...")

	elif state == WebSocketPeer.STATE_CLOSED:
		var code: int = socket.get_close_code()
		print("WebSocket closed with code: %d, Reason: %s. Clean: %s" % [code, socket.get_close_reason(), code != -1])
		process_mode = ProcessMode.PROCESS_MODE_DISABLED # End the script.

	# Debug-Timer
	debug_timer += delta
	if debug_timer >= 2.0:  # Print the status every 2 seconds.
		print("Connection status: ", _get_state_name(state))
		debug_timer = 0.0


# Helper function to output the state in a readable format.
func _get_state_name(state: int) -> String:
	match state:
		WebSocketPeer.STATE_CONNECTING: return "CONNECTING"
		WebSocketPeer.STATE_OPEN:       return "OPEN"
		WebSocketPeer.STATE_CLOSING:    return "CLOSING"
		WebSocketPeer.STATE_CLOSED:     return "CLOSED"
		_: return "UNKNOWN"


func _process_content(data_string: String) -> void:
	# Simulated is_action_just_pressed behaviour on a custom input action.
	match data_string:
		"r": event.action = "move_right"
		"l": event.action = "move_left"
		"j": event.action = "jump"
		"d": event.action = "dodge"
		_:
			return

	event.pressed = true
	Input.parse_input_event(event)

	event_timer.start(EVENT_TIMER_WAIT_TIME)
	await event_timer.timeout

	event.pressed = false
	Input.parse_input_event(event)
