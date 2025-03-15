import { io, Socket } from 'socket.io-client';

class WebSocketService {
    private socket: Socket | null = null;
    private static instance: WebSocketService;

    private constructor() {
        this.initializeSocket();
    }

    public static getInstance(): WebSocketService {
        if (!WebSocketService.instance) {
            WebSocketService.instance = new WebSocketService();
        }
        return WebSocketService.instance;
    }

    private initializeSocket() {
        this.socket = io('http://localhost:8000', {
            transports: ['polling', 'websocket'],
            autoConnect: true,
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000
        });

        this.socket.on('connect', () => {
            console.log('Connected to WebSocket server');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from WebSocket server');
        });

        this.socket.on('error', (error: Error) => {
            console.error('WebSocket error:', error);
        });
    }

    public sendMessage(message: string) {
        if (this.socket && this.socket.connected) {
            this.socket.emit('message', message);
        } else {
            console.error('Socket is not connected');
        }
    }

    public getSocket(): Socket | null {
        return this.socket;
    }

    public onMessage(callback: (message: any) => void) {
        if (this.socket) {
            this.socket.on('message', callback);
        }
    }

    public disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

export default WebSocketService.getInstance();