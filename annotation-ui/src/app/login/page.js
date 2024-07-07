// import { getCsrfToken } from "next-auth/client"
// "use client" // For some reason the csrf token doesn't work without client-side work, 
// see https://github.com/nextauthjs/next-auth/discussions/7256#discussioncomment-7269368
// and https://github.com/nextauthjs/next-auth/discussions/2573

import { getCsrfToken, getProviders } from "next-auth/react"
import { cookies } from 'next/headers';

export default async function SignIn(props) {
    const providers = await getProviders()

    const csrfToken = await getCsrfToken({
        req: {
            headers: {
                cookie: cookies().toString(),
            },
        },
    });

    // console.log("csrfToken", csrfToken)

    return (
        <form method="POST" action={providers.credentials.callbackUrl}>
            <input type="hidden" name="csrfToken" value={csrfToken} />

            <label>
                Email address
                <input type="text" id="username" name="username" />
            </label>
            <label>
                Password
                <input type="password" id="password" name="password" />
            </label>
            <button type="submit">Sign in with Email</button>
        </form>
    )
}

// // This is the recommended way for Next.js 9.3 or newer
// export async function getServerSideProps(context) {
//   const csrfToken = await getCsrfToken(context)
//   return {
//     props: { csrfToken },
//   }
// }
