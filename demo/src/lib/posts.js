import { getCollection } from 'astro:content';

export async function listPosts() {
  const posts = await getCollection('posts');
  return posts
    .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf())
    .map((post) => ({
      id: post.id,
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.pubDate.toISOString().slice(0, 10),
    }));
}
