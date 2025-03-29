"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import toast from "react-hot-toast";
import { api } from "@/trpc/react";

const messageSchema = z.object({
  title: z.string().min(1, { message: "Title is required" }),
  content: z.string().min(1, { message: "Content is required" }),
});

type MessageFormData = z.infer<typeof messageSchema>;

export function MessageForm() {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<MessageFormData>({
    resolver: zodResolver(messageSchema),
  });

  const createMessageMutation = api.createMessage.useMutation({
    onSuccess: () => {
      toast.success("Message posted successfully!");
      reset();
    },
    onError: () => {
      toast.error("Failed to post message. Please try again.");
    },
  });

  const onSubmit = (data: MessageFormData) => {
    createMessageMutation.mutate(data);
  };

  return (
    <div className="card mb-8">
      <h2 className="text-xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-primary">
        Post a Message
      </h2>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label
            htmlFor="title"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            Title
          </label>
          <input
            id="title"
            type="text"
            {...register("title")}
            className="input"
            placeholder="Enter a title for your message"
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
          )}
        </div>
        <div>
          <label
            htmlFor="content"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            Message
          </label>
          <textarea
            id="content"
            rows={4}
            {...register("content")}
            className="input"
            placeholder="What's on your mind?"
          />
          {errors.content && (
            <p className="mt-1 text-sm text-red-600">{errors.content.message}</p>
          )}
        </div>
        <button
          type="submit"
          disabled={createMessageMutation.isPending}
          className="btn-primary w-full"
        >
          {createMessageMutation.isPending ? "Posting..." : "Post Message"}
        </button>
      </form>
    </div>
  );
}
