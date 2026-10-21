import { listPosts } from '../../lib/posts.js';

export async function GET() {
  return Response.json(await listPosts());
}
