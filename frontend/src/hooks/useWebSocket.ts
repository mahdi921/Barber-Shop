/**
 * WebSocket hook for chat functionality
 */
import { useState, useEffect, useCallback, useRef } from 'react';

interface WebSocketMessage {
    type: string;
    message: string;
    sender?: string;
    timestamp: string;
    status?: string;
    queue_position?: number;
}

export const useWebSocket = (sessionKey: string) => {
    const [messages, setMessages] = useState<WebSocketMessage[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const [status, setStatus] = useState<'bot' | 'queued' | 'admin' | 'closed'>('bot');
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!sessionKey) return;

        // WebSocket URL
        const wsUrl = `ws://${window.location.hostname}:8000/ws/chat/${sessionKey}/`;

        // Create WebSocket connection
        ws.current = new WebSocket(wsUrl);

        ws.current.onopen = () => {
            console.log('WebSocket connected');
            setIsConnected(true);
        };

        ws.current.onmessage = (event) => {
            const data: WebSocketMessage = JSON.parse(event.data);

            // Update status if provided
            if (data.status) {
                setStatus(data.status as any);
            }

            // Add message to list
            setMessages((prev) => [...prev, data]);
        };

        ws.current.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        ws.current.onclose = () => {
            console.log('WebSocket disconnected');
            setIsConnected(false);

            // Attempt reconnection after 3 seconds
            setTimeout(() => {
                if (sessionKey) {
                    window.location.reload(); // Simple reconnect strategy
                }
            }, 3000);
        };

        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, [sessionKey]);

    const sendMessage = useCallback((message: string) => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ message }));
        }
    }, []);

    return {
        messages,
        isConnected,
        status,
        sendMessage,
    };
};
