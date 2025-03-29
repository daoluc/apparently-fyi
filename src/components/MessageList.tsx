"use client";

import { api } from "@/trpc/react";

export function MessageList() {
  const messagesQuery = api.getAllMessages.useQuery();

  if (messagesQuery.isPending) {
    return (
      <div className="flex justify-center py-8">
        <div className="text-center">
          <p className="text-gray-500">Loading messages...</p>
        </div>
      </div>
    );
  }

  if (messagesQuery.error) {
    return (
      <div className="flex justify-center py-8">
        <div className="text-center">
          <p className="text-red-500">Error loading messages. Please try again.</p>
        </div>
      </div>
    );
  }

  const messages = messagesQuery.data;

  if (messages.length === 0) {
    return (
      <div className="flex justify-center py-8">
        <div className="text-center">
          <p className="text-gray-500">No messages yet. Be the first to post!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-primary">
        Messages
      </h2>
      {messages.map((message) => (
        <div key={message.id} className="card">
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-bold text-lg">{message.title}</h3>
            <span className="text-xs text-gray-500">
              {new Date(message.createdAt).toLocaleString()}
            </span>
          </div>
          <p className="text-gray-700 whitespace-pre-wrap">{message.content}</p>
        </div>
      ))}
    </div>
  );
}
