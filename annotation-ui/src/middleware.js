import { NextResponse, userAgent } from 'next/server';
import { getSession } from 'next-auth/react';
export { default } from "next-auth/middleware"

// // See "Matching Paths" below to learn more
export const config = {
  matcher: ['/'],
}

// https://github.com/vercel/next.js/discussions/62261
async function loggingMiddleware(
  request,
  event,
) {
  // const response = NextResponse.next();
  const { pathname, searchParams } = request.nextUrl;

  if (pathname.startsWith("/_next")) {
    return NextResponse.next();
  }

  const agent = userAgent(request);
  // const session = await getSession(request, response); // In case user information is in the session
  const log = {
    level: "info",
    ip: request.ip ?? request.headers.get("x-forwarded-for") ?? "",
    method: request.method,
    pathname: pathname,
    search_params: Object.fromEntries(searchParams),
    browser: agent.browser,
    device: agent.device,
    "user-agent": request.headers.get("user-agent"),
    "x-amzn-trace-id": request.headers.get("x-amzn-trace-id"),
  };
  // if (session) {
  //   log.user = {
  //     app: session.user.app,
  //     sid: session.user.sid,
  //     sub: session.user.sub,
  //     email: session.user.email,
  //     name: session.user.name,
  //   };
  // }
  console.log(JSON.stringify(log));
  return NextResponse.next()
  // return response;
};