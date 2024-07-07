"use client"

import { signIn, signOut } from "next-auth/react"

export default function Component({ session }) {
    if (session) {
        return (
            <>
                Signed in as {session.user.email} <br />
                <pre>{JSON.stringify(session, null, 2)}</pre>
                <button onClick={() => signOut()}>Sign out</button>
            </>
        )
    }
    return (
        <>
            Not signed in <br />
            <button onClick={() => signIn()}>Sign in</button>
        </>
    )
}
