"use client"

import { SessionProvider } from "next-auth/react";
import { signIn, signOut, useSession } from "next-auth/react"

const Component = (props) => {
    const { data: session, status } = useSession();
    if (status === "loading") return <p className="text-gray-500">Loading...</p>;

    if (session) {
        return (
            <>
                <p className="text-gray-700">Signed in as <span className="font-semibold">{session.user.email}</span></p>
                <button
                    className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition duration-300"
                    onClick={() => signOut()}
                >
                    Sign out
                </button>
            </>
        );
    }
    return (
        <>
            <p className="text-gray-700">Not signed in</p>
            <button
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition duration-300"
                onClick={() => signIn()}
            >
                Sign in
            </button>
        </>
    );
};

export default function AuthHeader({ session }) {
    return (
        <SessionProvider>
            <Component />
        </SessionProvider>
    )
}
