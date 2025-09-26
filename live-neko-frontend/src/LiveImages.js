import React, { useEffect, useState } from 'react';
import { io } from 'socket.io-client';

const socket = io('http://localhost:5000');

export default function LiveImages() {
  const [images, setImages] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    socket.on('connect', () => {
      console.log('✅ Connected to Socket.IO server');
      setConnected(true);
    });

    socket.on('disconnect', () => {
      console.log('❌ Disconnected from Socket.IO server');
      setConnected(false);
    });

    socket.on('new_image', (data) => {
      console.log('📥 Received new image:', data);
      setImages((prev) => [data, ...prev].slice(0, 20)); // keep only last 20
    });

    return () => {
      socket.off('new_image');
      socket.off('connect');
      socket.off('disconnect');
    };
  }, []);

  return (
    <div style={{ textAlign: 'center' }}>
      <h1>Live Neko Images</h1>
      <p>Connection Status: {connected ? '🟢 Connected' : '🔴 Disconnected'}</p>
      <p>Images received: {images.length}</p>

      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
        {images.map((image, index) => (
          <div key={index} style={{ margin: '10px' }}>
            <img
              src={image.url}
              alt={image.category}
              style={{ maxWidth: '200px', borderRadius: '8px' }}
              onError={(e) => {
                console.log('⚠️ Failed to load image:', image.url);
                e.target.style.display = 'none';
              }}
              onLoad={() => console.log('✅ Image loaded:', image.url)}
            />
            <div>
              {image.category} {image.artist ? `- ${image.artist}` : ''}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
