// client/src/api/backend.js
import axios from "axios";

const API_BASE = "http://localhost:8000"; // change to Vercel URL in prod

export async function fetchThreads(userId) {
  const res = await axios.get(`${API_BASE}/threads`, { params: { user_id: userId } });
  return res.data;
}

export async function fetchMessages(threadId) {
  const res = await axios.get(`${API_BASE}/messages`, { params: { thread_id: threadId } });
  return res.data;
}

export async function sendMessage({ userId, threadId, message }) {
  const res = await axios.post(`${API_BASE}/chat`, {
    user_id: userId,
    thread_id: threadId,
    message,
  });
  return res.data;
}

export async function createThread({ userId, threadId, title }) {
  const res = await axios.post(`${API_BASE}/threads`, {
    user_id: userId,
    thread_id: threadId,
    title,
  });
  return res.data;
}
