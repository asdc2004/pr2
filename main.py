from flask import Flask, render_template, request, Response
import cv2
import threading
import socket
import pickle

app = Flask(__name__)

# 클라이언트 목록을 저장할 리스트
clients = []

def video_stream():
    global clients
    while True:
        # 웹캠 대신 "video.mp4" 파일을 읽어옴
        frame = cv2.imread('video.mp4')
        data = pickle.dumps(frame)
        for client in clients:
            client.sendall(data)

# 클라이언트와의 소켓 통신을 처리하는 함수
def client_handler(client_socket):
    global clients
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            # 클라이언트로부터 채팅을 받아 모든 클라이언트에게 전달
            for client in clients:
                client.sendall(data)
        except Exception as e:
            print(e)
            break

@app.route('/')
def index():
    return render_template('ui.html')

@app.route('/video')
def video():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/chat', methods=['POST'])
def chat():
    message = request.form['message']
    # 받은 메시지를 모든 클라이언트에게 전달
    for client in clients:
        client.sendall(message.encode())
    return '', 204

if __name__ == '__main__':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8888))
    server_socket.listen(5)

    video_thread = threading.Thread(target=video_stream)
    video_thread.daemon = True
    video_thread.start()

    while True:
        client, addr = server_socket.accept()
        clients.append(client)

        client_thread = threading.Thread(target=client_handler, args=(client,))
        client_thread.daemon = True
        client_thread.start()
