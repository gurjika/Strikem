const socket = new WebSocket("ws://127.0.0.1:8000/ws/base/");

// Optional: handle WebSocket events
socket.onopen = () => {
    console.log("WebSocket is open");
};

socket.onmessage = (event) => {
    console.log("Message from server:", event.data);
};

// Export the WebSocket instance
export default socket;