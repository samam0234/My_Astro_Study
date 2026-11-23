import { dispatch } from '../../lib/api.mjs';
import { getStore } from '../../lib/store.mjs';

export const prerender = false;
export const ALL = async context => dispatch(context, await getStore());
