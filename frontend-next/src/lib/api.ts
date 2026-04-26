import ky, {HTTPError} from "ky";
import type {
  PageDetail,
  Paginated,
  SearchResult,
  Space,
  SpaceDetail,
  User,
} from "./types";

const SERVER_API_BASE =
  process.env.INTERNAL_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://127.0.0.1:8000";

const browser = ky.create({
  prefixUrl: "/api",
  credentials: "include",
  retry: 0,
  timeout: 15_000,
});

function server(cookieHeader?: string) {
  return ky.create({
    prefixUrl: `${SERVER_API_BASE}/api`,
    headers: cookieHeader ? {cookie: cookieHeader} : undefined,
    retry: 0,
    timeout: 15_000,
  });
}

export const api = {
  requestOtp: (email: string) =>
    browser.post("auth/otp/request", {json: {email}}).json<{detail: string}>(),
  verifyOtp: (email: string, code: string, display_name?: string) =>
    browser.post("auth/otp/verify", {json: {email, code, display_name}}).json<User>(),
  logout: () => browser.post("auth/logout"),
  me: () => browser.get("auth/me").json<User>(),

  listSpaces: () => browser.get("spaces/").json<Paginated<Space>>(),
  getSpace: (slug: string) => browser.get(`spaces/${slug}/`).json<SpaceDetail>(),
  createSpace: (data: {slug: string; name: string; description?: string}) =>
    browser.post("spaces/", {json: data}).json<Space>(),

  getPage: (id: number) => browser.get(`pages/${id}/`).json<PageDetail>(),
  createPage: (data: {space: number; parent?: number | null; title: string; body_md: string}) =>
    browser.post("pages/", {json: data}).json<PageDetail>(),
  updatePage: (id: number, data: Partial<PageDetail>) =>
    browser.patch(`pages/${id}/`, {json: data}).json<PageDetail>(),
  deletePage: (id: number) => browser.delete(`pages/${id}/`),
  movePage: (id: number, parent_id: number | null, position: number) =>
    browser.post(`pages/${id}/move`, {json: {parent_id, position}}).json<PageDetail>(),

  search: (q: string, space?: string) =>
    browser
      .get("search/", {searchParams: space ? {q, space} : {q}})
      .json<{results: SearchResult[]}>(),
};

export const ssrApi = {
  me: (cookieHeader?: string) => server(cookieHeader).get("auth/me").json<User>(),
  getSpace: (cookieHeader: string, slug: string) =>
    server(cookieHeader).get(`spaces/${slug}/`).json<SpaceDetail>(),
  listSpaces: (cookieHeader: string) =>
    server(cookieHeader).get("spaces/").json<Paginated<Space>>(),
  getPage: (cookieHeader: string, id: number) =>
    server(cookieHeader).get(`pages/${id}/`).json<PageDetail>(),
};

export {HTTPError};
