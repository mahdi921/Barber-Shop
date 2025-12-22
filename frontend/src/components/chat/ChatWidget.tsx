import React, { useState, useEffect } from 'react';
import ChatButton from './ChatButton';
import ChatWindow from './ChatWindow';
import { useWebSocket } from '../../hooks/useWebSocket';

// Simple UUID generator
const generateUUID = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
};

const ChatWidget: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [sessionKey, setSessionKey] = useState<string>('');

    useEffect(() => {
        // Get or create session key
        let key = localStorage.getItem('chat_session_key');
        if (!key) {
            key = generateUUID();
            localStorage.setItem('chat_session_key', key);
        }
        setSessionKey(key);
    }, []);

    const { messages, isConnected, status, sendMessage } = useWebSocket(sessionKey);

    return (
        <>
            {!isOpen && <ChatButton onClick={() => setIsOpen(true)} />}
            {isOpen && (
                <ChatWindow
                    messages={messages}
                    onSend={sendMessage}
                    onClose={() => setIsOpen(false)}
                    status={status}
                    isConnected={isConnected}
                />
            )}
        </>
    );
};

export default ChatWidget;
